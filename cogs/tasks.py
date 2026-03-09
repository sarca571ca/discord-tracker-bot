import asyncio

import discord
from discord.ext import commands, tasks

from src import channelutil, hnmutil, settings, stringutil, timeutil

#variable for logging helper
log_print = stringutil.StringUtil.log_print


class SendHourWarning(commands.Cog):
    #checks the HNM timers channel and sends an @everyone warning in the camp pings channel when an HNM is between 1 hour before and 1 hour after its scheduled timestamp.

    def __init__(self, bot) -> None:
        # Store bot reference for later access
        self.bot = bot
        # Start the background task when the cog is loaded
        self.send_hour_warning.start()
       

    def cog_unload(self):
        #stop the background task
        self.send_hour_warning.cancel()

    @tasks.loop(seconds=60)
    #HNM timer message, check if we are in the warning window. then send an @everyone ping.
    async def send_hour_warning(self):
        hnm_timers_channel = self.bot.get_channel(settings.HNMTIMES)
        camp_pings_channel = self.bot.get_channel(settings.CAMPPINGS)
        # If either channel is missing, do nothing 
        if hnm_timers_channel is None or camp_pings_channel is None:
            return

        # Current time in in channelk's timezone
        now = timeutil.Time.now()

        try:
            #Iterate over messages oldest first
            async for message in hnm_timers_channel.history(
                limit=None,
                oldest_first=True, 
            ):
                #process messages that follow the "- " timer format.
                if not message.content.startswith("- "):
                    continue

            await self._process_timer_message(message, now, camp_pings_channel)
              
#handles 503 errors by waiting 60 seconds and retrying, handles other discord server errors by logging them, and logs any other exceptions that occur during the task.
        except discord.errors.DiscordServerError as e:
             if e.code == 0 and e.status == 503:
                        msg = log_print("SendHourWarning: Service Unavailable. Retrying in 60 seconds...")
                        await channelutil.LogPrint.print(self.bot, msg)
                        await asyncio.sleep(60)
                        self.send_hour_warning.restart()
             else:
                        msg = log_print(f"SendHourWarning: DiscordServerError -> {e}")
                        await channelutil.LogPrint.print(self.bot, msg)
        except Exception as e:
            msg = log_print(f"SendHourWarning: Error -> {e}")
            await channelutil.LogPrint.print(self.bot, msg)

    async def _process_timer_message(
        self, message: discord.Message,now: int,camp_pings_channel: discord.TextChannel)-> None:
        #Processes a single timer message, checks if it's within the warning window, and sends an @everyone ping if necessary.
        Timestamp, dt = timeutil.Time.strip_timestamp(message) # Extract timestamp and ignore the returned datetime object
        warning_msg = message.content.replace("- ", "", 1) # Remove the "- " prefix for the user‑facing warning content.
       # Define the window: 1 hour before to 1 hour after the camp time.
        hour_warn_time = timestamp - (60 * 60)
        camp_end_time = timestamp + (60 * 60)

        if not(hour_warn_time <= now <= camp_end_time):
                return
# Avoid spamming: only send if a matching warning is not already present.
        already_sent= await self._check_already_sent(camp_pings_channel, warning_msg)
        if not already_sent:
                await camp_pings_channel.send(f"@everyone {warning_msg}")
                
        async def _warning_already_sent(self, camp_pings_channel: discord.TextChannel, warning_msg: str) -> bool:#checks messages in the camp pings to see if the warning has already been sent, returns True if found, False otherwise.
         async for msg in camp_pings_channel.history(limit=100, oldest_first=False):
             if warning_msg == msg.content.replace("@everyone ", "", 1):# Compare the warning message to the content of the message in the camp pings channel, ignoring the @everyone prefix.
                 return True
             return False   
         
class CreateChannelTasks(commands.Cog):

    # This cog handles the creation of HNM attendance channels based on the schedule posted in the HNM timers channel. It runs every 60 seconds, checks the schedule, and creates channels as needed. It also handles potential Discord server errors gracefully by retrying after a delay.
    def __init__(self, bot) -> None:
        self.create_channel_task.start()
        self.bot = bot
        

    def cog_unload(self) -> None:
        # Stop the background task when the cog is unloaded
        self.create_channel_task.cancel()

    @tasks.loop(seconds=60)
    async def create_channel_task(self):
        # Check the HNM timers channel and create attendance channels as needed
        guild = self.bot.get_guild(settings.GUILDID)
        if guild is None:
            return

        category = discord.utils.get(guild.categories, id=settings.HNMCATEGORYID)
        hnm_times_channel = self.bot.get_channel(settings.HNMTIMES)

        if category is None:
            msg = log_print(
                "HNM Attendance: Catergory either not set properly in settings or doesn't exist."
            )
            await channelutil.LogPrint.print(self.bot, msg)
            return

        if hnm_times_channel is None:
            return

        now = timeutil.Time.now()  # Current time in the bot's timezone
        target_time = timeutil.Time.format_time(now)

        try:
            async for message in hnm_times_channel.history(
                limit=None, oldest_first=True):# Iterate through the message history of the HNM timers channel, starting with the oldest messages first. This allows the bot to process scheduled HNMs in chronological order and create channels for upcoming events as needed.
                if message.content.startswith("- "):
                    continue


# Extract the day
                day_start = message.content.find("(")
                day_end = message.content.find(")")
                if day_start != -1 and day_end != -1:
                    raw_day = message.content[day_start + 1 : day_end].strip()
                    day = stringutil.StringUtil.remove_formating(raw_day)
                else:
                    day = None
# Handle special cases for certain HNMs 
                special_hnms = {
                        "King Arthro": "ka",
                        "King Vinegarroon": "kv",
                        "Bloodsucker": "bs",
                    }

                channel_name: str = None
                for key, short in special_hnms.items():
                    if key in message.content:
                        channel_name = short
                        break
                        # If the message doesn't match any special cases, attempt to extract the channel name based on the day and message format. 
                        # For early days (1-3), it may be in a different position than for later days (4+), so we check both possibilities.
                    if channel_name is None:
                        if day == None or int(day) <= 3:
                            channel_name = message.content[2:5].strip()
                        elif int(day) >= 4:
                            nq = message.content[4:7].strip()
                            channel_name = f"{nq}"

                    timestamp, dt = timeutil.Time.strip_timestamp(message)  # dt, utc = calculate_time_diff(message.content) # Extracts the utc timestamp
                    dt_pst = dt.astimezone(timeutil.Time.bot_tz())
                    date = dt_pst.strftime("%b%d").lower()
                    hnm = channel_name.upper()
                    hnm_name = message.content.replace("- ", "", 1)# Full HNM name without the "- " prefix.
                    unix_target = int(dt.timestamp())# Unix timestamp and difference from 'now', for window logic.
                    time_diff = now - unix_target

                    hnm_time = timeutil.Time.format_time(
                        timestamp - (settings.MAKECHANNEL * 60)
                    )
                    # Determine the end of the HNM window based on the type of HNM. For certain HNMs (like Jormungand, Vritra, Tiamat), 
                    # the window is 24 hours, while for others it's 1 hour. 
                    if any(
                        keyword in channel_name.lower()
                        for keyword in ["jor", "vrt", "tia"]
                    ):
                        hnm_window_end = timeutil.Time.format_time(
                            timestamp + (24 * 3600)
                        )  # 24 hours for GW
                    else:
                        hnm_window_end = timeutil.Time.format_time(
                            timestamp + (1 * 3600)
                        )  # 1 hour for everything else
#Delegate actual channel management to your HandleHNM helper.
                    await hnmutil.HandleHNM.process_hnm_window(
                        hnm_window_end,
                        target_time,
                        hnm,
                        hnm_time,
                        date,
                        day,
                        message,
                        guild,
                        category,
                        timestamp,
                        hnm_times_channel,
                        hnm_name,
                        time_diff,
                    )
                pass
        except discord.errors.DiscordServerError as e:
            if e.code == 0 and e.status == 503:
                msg = log_print("CreateChannelTask: Service Unavailable error. Retrying in 60 seconds...")
                await channelutil.LogPrint.print(self.bot, msg)
                await asyncio.sleep(60)
                CreateChannelTasks.create_channel_task.restart()
            else:
                msg = log_print(f"CreateChannelTask: DiscordServerError -> {e}")
                await channelutil.LogPrint.print(self.bot, msg)
        except Exception as e:
            msg = log_print(f"CreateChannelTask: Error -> {e}")
            await channelutil.LogPrint.print(self.bot, msg)


class DeleteOldChannels(commands.Cog): #Once every 24 hours, scans the archive category and deletes text channels older than the configured ARCHIVEWAIT age.

    def __init__(self, bot) -> None:
        #Store bot reference and start scheduled cleanup.
        self.bot = bot
        self.delete_old_channels.start()
        

    def cog_unload(self) -> None:
        #Stop the scheduled cleanup when the cog is unloaded to prevent it from running after the cog is removed.
        self.delete_old_channels.cancel()

    @tasks.loop(hours=24)
    #Scans the archive category and deletes text channels older than the configured ARCHIVEWAIT age. This helps keep the server organized by removing old attendance channels that are no longer needed.
    async def delete_old_channels(self):
        try:
            archive_category = discord.utils.get(self.bot.guilds[0].categories, name=settings.ATTENDARCHID)
            if archive_category is None:
                msg = log_print( "DeleteOldChannels: Archive category not found; nothing to delete.")
                await channelutil.LogPrint.print(self.bot, msg) 
                return
            # For each text channel in the archive category, check its age.
            for channel in archive_category.channels:
                if not isinstance(channel, discord.TextChannel):
                        continue
                    # Compute channel age in whole days using time utility.
                age_days =(timeutil.Time.discord_tz() - channel.created_at).days

                if age_days>= settings.ARCHIVEWAIT:
                        await channelutil.Manager.archive_channels(
                                archive_category,
                                channel,
                                archive_category,
                                option="delete",)

            pass
        except discord.errors.DiscordServerError as e:
            if e.code == 0 and e.status == 503:
                msg = log_print("Service Unavailable error. Retrying in 60 seconds...")
                await channelutil.LogPrint.print(self.bot, msg)
                await asyncio.sleep(60)
                self.delete_old_channels.restart()
            else:
                msg = log_print(f"DeleteOldChannels: DiscordServerError -> {e}")
                await channelutil.LogPrint.print(self.bot, msg)
        except Exception as e:
            msg = log_print(f"DeleteOldChannels: Error -> {e}")
            await channelutil.LogPrint.print(self.bot, msg)

# The setup function is called when the cog is loaded, and it adds each of the task cogs to the bot. It also logs a message indicating that all tasks have been loaded and that the bot is online.
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SendHourWarning(bot))
    await bot.add_cog(CreateChannelTasks(bot))
    await bot.add_cog(DeleteOldChannels(bot))
    msg = log_print("All tasks loaded. Alise is online.")
    await channelutil.LogPrint.print(bot, msg)

