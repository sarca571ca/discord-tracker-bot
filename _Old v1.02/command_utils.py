import discord
import pytz
import asyncio
import aiofiles
import os
import pandas as pd

from datetime import datetime, timedelta

from string_utils import load_settings, get_utc_timestamp, calculate_time_diff, log_print
from channel_utils import start_channel_tasks, restart_channel_tasks

# Settings
ss = load_settings()
hnm_times =  ss['hnm_times']
bnm_times = ss['bnm_times']
bot_commands = ss['bot_commands']
dkp_review_category_name = ss['dkp_review_category_name']
hnm_att_category_name = ss['hnm_att_category_name']
att_arch_category_name = ss['att_arch_category_name']
time_zone = pytz.timezone(ss['time_zone'])

async def handle_hnm_command(ctx, hnm, hq, day: int, mod: str, timestamp, channel, bot_channel, bot):
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
        if message.author == bot and message.content.startswith(f"- {original_hnm}") or message.content.startswith(f"- **{original_hnm}"):
            await message.delete()


    if unix_timestamp:
        if original_hnm not in ["Fafnir", "Adamantoise", "Behemoth"] and mod == 'n':
            if original_hnm == "King Arthro":
                await channel.send(f"- {original_hnm} :crab:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "King Vinegarroon":
                await channel.send(f"- {original_hnm} :scorpion:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Shikigami Weapon":
                await channel.send(f"- {original_hnm} :japanese_ogre:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Simurgh":
                await channel.send(f"- {original_hnm} :bird:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Jormungand":
                await channel.send(f"- {original_hnm} :ice_cube::chicken::ice_cube:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Tiamat":
                await channel.send(f"- {original_hnm} :fire::chicken::fire:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            else:
                await channel.send(f"- {original_hnm}: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
        elif original_hnm not in ["Fafnir", "Adamantoise", "Behemoth"] and mod == 'a':
            if original_hnm == "King Arthro":
                await channel.send(f"- {original_hnm} :grey_question::crab::grey_question:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "King Vinegarroon":
                await channel.send(f"- {original_hnm} :grey_question::scorpion::grey_question:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Shikigami Weapon":
                await channel.send(f"- {original_hnm} :grey_question::japanese_ogre::grey_question:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Simurgh":
                await channel.send(f"- {original_hnm} :grey_question::bird::grey_question:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Jormungand":
                await channel.send(f"- {original_hnm} :grey_question::ice_cube::chicken::ice_cube::grey_question:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif original_hnm == "Tiamat":
                await channel.send(f"- {original_hnm} :grey_question::fire::chicken::fire::grey_question:: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            else:
                await channel.send(f"- {original_hnm}: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
        else:
            if int(day) >= 4 and mod == "n": # Possible HQ or NQ day 4+
                await channel.send(f"- **{original_hnm}/{hq}** 🚨 (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif int(day) >= 4 and mod == "d":
                await channel.send(f"- **{original_hnm}/{hq}** :moneybag:🚨:moneybag: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif int(day) >= 4 and mod == "t":
                await channel.send(f"- **{original_hnm}/{hq}** :moneybag::moneybag:🚨:moneybag::moneybag: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            else: # NQ only
                if original_hnm == "Behemoth":
                    if mod == "a":
                        await channel.send(f"- {original_hnm} :grey_question::zap::grey_question: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    elif mod == "d":
                        await channel.send(f"- {original_hnm} :moneybag::zap::moneybag: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    elif mod == "t":
                        await channel.send(f"- {original_hnm} :gem::zap::gem: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    else:
                        await channel.send(f"- {original_hnm} :zap: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                elif original_hnm == "Adamantoise":
                    if mod == "a":
                        await channel.send(f"- {original_hnm} :grey_question::turtle::grey_question: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    elif mod == "d":
                        await channel.send(f"- {original_hnm} :moneybag::turtle::moneybag: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    elif mod == "t":
                        await channel.send(f"- {original_hnm} :gem::turtle::gem: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    else:
                        await channel.send(f"- {original_hnm} :turtle: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                elif original_hnm == "Fafnir":
                    if mod == "a":
                        await channel.send(f"- {original_hnm} :grey_question::dragon_face::grey_question: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    elif mod == "d":
                        await channel.send(f"- {original_hnm} :moneybag::dragon_face::moneybag: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    elif mod == "t":
                        await channel.send(f"- {original_hnm} :gem::dragon_face::gem: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                    else:
                        await channel.send(f"- {original_hnm} :dragon_face: (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
                else:
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
        dt, utc = calculate_time_diff(content)
        unix_now = int(datetime.now().timestamp())
        unix_target = int(dt.timestamp())
        time_diff = unix_now - unix_target
        if any(keyword in message.content for keyword in ['Jormungand', 'Tiamat', 'Vrtra']) and time_diff > 86400 * 3:
            continue
        elif not any(keyword in message.content for keyword in ['Jormungand', 'Tiamat', 'Vrtra']) and time_diff > 86400:
            continue
        else:
            await channel.send(content)

def get_channels(bot, ctx):
    allowed_channel_id = bot_commands
    author = ctx.author
    hnm_channel_id = hnm_times

    if ctx.channel.id != allowed_channel_id:
        asyncio.create_task(author.send("This command can only be used in the specified channel."))
        asyncio.create_task(ctx.message.delete())
        return None, None

    hnm_channel = bot.get_channel(hnm_channel_id)
    bot_channel = bot.get_channel(bot_commands)

    return hnm_channel, bot_channel

async def process_hnm_window(hnm_window_end, target_time, hnm, hnm_time, date,
                             day, message, guild, category, utc, hnm_times_channel,
                             hnm_name, time_diff):
    hnm_category = discord.utils.get(guild.categories, id=hnm_att_category_name)
    if hnm_window_end >= target_time:
        if hnm_time <= target_time:
            if any(keyword in message.content for keyword in ["Fafnir", "Adamantoise", "Behemoth"]):
                channel_name = f"{date}-{hnm}{day}".lower()
            else:
                channel_name = f"{date}-{hnm}".lower()

            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            if existing_channel:
                async for message in existing_channel.history(limit=1, oldest_first=True):
                    channel_dt, channel_utc = calculate_time_diff(message.content)
                if channel_utc == utc and category != hnm_category:
                    return
                elif channel_utc == utc and category == hnm_category:
                    await asyncio.sleep(5)
                    for task in asyncio.all_tasks():
                        if task.get_name() == f"wm-{channel_name}":
                            break
                    else:
                        if existing_channel.category == hnm_category:
                            await restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel)
                else:
                    channel_name = f"{channel_name}1"
                    existing_channel = discord.utils.get(guild.channels, name=channel_name)
                    if existing_channel:                    
                        await asyncio.sleep(5)
                        for task in asyncio.all_tasks():
                            if task.get_name() == f"wm-{channel_name}":
                                break
                        else:
                            if str(existing_channel.category_id) == hnm_category:
                                await restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel)
                    else:
                        await start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)
            else:
                await start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)

async def archive_channels(archive_category, archive_channel, category, option):
    data_dir = "data"
    backups_dir = "backups"
    category_folder = f"{category}"

    dir_structure = [data_dir, backups_dir, category_folder]

    current_path = ''
    for directory in dir_structure:
        current_path = os.path.join(current_path, directory)
        if not os.path.exists(current_path):
            os.mkdir(current_path)

    log_file_path = os.path.join(current_path, 'log.txt')

    if option == "delete":
        channel = archive_channel
        file_name = os.path.join(current_path, f"{channel.name}.csv")

        data = []
        async for message in channel.history(limit=None, oldest_first=True):
            data.append({
                "Author": message.author.display_name,
                "Content": message.content,
                "Timestamp": message.created_at
            })

        df = pd.DataFrame(data)
        df.to_csv(file_name, index=False)

        log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
        async with aiofiles.open(log_file_path, "a") as file:
            await file.write(log_message + "\n")

        await channel.delete()

    elif option == "all":  # 'all' argument will archive all channels in the category
        channels = category.channels

        for channel in channels:
            if isinstance(channel, (discord.VoiceChannel, discord.CategoryChannel)):
                continue

            file_name = os.path.join(current_path, f"{channel.name}.csv")

            data = []
            async for message in channel.history(limit=None, oldest_first=True):
                data.append({
                    "Author": message.author.display_name,
                    "Content": message.content,
                    "Timestamp": message.created_at
                })

            df = pd.DataFrame(data)
            df.to_csv(file_name, index=False)

            if archive_category:
                await channel.edit(category=archive_category)
            else:
                await channel.send("The 'Archive' category does not exist.")

            log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
            async with aiofiles.open(log_file_path, "a") as file:
                await file.write(log_message + "\n")

    else:
        channel = archive_channel
        file_name = os.path.join(current_path, f"{channel.name}.csv")

        data = []
        async for message in channel.history(limit=None, oldest_first=True):
            data.append({
                "Author": message.author.display_name,
                "Content": message.content,
                "Timestamp": message.created_at
            })

        df = pd.DataFrame(data)
        df.to_csv(file_name, index=False)

        if archive_category:
            await channel.edit(category=archive_category)
        else:
            await channel.send("The 'Archive' category does not exist.")

        log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
        async with aiofiles.open(log_file_path, "a") as file:
            await file.write(log_message + "\n")
