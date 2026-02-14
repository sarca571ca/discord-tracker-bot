import asyncio

import discord
from discord.ext import commands, tasks

from src import channelutil, hnmutil, settings, stringutil, timeutil

log_print = stringutil.StringUtil.log_print


class SendHourWarning(commands.Cog):

    def __init__(self, bot) -> None:
        self.send_hour_warning.start()
        self.bot = bot

    def cog_unload(self) -> tasks.Coroutine[tasks.Any, tasks.Any, None]:
        self.send_hour_warning.cancel()

    #!! This whole task is janky with if statements ; ;
    @tasks.loop(seconds=60)
    async def send_hour_warning(self):
        hnm_timers_channel = self.bot.get_channel(settings.HNMTIMES)
        camp_pings_channel = self.bot.get_channel(settings.CAMPPINGS)
        now = timeutil.Time.now()
        try:
            async for message in hnm_timers_channel.history(
                limit=None, oldest_first=True
            ):
                if message.content.startswith("- "):
                    timestamp, dt = timeutil.Time.strip_timestamp(message)
                    warning_msg = message.content.replace("- ", "", 1)
                    hour_warn_time = timestamp - (60 * 60)
                    camp_end_time = timestamp + (60 * 60)

                    if camp_end_time >= now and hour_warn_time <= now:
                        if camp_pings_channel:
                            last_message = [
                                msg async for msg in camp_pings_channel.history(limit=1)
                            ]

                            if last_message:
                                message_sent = False

                                async for msg in camp_pings_channel.history(
                                    limit=100, oldest_first=False
                                ):
                                    if warning_msg == msg.content.replace(
                                        "@everyone ", "", 1
                                    ):
                                        message_sent = True
                                        break

                                if not message_sent:
                                    await camp_pings_channel.send(
                                        f"@everyone {warning_msg}"
                                    )
                            else:
                                await camp_pings_channel.send(
                                    f"@everyone {warning_msg}"
                                )
                pass
        except discord.errors.DiscordServerError as e:
            if e.code == 0 and e.status == 503:
                msg = log_print(
                    "SendHourWarning: Service Unavailable error. Retrying in 60 seconds..."
                )
                await channelutil.LogPrint.print(self.bot, msg)
                await asyncio.sleep(60)
                SendHourWarning.send_hour_warning.restart()
            else:
                msg = log_print(f"SendHourWarning: DiscordServerError -> {e}")
                await channelutil.LogPrint.print(self.bot, msg)
        except Exception as e:
            msg = log_print(f"SendHourWarning: Error -> {e}")
            await channelutil.LogPrint.print(self.bot, msg)


class CreateChannelTasks(commands.Cog):

    def __init__(self, bot) -> None:
        self.create_channel_task.start()
        self.bot = bot

    def cog_unload(self) -> tasks.Coroutine[tasks.Any, tasks.Any, None]:
        self.send_hour_warning.cancel()

    @tasks.loop(seconds=60)
    async def create_channel_task(self):
        guild = self.bot.get_guild(settings.GUILDID)
        category = discord.utils.get(guild.categories, id=settings.HNMCATEGORYID)
        hnm_times_channel = self.bot.get_channel(settings.HNMTIMES)

        if not category:
            msg = log_print(
                "HNM Attendance: Catergory either not set properly in settings or doesn't exist."
            )
            await channelutil.LogPrint.print(self.bot, msg)

        now = timeutil.Time.now()
        target_time = timeutil.Time.format_time(now)
        try:
            async for message in hnm_times_channel.history(
                limit=None, oldest_first=True
            ):
                if message.content.startswith("- "):

                    # Extract the day
                    day_start = message.content.find("(")
                    day_end = message.content.find(")")
                    if day_start != -1 and day_end != -1:
                        raw_day = message.content[day_start + 1 : day_end].strip()
                        day = stringutil.StringUtil.remove_formating(raw_day)
                    else:
                        day = None

                    if "King Arthro" in message.content:
                        channel_name = "ka"
                    elif "King Vinegarroon" in message.content:
                        channel_name = "kv"
                    elif "Bloodsucker" in message.content:
                        channel_name = "bs"
                    else:
                        if day == None or int(day) <= 3:
                            channel_name = message.content[2:5].strip()
                        elif int(day) >= 4:
                            nq = message.content[4:7].strip()
                            channel_name = f"{nq}"

                    timestamp, dt = timeutil.Time.strip_timestamp(
                        message
                    )  # dt, utc = calculate_time_diff(message.content) # Extracts the utc timestamp
                    dt_pst = dt.astimezone(timeutil.Time.bot_tz())
                    date = dt_pst.strftime("%b%d").lower()
                    hnm = channel_name.upper()
                    hnm_name = message.content.replace("- ", "", 1)
                    unix_target = int(dt.timestamp())
                    time_diff = now - unix_target

                    hnm_time = timeutil.Time.format_time(
                        timestamp - (settings.MAKECHANNEL * 60)
                    )
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
                msg = log_print(
                    "CreateChannelTask: Service Unavailable error. Retrying in 60 seconds..."
                )
                await channelutil.LogPrint.print(self.bot, msg)
                await asyncio.sleep(60)
                CreateChannelTasks.create_channel_task.restart()
            else:
                msg = log_print(f"CreateChannelTask: DiscordServerError -> {e}")
                await channelutil.LogPrint.print(self.bot, msg)
        except Exception as e:
            msg = log_print(f"CreateChannelTask: Error -> {e}")
            await channelutil.LogPrint.print(self.bot, msg)


class DeleteOldChannels(commands.Cog):

    def __init__(self, bot) -> None:
        self.delete_old_channels.start()
        self.bot = bot

    def cog_unload(self) -> tasks.Coroutine[tasks.Any, tasks.Any, None]:
        self.send_hour_warning.cancel()

    @tasks.loop(hours=24)
    async def delete_old_channels(self):
        try:
            archive_category = discord.utils.get(
                self.bot.guilds[0].categories, name=settings.ATTENDARCHID
            )
            if archive_category:
                for channel in archive_category.channels:
                    if isinstance(channel, discord.TextChannel):
                        if (
                            timeutil.Time.discord_tz() - channel.created_at
                        ).days >= settings.ARCHIVEWAIT:
                            await channelutil.Manager.archive_channels(
                                archive_category,
                                channel,
                                archive_category,
                                option="delete",
                            )
            pass
        except discord.errors.DiscordServerError as e:
            if e.code == 0 and e.status == 503:
                msg = log_print("Service Unavailable error. Retrying in 60 seconds...")
                await channelutil.LogPrint.print(self.bot, msg)
                await asyncio.sleep(60)
                DeleteOldChannels.delete_old_channels.restart()
            else:
                msg = log_print(f"DiscordServerError: {e}")
                await channelutil.LogPrint.print(self.bot, msg)
        except Exception as e:
            msg = log_print(f"Error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(SendHourWarning(bot))
    await bot.add_cog(CreateChannelTasks(bot))
    await bot.add_cog(DeleteOldChannels(bot))
    msg = log_print("All tasks loaded. Alise is online.")
    await channelutil.LogPrint.print(bot, msg)

