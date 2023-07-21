import discord
from discord.ext import commands, tasks
import time
from datetime import datetime, timedelta, timezone
import re
import os
import pandas as pd
import asyncio
import pytz
import yaml


def load_settings():
    with open('settings.yaml', 'r') as f:
        ss = yaml.safe_load(f)
    return ss

intents = discord.Intents.all()

ss = load_settings()

bot = commands.Bot(command_prefix="!", intents=intents)
# Variables for the server
guild_id = ss['guild']                         # Replace with your guild ID
hnm_times =  ss['hnm_times']                   # Replace with the HNM TIMES channel ID
bot_commands = ss['bot_commands']              # Replace with bot-commands channel ID
bot_id = ss['bot_token']                       # Replace with Bot Token
dkp_review_category_name = "DKP REVIEW"
hnm_att_category_name = "HNM ATTENDANCE"
att_arch_category_name = "ATTENDANCE ARCHIVE"
time_zone = pytz.timezone('America/Los_Angeles')
running_tasks = []
processed_channels_list = []

@tasks.loop(seconds=60)
async def create_channel_task():
#######################################################################################
# create_channel_task _________________________________________________________________
# Task currently creates a channel 30 minutes prior to window and notifies everyone.
# ToDo:
#   - Grand Wyrvn's will be managed by guild memembers
########################################################################################

    hnm_times_channel_id = hnm_times

    guild = bot.get_guild(guild_id)
    category = discord.utils.get(guild.categories, name=hnm_att_category_name)
    hnm_times_channel = bot.get_channel(hnm_times_channel_id)

    if not category:
        category = await guild.create_category(hnm_att_category_name)

    now = int(time.time())
    target_time = datetime.fromtimestamp(now)
    try:
        async for message in hnm_times_channel.history(limit=None, oldest_first=True):
            if message.content.startswith("- "):

                # Extract the day
                day_start = message.content.find("(")
                day_end = message.content.find(")")
                if day_start != -1 and day_end != -1:
                    raw_day = message.content[day_start + 1:day_end].strip()
                    day = ref(raw_day)
                else:
                    day = None

                if any(keyword in message.content for keyword in ss['ignore_create_channels']):
                    continue
                elif "King Arthro" in message.content:
                    channel_name = "ka"
                else:
                    if day == None or int(day) <= 3:
                        channel_name = message.content[2:5].strip()
                    elif int(day) >= 4:
                        nq = message.content[2:5].strip()
                        hq_start = message.content.find("/") + 1
                        hq_end = message.content.find("(")
                        hq = message.content[hq_start:hq_end].strip()[:3]
                        channel_name = f"{nq}"

                dt, utc = calculate_time_diff(message.content) # Extracts the utc timestamp
                date = dt.strftime("%b%d").lower()
                hnm = channel_name.upper()
                hnm_name = message.content
                unix_now = int(datetime.now().timestamp())
                unix_target = int(dt.timestamp())
                time_diff = unix_now - unix_target

                # Subtract 10 minutes from the posted time and compare it to target_time
                hnm_time = datetime.fromtimestamp(utc - (ss['make_channel'] * 60))
                hnm_window_end = datetime.fromtimestamp(utc + (1 * 3600))

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
                            if channel_utc == utc:
                                await asyncio.sleep(5)
                                for task in asyncio.all_tasks():
                                    if task.get_name() == f"wm-{channel_name}":
                                        break
                                else:
                                    await restart_channel_tasks(channel_name, time_diff, existing_channel)
                            else:
                                channel_name = f"{channel_name}1"
                                existing_channel = discord.utils.get(guild.channels, name=channel_name)
                                if existing_channel:
                                    await restart_channel_tasks(channel_name, time_diff, existing_channel)
                                else:
                                    await start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)
                        else:
                            await start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)
            pass
    except discord.errors.DiscordServerError as e:
        if e.code == 0 and e.status == 503:
            print("Service Unavailable error. Retrying in 60 seconds...")
            await asyncio.sleep(60)
            create_channel_task.start()
        else:
            print(f"DiscordServerError: {e}")
    except Exception as e:
        print(f"Error: {e}")


@tasks.loop(hours=24)
async def delete_old_channels():
    try:
        archive_category = discord.utils.get(bot.guilds[0].categories, name=att_arch_category_name)
        if archive_category:
            for channel in archive_category.channels:
                if isinstance(channel, discord.TextChannel):
                    now = datetime.now(timezone.utc)
                    if (now - channel.created_at).days >= ss['archive_wait']:
                        await channel.delete()
        pass
    except discord.errors.DiscordServerError as e:
        if e.code == 0 and e.status == 503:
            print("Service Unavailable error. Retrying in 60 seconds...")
            await asyncio.sleep(60)
            delete_old_channels.start()
        else:
            print(f"DiscordServerError: {e}")
    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    create_channel_task.start()
    delete_old_channels.start()
    # with open('images/logo.png', 'rb') as avatar_file:
    #     avatar = avatar_file.read()
    #     await bot.user.edit(avatar=avatar)
    guild = bot.get_guild(guild_id)
    member = guild.get_member(bot.user.id)
    if member:
        display_name = "Alise"
        await member.edit(nick=display_name)
        print(f"Display name set to: {display_name}")

@bot.command(name='pop')
async def pop(ctx):
    async for message in ctx.channel.history(limit=1, oldest_first=True):
        if message.content.startswith("- "):
            dt, utc = calculate_time_diff(message.content)

    if isinstance(ctx.channel.name, discord.TextChannel):
        print(f"Pop: Channel {ctx.channel.name} is not a text channel. Ignoring.")
        return

    if not ctx.channel.category or ctx.channel.category.name != hnm_att_category_name:
        print(f"Pop: Channel {ctx.channel.name} is not in {hnm_att_category_name} category. Ignoring.")
        return

    if ctx.author.bot:
        print("Pop: Bot user issued command. Ignoring.")
        return
    for entry in processed_channels_list:
        if ctx.channel.id == entry["id"]:
            print(f"Pop: {ctx.channel.name} has already been processed. Ignoring.")
            return

    await ctx.message.delete()
    print(f"Pop: {ctx.author.display_name} issued !pop command.")
    await ctx.channel.send(f"------------------------- POP ------------------------")

    return await calculate_DKP(ctx.channel, ctx.channel.name, dt, utc)
pop.brief = f"Used when the NM has popped."
pop.usage = ""

@bot.command(name='close')
async def close(ctx):
    async for message in ctx.channel.history(limit=1, oldest_first=True):
        if message.content.startswith("- "):
            dt, utc = calculate_time_diff(message.content)

    existing_task = asyncio.all_tasks()
    for task in existing_task:
        if task.get_name() == f"wm-{ctx.channel.name}" or task.get_name() == f"wt-{ctx.channel.name}":
            task.cancel()

    process_dict = {
        "id": ctx.channel.id,
        "utc": utc,
        "processed": False
    }

    processed_channels_list.append(process_dict)
    await ctx.message.delete()
    await ctx.send("----------------------- Closed -----------------------")
    print(f"Close: {ctx.author.display_name} closed {ctx.channel.name}.")
close.brief = f"Used to re-open closed channels."
close.usage = ""

@bot.command(name='open')
async def open(ctx):
    async for message in ctx.channel.history(limit=1, oldest_first=True):
        if message.content.startswith("- "):
            dt, utc = calculate_time_diff(message.content)

    existing_task = asyncio.all_tasks()
    task_running = False
    for task in existing_task:
        if task.get_name() == f"wm-{ctx.channel.name}":
            await ctx.author.send(f"{ctx.channel.name} is already open.")
            task_running = True
    if not task_running:
        process_dict = {
            "id": ctx.channel.id,
            "utc": utc,
            "processed": False
        }

        processed_channels_list.remove(process_dict)
        await ctx.message.delete()
        await ctx.send("---------------------- Open x-in ---------------------")
        print(f"Open: {ctx.author.display_name} opened {ctx.channel.name}.")
open.brief = f"Used to close channels."
open.usage = ""

@bot.command(aliases=["faf", "fafnir"])
async def Fafnir(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Fafnir", "Nidhogg", day, timestamp)
Fafnir.brief = f"Used to set the ToD of Fafnir/Nidhogg."
Fafnir.usage = "<day> <timestamp>"

@bot.command(aliases=["ad", "ada", "adam", "adamantoise"])
async def Adamantoise(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Adamantoise", "Aspidochelone", day, timestamp)
Adamantoise.brief = f"Used to set the ToD of Adamantoise/Aspidochelone."
Adamantoise.usage = "<day> <timestamp>"

@bot.command(aliases=["be", "behe", "behemoth"])
async def Behemoth(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Behemoth", "King Behemoth", day, timestamp)
Behemoth.brief = f"Used to set the ToD of Behemoth/King Behemoth."
Behemoth.usage = "<day> <timestamp>"

@bot.command(aliases=["ka", "kinga"])
async def KingArthro(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "King Arthro", None, day, timestamp)
KingArthro.brief = f"Used to set the ToD of King Arthro."
KingArthro.usage = "<day> <timestamp>"

@bot.command(aliases=["sim"])
async def Simurgh(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Simurgh", None, day, timestamp)
Simurgh.brief = f"Used to set the ToD of Simurgh."
Simurgh.usage = "<day> <timestamp>"

@bot.command(aliases=["shi", "shiki", "shikigami"])
async def ShikigamiWeapon(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Shikigami Weapon", None, day, timestamp)
ShikigamiWeapon.brief = f"Used to set the ToD of Shikigami Weapon."
ShikigamiWeapon.usage = "<day> <timestamp>"

@bot.command(aliases=["kv", "kingv", "kingvine"])
async def KingVinegarroon(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "King Vinegarroon", None, day, timestamp)
KingVinegarroon.brief = f"Used to set the ToD of King Vinegarroon."
KingVinegarroon.usage = "<day> <timestamp>"

@bot.command(aliases=["vrt", "vrtr", "vrtra"])
async def Vrtra(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Vrtra", None, day, timestamp)
Vrtra.brief = f"Used to set the ToD of Vrtra."
Vrtra.usage = "<day> <timestamp>"

@bot.command(aliases=["tia", "tiam", "tiamat"])
async def Tiamat(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Tiamat", None, day, timestamp)
Tiamat.brief = f"Used to set the ToD of Tiamat."
Tiamat.usage = "<day> <timestamp>"

@bot.command(aliases=["jor", "jorm", "jormungand"])
async def Jormungand(
    ctx,
    day: str = commands.parameter(
        default="Day",
        description="Used for HQ system, can be set to 0 for mobs that do not HQ"
    ),
    *,
    timestamp: str = commands.parameter(
        default="Timestamp",
        description="ToD of the mob in your TZ"
    )
):
    allowed_channel_id = bot_commands
    author = ctx.author

    if ctx.channel.id != allowed_channel_id:
        await author.send("This command can only be used in the specified channel.")
        await ctx.message.delete()
        return

    await handle_hnm_command(ctx, "Jormungand", None, day, timestamp)
Jormungand.brief = f"Used to set the ToD of Jormungand."
Jormungand.usage = "<day> <timestamp>"

@bot.command() # Archive command used for moving channels from DKP Review Category
async def archive(ctx, option=None):
    category = ctx.channel.category

    if not category or category.name != dkp_review_category_name:
        await ctx.send("The command can only be used in the 'DKP REVIEW' category.")
        return

    dt = "data"
    if not os.path.exists(dt):
        os.mkdir(dt)

    backups = f"backups"
    if not os.path.exists(f"{dt}/{backups}"):
        os.mkdir(f"{dt}/{backups}")

    folder_name = f"{category}"
    if not os.path.exists(f"{dt}/{backups}/{folder_name}"):
        os.mkdir(f"{dt}/{backups}/{folder_name}")

    log_file = f"{dt}/{backups}/{folder_name}/log.txt"

    if option == "all": # all argument will archive all channels in the category
        channels = category.channels

        for channel in channels:
            if isinstance(channel, (discord.VoiceChannel, discord.CategoryChannel)):
                continue

            file_name = f"{dt}/{backups}/{folder_name}/{channel.name}.csv"

            data = []
            async for message in channel.history(limit=None, oldest_first=True):
                data.append({
                    "Author": message.author.display_name,
                    "Content": message.content,
                    "Timestamp": message.created_at
                })

            df = pd.DataFrame(data)

            df.to_csv(file_name, index=False)

            archive_category = discord.utils.get(ctx.guild.categories, name=att_arch_category_name)
            if archive_category:
                await channel.edit(category=archive_category)
            else:
                await ctx.send("The 'Archive' category does not exist.")

            log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
            with open(log_file, "a") as file:
                file.write(log_message + "\n")

    else:
        channel = ctx.channel

        file_name = f"{dt}/{backups}/{folder_name}/{channel.name}.csv"

        data = []
        async for message in channel.history(limit=None, oldest_first=True):
            data.append({
                "Author": message.author.display_name,
                "Content": message.content,
                "Timestamp": message.created_at
            })

        df = pd.DataFrame(data)

        df.to_csv(file_name, index=False)

        archive_category = discord.utils.get(ctx.guild.categories, name=att_arch_category_name)
        if archive_category:
            await channel.edit(category=archive_category)
        else:
            await ctx.send("The 'Archive' category does not exist.")

        log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
        with open(log_file, "a") as file:
            file.write(log_message + "\n")


@bot.command()
async def sort(ctx): # Command used to sort the hnm-times
    channel_id = hnm_times
    channel = bot.get_channel(channel_id)

    messages = []

    async for message in channel.history(limit=None):
        if message.author == bot.user:
            messages.append(message)

    messages.sort(key=lambda m: get_utc_timestamp(m))

    for message in messages:
        content = message.content
        await message.delete()
        await channel.send(content)

async def warn_ten(channel_name):
    now = datetime.now()

    guild = bot.get_guild(guild_id)
    category_name = hnm_att_category_name
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        return

    channels = category.channels
    try:
        for channel in channels:
            if isinstance(channel, discord.TextChannel) and channel_name in channel.name and all(keyword not in channel.name for keyword in ss['ignore_channels']):
                async for message in channel.history(limit=1, oldest_first=True):
                    dt, utc = calculate_time_diff(message.content)
                    dt = datetime.fromtimestamp(utc - (10 * 60))
                    delay = dt - now
                    if delay.total_seconds() > 0:
                        await asyncio.sleep(delay.total_seconds())
                    await channel.send(f"---------- Window opens in 10-Minutes x-in ----------")
                    await channel.send(ss['window_message'])

                    return
    except asyncio.CancelledError:
        print(f"Warn Ten: Task for channel {channel_name} was cancelled.")

async def window_manager(channel_name):
#######################################################################################
# window_manager_______________________________________________________________________
# Manages the windows within the channels
# ToDo:
########################################################################################
    now = datetime.now()

    guild = bot.get_guild(guild_id)
    category_name = hnm_att_category_name
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        return

    channels = category.channels

    try:
        for channel in channels:
            if isinstance(channel, discord.TextChannel) and channel_name in channel.name and all(keyword not in channel.name for keyword in ss['ignore_channels']):
                async for message in channel.history(limit=1, oldest_first=True):
                    dt, utc = calculate_time_diff(message.content)

                    unix_now = int(datetime.now().timestamp())
                    unix_target = int(dt.timestamp())

                    time_diff = unix_now - unix_target
                    sleep_time = unix_target - unix_now
                    if time_diff <= -0:
                        await asyncio.sleep(sleep_time)
                        time_diff = int(datetime.now().timestamp()) - unix_target

                    while time_diff >= 0 and time_diff <= 3600:
                        if time_diff % 600 == 0:
                            window = round(time_diff / 600) + 1
                            if "shi" in channel.name:
                                await channel.send(f"------------ Shikigami Weapon has spawned ------------")
                                return await calculate_DKP(channel, channel_name, dt, utc)
                            else:
                                await channel.send(f"------------------- Window {window} is now ------------------")
                                await asyncio.sleep(5)
                        await asyncio.sleep(1)
                        time_diff = int(datetime.now().timestamp()) - unix_target

                    return await calculate_DKP(channel, channel_name, dt, utc)
    except asyncio.CancelledError:
        print(f"Window Manager: Task for channel {channel_name} was cancelled.")

async def calculate_DKP(channel, channel_name, dt, utc):
    guild = bot.get_guild(guild_id)
    dkp_review_category = discord.utils.get(guild.categories, name=dkp_review_category_name)
    existing_task = asyncio.all_tasks()

    process_dict = {
        "id": channel.id,
        "utc": utc,
        "processed": True
    }

    processed_channels_list.append(process_dict)

    await channel.send("Moving channel for dkp review in 5 minutes.")
    await asyncio.sleep(300)
    await channel.edit(category=dkp_review_category)
    await channel.send("--------------------- DKP Review ---------------------")
    for task in existing_task:
        if task.get_name() == f"wm-{channel_name}" or task.get_name() == f"wt-{channel_name}":
            task.cancel()
            print(f"Calc DKP: Task for channel {channel_name} was completed.")

async def handle_hnm_command(ctx, hnm, hq, day: int, timestamp):
    original_hnm = hnm  # Store the original HNM name
    channel_id = hnm_times
    channel = bot.get_channel(channel_id)
    bot_channel = bot.get_channel(bot_commands)

    if hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
        hnm = "GroundKings"
    if hnm in ["Jormungand", "Tiamat", "Vrtra"]:
        hnm = "GrandWyrm"
    try:
        day = int(day) + 1
    except (ValueError, OverflowError):
        print("Handle HNM: Day was not provided.")
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
            print("Handle HNM: No timestamp provided.")
        else:
            await ctx.author.send(f"Incorrect time format for {original_hnm}.\nUse the !help command for a list of commands and how to use them.\n Then resend your command in  {bot_channel.mention}")
            print("Handle HNM: Incorrect timestamp format was provided.")
        return

    try:
        if original_hnm in ["Fafnir", "Adamantoise", "Behemoth", "King Arthro", "Simurgh"]:
            unix_timestamp += (22 * 3600)  # Add 22 hours for GroundKings and KA
        elif original_hnm in ["Jormungand", "Tiamat", "Vrtra"]:
            unix_timestamp += (84 * 3600)  # Add 84 hours for GrandWyrms and KA
        else:
            unix_timestamp += (21 * 3600)  # Add 21 hours for other HNMs
    except (UnboundLocalError):
        print("Handle HNM: No timestamp provided.")
        return
    except (ValueError, OverflowError):
        print("Handle HNM: HNM provided does not exist.")
        return

    async for message in channel.history(limit=None):
        if message.author == bot.user and message.content.startswith(f"- {original_hnm}"):
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

    await sort(ctx)

def calculate_time_diff(message_content):
    # Extract the UTC timestamp
    utc_start = message_content.find("<t:")
    utc_end = message_content.find(":T>")
    if utc_start != -1 and utc_end != -1:
        utc = int(message_content[utc_start + 3:utc_end])
        dt = datetime.fromtimestamp(utc)
        return dt, utc
    else:
        return None, None  # If no valid timestamp found, return None

async def start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name):
    channel = await guild.create_text_channel(channel_name, category=category, topic=f"<t:{utc}:T> <t:{utc}:R>")
    await channel.edit(position=hnm_times_channel.position + 1)
    await channel.send(f"{hnm_name}")
    await channel.send(f"@everyone First window in {ss['make_channel']}-Minutes")
    wttask = asyncio.create_task(warn_ten(channel_name))
    wttask.set_name(f"wt-{channel_name}")
    task_name = wttask.get_name()
    print(f"Warn Ten: Task for {task_name} has been started.")
    running_tasks.append(task_name)
    wmtask = asyncio.create_task(window_manager(channel_name))
    wmtask.set_name(f"wm-{channel_name}")
    task_name = wmtask.get_name()
    print(f"Window Manager: Task {task_name} has been started.")
    running_tasks.append(task_name)

async def restart_channel_tasks(channel_name, time_diff, existing_channel):
    if time_diff >= 0 and time_diff <= 3900 and not processed_channels_list:
        wmtask = asyncio.create_task(window_manager(channel_name))
        wmtask.set_name(f"wm-{channel_name}")
        task_name = wmtask.get_name()
        print(f"Window Manager: Task {task_name} has been started.")
        running_tasks.append(task_name)
    else:
        processed_id = False
        for entry in processed_channels_list:
            if existing_channel.id == entry["id"]:
                processed_id = True
                break
            print("nothing found")

        if time_diff >= 0 and time_diff <= 3900 and not processed_id:
            print("I decided to start anyways")
            wmtask = asyncio.create_task(window_manager(channel_name))
            wmtask.set_name(f"wm-{channel_name}")
            task_name = wmtask.get_name()
            print(f"Window Manager: Task {task_name} has been started.")
            running_tasks.append(task_name)

def get_utc_timestamp(message):
    if "<t:" not in message.content:
        return 0
    timestamp_start = message.content.index("<t:") + 3
    timestamp_end = message.content.index(":T>", timestamp_start)
    timestamp = message.content[timestamp_start:timestamp_end]
    return int(timestamp)

def ref(text): # Remove any formatting (e.g., **bold**, *italic*, __underline__, ~~strikethrough~~, etc.)
    pattern = r'(\*\*|\*|__|~~)(.*?)(\*\*|\*|__|~~)'
    stripped_text = re.sub(pattern, r'\2', text)

    return stripped_text

bot.run(bot_id)