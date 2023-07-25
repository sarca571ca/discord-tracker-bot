import discord
import pytz
import asyncio

from datetime import datetime, timedelta

from string_utils import load_settings, get_utc_timestamp, calculate_time_diff, log_print
from channel_utils import start_channel_tasks, restart_channel_tasks

# Settings
ss = load_settings()
hnm_times =  ss['hnm_times']                   # Replace with the HNM TIMES channel ID
bot_commands = ss['bot_commands']              # Replace with bot-commands channel ID
dkp_review_category_name = "DKP REVIEW"
hnm_att_category_name = "HNM ATTENDANCE"
att_arch_category_name = "ATTENDANCE ARCHIVE"
time_zone = pytz.timezone('America/Los_Angeles')

async def handle_hnm_command(ctx, hnm, hq, day: int, timestamp, channel, bot_channel, bot):
    original_hnm = hnm  # Store the original HNM name

    if hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
        hnm = "GroundKings"
    if hnm in ["Jormungand", "Tiamat", "Vrtra"]:
        hnm = "GrandWyrm"
    try:
        day = int(day) + 1
    except (ValueError, OverflowError):
        log_print("Handle HNM: Day was not provided.")
        await ctx.author.send(f"No day provided for {original_hnm}.\nUse the !help command for a list of commands and how to use them.\n Then resend your command in  {bot_channel.mention}")
        return

    try:
        date_formats = [ # List of accepted date formats
            "%Y-%m-%d %I%M%S %p", "%Y%m%d %I%M%S %p", "%y%m%d %I%M%S %p", "%m%d%Y %I%M%S %p", "%m%d%Y %I%M%S %p",
            "%Y-%m-%d %I:%M:%S %p", "%Y%m%d %I:%M:%S %p", "%y%m%d %I:%M:%S %p", "%m%d%Y %I:%M:%S %p", "%m%d%Y %I:%M:%S %p",
            "%Y-%m-%d %H%M%S", "%Y%m%d %H%M%S", "%y%m%d %H%M%S", "%m%d%Y %H%M%S", "%m%d%Y %H%M%S",
            "%Y-%m-%d %H:%M:%S", "%Y%m%d %H:%M:%S", "%y%m%d %H:%M:%S", "%m%d%Y %H:%M:%S", "%m%d%Y %H:%M:%S",
            "%Y-%m-%d %h%M%S", "%Y%m%d %h%M%S", "%y%m%d %h%M%S", "%m%d%Y %h%M%S", "%m%d%Y %h%M%S",
            "%Y-%m-%d %h:%M:%S", "%Y%m%d %h:%M:%S", "%y%m%d %h:%M:%S", "%m%d%Y %h:%M:%S", "%m%d%Y %h:%M:%S"
        ]
        time_formats = [
            "%I%M%S %p", "%I:%M:%S %p", "%H%M%S", "%H:%M:%S", "%h:%M:%S"
        ]

        # Current date
        current_datetime = datetime.now(time_zone)
        current_date = current_datetime.date()

        # Check if the provided timestamp matches any of the accepted formats
        valid_format = False
        parsed_datetime = None
        for date_format in date_formats:
            try: # Try parsing the timestamp with the current format
                parsed_datetime = time_zone.localize(datetime.strptime(timestamp, date_format))
                valid_format = True
                break
            except ValueError:
                pass

        # If the timestamp does not match any accepted formats, try parsing with the '%H%M%S' format
        if not valid_format:
            for time_format in time_formats:
                try: # Try parsing the timestamp with the current format
                    parsed_time = datetime.strptime(timestamp, time_format).time()
                    parsed_datetime = time_zone.localize(datetime.combine(current_date, parsed_time))
                    valid_format = True
                    break
                except ValueError:
                    pass

        if valid_format:
            if parsed_datetime > datetime.now(time_zone): # Check if the parsed datetime is in the future
                current_date -= timedelta(days=1) # Subtract one day from the current date
            if "GrandWyrm" not in hnm:
                parsed_datetime = time_zone.localize(datetime.combine(current_date, parsed_datetime.time()))

            unix_timestamp = int(parsed_datetime.timestamp())

    except (ValueError, OverflowError, UnboundLocalError):
        if timestamp == None:
            await ctx.author.send(f"No date/time provided for {original_hnm}.\nUse the !help command for a list of commands and how to use them.\n Then resend your command in  {bot_channel.mention}")
            log_print("Handle HNM: No timestamp provided.")
        else:
            await ctx.author.send(f"Incorrect time format for {original_hnm}.\nUse the !help command for a list of commands and how to use them.\n Then resend your command in  {bot_channel.mention}")
            log_print("Handle HNM: Incorrect timestamp format was provided.")
        return

    try:
        if original_hnm in ["Fafnir", "Adamantoise", "Behemoth", "King Arthro", "Simurgh"]:
            unix_timestamp += (22 * 3600)  # Add 22 hours for GroundKings and KA
        elif original_hnm in ["Jormungand", "Tiamat", "Vrtra"]:
            unix_timestamp += (84 * 3600)  # Add 84 hours for GrandWyrms and KA
        else:
            unix_timestamp += (21 * 3600)  # Add 21 hours for other HNMs
    except (UnboundLocalError):
        log_print("Handle HNM: No timestamp provided.")
        return
    except (ValueError, OverflowError):
        log_print("Handle HNM: HNM provided does not exist.")
        return

    async for message in channel.history(limit=None):
        if message.author == bot and message.content.startswith(f"- {original_hnm}"):
            await message.delete()


    if unix_timestamp:
        if original_hnm not in ["Fafnir", "Adamantoise", "Behemoth"]:
            await channel.send(f"- {original_hnm}: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
        else:
            if int(day) >= 4: # Possible HQ or NQ day 4+
                await channel.send(f"- {original_hnm}/{hq} (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            else: # NQ only
                await channel.send(f"- {original_hnm} (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
    else:
        await channel.send(f"- {original_hnm}")

    await sort_hnm_times_channel(channel, bot)

async def sort_hnm_times_channel(channel, bot):
    messages = []

    async for message in channel.history(limit=None):
        if message.author == bot:
            messages.append(message)

    messages.sort(key=lambda m: get_utc_timestamp(m))

    for message in messages:
        content = message.content
        await message.delete()
        await channel.send(content)

def get_channels(bot, ctx):
    allowed_channel_id = bot_commands
    author = ctx.author
    channel_id = hnm_times

    if ctx.channel.id != allowed_channel_id:
        asyncio.create_task(author.send("This command can only be used in the specified channel."))
        asyncio.create_task(ctx.message.delete())
        return None, None

    channel = bot.get_channel(channel_id)
    bot_channel = bot.get_channel(bot_commands)

    return channel, bot_channel

async def process_hnm_window(hnm_window_end, target_time, hnm, hnm_time, date,
                             day, message, guild, category, utc, hnm_times_channel,
                             hnm_name, time_diff):
    if hnm_window_end >= target_time:
        if hnm_time <= target_time:
            if any(keyword in message.content for keyword in ["Fafnir", "Adamantoise", "Behemoth"]):
                channel_name = f"{date}-{hnm}{day}".lower()
            else:
                channel_name = f"{date}-{hnm}".lower()

            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            if existing_channel:
                async for message in existing_channel.history(limit=1, oldest_first=True):
                    if message.content.startswith("- "):
                        channel_dt, channel_utc = calculate_time_diff(message.content)
                if channel_utc == utc and category != hnm_att_category_name:
                    return
                elif channel_utc == utc and category == hnm_att_category_name:
                    await asyncio.sleep(5)
                    for task in asyncio.all_tasks():
                        if task.get_name() == f"wm-{channel_name}":
                            break
                    else:
                        await restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel)
                else:
                    channel_name = f"{channel_name}1"
                    existing_channel = discord.utils.get(guild.channels, name=channel_name)
                    if existing_channel:
                        await restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel)
                    else:
                        await start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)
            else:
                await start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)