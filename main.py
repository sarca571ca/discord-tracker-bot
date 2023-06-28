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
        # Read messages from the target channels
        async for message in hnm_times_channel.history(limit=None, oldest_first=True):
            if message.content.startswith("-"):

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

                # Extract UTC timestamp
                utc_start = message.content.find("<t:")
                utc_end = message.content.find(":T>")
                if utc_start != -1 and utc_end != -1:
                    utc = int(message.content[utc_start + 3:utc_end])
                    dt = datetime.fromtimestamp(utc)
                    date = dt.strftime("%b%d").lower()
                    hnm = channel_name.upper()
                    hnm_name = message.content
                    unix_now = int(datetime.now().timestamp())
                    unix_target = int(dt.timestamp())
                    time_diff = unix_now - unix_target

                    # Subtract 10 minutes from the posted time and compare it to target_time
                    hnm_time = datetime.fromtimestamp(utc - (ss['make_channel'] * 60))
                    hnm_window_end = datetime.fromtimestamp(utc + (1 * 3600))

                    # Create the channel inside the category with the calculated time
                    if hnm_window_end >= target_time:
                        if hnm_time <= target_time:
                            if any(keyword in message.content for keyword in ["Fafnir", "Adamantoise", "Behemoth"]):
                                channel_name = f"{date}-{hnm}{day}".lower()
                            else:
                                channel_name = f"{date}-{hnm}".lower()

                            existing_channel = discord.utils.get(guild.channels, name=channel_name)
                            if existing_channel:
                                await asyncio.sleep(5)
                                # Check if a window_manager task is already running for the channel
                                for task in asyncio.all_tasks():
                                    if task.get_name() == f"wm-{channel_name}":
                                        break
                                else:
                                    # Channel already exists, check if it qualifies for window_manager
                                    if time_diff >= 0 and time_diff <= 3900:
                                        wmtask = asyncio.create_task(window_manager(channel_name))
                                        wmtask.set_name(f"wm-{channel_name}")
                            else:
                                channel = await guild.create_text_channel(channel_name, category=category, topic=f"<t:{utc}:T> <t:{utc}:R>")
                                await channel.edit(position=hnm_times_channel.position + 1)
                                await channel.send(f"{hnm_name}")
                                await channel.send(f"@everyone First window in {ss['make_channel']}-Minutes")
                                wttask = asyncio.create_task(warn_ten(channel_name))
                                wttask.set_name(f"wt-{channel_name}")
                                wmtask = asyncio.create_task(window_manager(channel_name))
                                wmtask.set_name(f"wm-{channel_name}")
            pass
    except discord.errors.DiscordServerError as e:
        if e.code == 0 and e.status == 503:
            print("Service Unavailable error. Retrying in 60 seconds...")
            await asyncio.sleep(60)  # Adjust the delay as needed
            create_channel_task.start()  # Restart the task
        else:
            # Handle other Discord server errors
            print(f"DiscordServerError: {e}")
    except Exception as e:
        # Handle other exceptions
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
            await asyncio.sleep(60)  # Adjust the delay as needed
            delete_old_channels.start()  # Restart the task
        else:
            # Handle other Discord server errors
            print(f"DiscordServerError: {e}")
    except Exception as e:
        # Handle other exceptions
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    create_channel_task.start()
    delete_old_channels.start()
    with open('images/logo.png', 'rb') as avatar_file:
        avatar = avatar_file.read()
        await bot.user.edit(avatar=avatar)
    guild = bot.get_guild(guild_id)
    member = guild.get_member(bot.user.id)
    if member:
        display_name = "Alise"
        await member.edit(nick=display_name)
        print(f"Display name set to: {display_name}")

@bot.event
async def on_message(message):
    bot_channel = bot.get_channel(bot_commands)

    # Check if the message is from a DM channel
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith('!help'):
            await message.author.send("This is the help command response.")
        else:
            await message.author.send(f"Please use the `!help` command in {bot_channel.mention}")

    elif ss['clear_bot_commands'] == True:
        # Check if the message is sent in the 'bot-commands' channel
        if message.channel.name == 'bot-commands':
            await message.delete()

    await bot.process_commands(message)

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

# Archive command used for moving channels from DKP Review Category
@bot.command()
async def archive(ctx, option=None):
# Check if the category is "DKP REVIEW"
    category = ctx.channel.category

    if not category or category.name != dkp_review_category_name:
        await ctx.send("The command can only be used in the 'DKP REVIEW' category.")
        return

    # Create the data folder if it doesn't exist
    dt = "data"
    if not os.path.exists(dt):
        os.mkdir(dt)

    # Create the backups folder if it doesn't exist
    backups = f"backups"
    if not os.path.exists(f"{dt}/{backups}"):
        os.mkdir(f"{dt}/{backups}")

    # Create the category folder if it doesn't exist
    folder_name = f"{category}"
    if not os.path.exists(f"{dt}/{backups}/{folder_name}"):
        os.mkdir(f"{dt}/{backups}/{folder_name}")

    log_file = f"{dt}/{backups}/{folder_name}/log.txt"

    if option == "all":
        # Get all channels in the category
        channels = category.channels

        for channel in channels:
            # Skip voice channels and categories
            if isinstance(channel, (discord.VoiceChannel, discord.CategoryChannel)):
                continue

            # Create a CSV file with the channel's name
            file_name = f"{dt}/{backups}/{folder_name}/{channel.name}.csv"

            # Create a DataFrame to store the messages
            data = []
            async for message in channel.history(limit=None, oldest_first=True):
                data.append({
                    "Author": message.author.display_name,
                    "Content": message.content,
                    "Timestamp": message.created_at
                })

            df = pd.DataFrame(data)

            # Write the DataFrame to a CSV file
            df.to_csv(file_name, index=False)

            # Move the channel to the "Archive" category
            archive_category = discord.utils.get(ctx.guild.categories, name=att_arch_category_name)
            if archive_category:
                await channel.edit(category=archive_category)
            else:
                await ctx.send("The 'Archive' category does not exist.")

            # Append log message to the log file
            log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
            with open(log_file, "a") as file:
                file.write(log_message + "\n")

    else:
        # Get the current channel
        channel = ctx.channel

        # Create a CSV file with the channel's name
        file_name = f"{dt}/{backups}/{folder_name}/{channel.name}.csv"

        # Create a DataFrame to store the messages
        data = []
        async for message in channel.history(limit=None, oldest_first=True):
            data.append({
                "Author": message.author.display_name,
                "Content": message.content,
                "Timestamp": message.created_at
            })

        df = pd.DataFrame(data)

        # Write the DataFrame to a CSV file
        df.to_csv(file_name, index=False)

        # Move the channel to the "Archive" category
        archive_category = discord.utils.get(ctx.guild.categories, name=att_arch_category_name)
        if archive_category:
            await channel.edit(category=archive_category)
        else:
            await ctx.send("The 'Archive' category does not exist.")

        # Append log message to the log file
        log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
        with open(log_file, "a") as file:
            file.write(log_message + "\n")

# Command used to sort the hnm-times
@bot.command()
async def sort(ctx):
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

# Send the 10-Minute warning to the channel
async def warn_ten(channel_name):
    now = datetime.now()

    # Get the category by name
    guild = bot.get_guild(guild_id)
    category_name = hnm_att_category_name
    category = discord.utils.get(guild.categories, name=category_name)

    # Adding a sleep to the task to deal with any potential latency issues.
    await asyncio.sleep(1)

    if not category:
        return

    channels = category.channels

    for channel in channels:
        if isinstance(channel, discord.TextChannel) and channel_name in channel.name and all(keyword not in channel.name for keyword in ss['ignore_channels']):
            async for message in channel.history(limit=1, oldest_first=True):
                # Extract the UTC timestamp
                utc_start = message.content.find("<t:")
                utc_end = message.content.find(":T>")
                if utc_start != -1 and utc_end != -1:
                    utc = message.content[utc_start + 3:utc_end]
                    dt = datetime.fromtimestamp(int(utc) - (10 * 60))

                    # Determine the delay needed before window opens
                    delay = dt - now
                    # Sends window open message channel
                    if delay.total_seconds() > 0:
                        await asyncio.sleep(delay.total_seconds())
                    await channel.send(f"-------- Window opens in 10-Minutes x in --------")
                    await channel.send(ss['window_message'])

                    return

# Helpers can probably move these to a module later on for readability
async def window_manager(channel_name):
#######################################################################################
# window_manager_______________________________________________________________________
# Manages the windows within the channels
# ToDo:
########################################################################################
    now = datetime.now()

    # Get the category by name
    guild = bot.get_guild(guild_id)
    category_name = hnm_att_category_name
    category = discord.utils.get(guild.categories, name=category_name)

    dkp_review_category = discord.utils.get(guild.categories, name=dkp_review_category_name)

    # Adding a sleep to the task to deal with any potential latency issues.
    await asyncio.sleep(1)

    if not category:
        return

    channels = category.channels

    for channel in channels:
        if isinstance(channel, discord.TextChannel) and channel_name in channel.name and all(keyword not in channel.name for keyword in ss['ignore_channels']):
            async for message in channel.history(limit=1, oldest_first=True):
                # Extract the UTC timestamp
                utc_start = message.content.find("<t:")
                utc_end = message.content.find(":T>")
                if utc_start != -1 and utc_end != -1:
                    utc = int(message.content[utc_start + 3:utc_end])
                    dt = datetime.fromtimestamp(utc)
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
                            if ss['wm_close_trigger'] is True:
                                async for message in channel.history(limit=None):
                                    if message.content.lower() in ["!kill", "!pop", "!claim", "!ours"]:
                                        # Stop the window manager loop
                                        await asyncio.sleep(300)
                                        await channel.send("Moving channel for dkp review in 5 minutes.")
                                        await asyncio.sleep(300)
                                        await channel.edit(category=dkp_review_category)
                                        return await calculate_DKP(channel, channel_name, window)
                            if "shi" in channel.name:
                                await channel.send(f"------------ Shikigami Weapon has spawned ------------")
                                await asyncio.sleep(300)
                                await channel.send("Moving channel for dkp review in 5 minutes.")
                                await asyncio.sleep(300)
                                await channel.edit(category=dkp_review_category)
                                return await calculate_DKP(channel, channel_name, window - 1)
                            else:
                                await channel.send(f"--------------- Window {window} is now ---------------")
                                await asyncio.sleep(5)
                        await asyncio.sleep(1)
                        time_diff = int(datetime.now().timestamp()) - unix_target

                    await asyncio.sleep(300)

                    await channel.send("Moving channel for dkp review in 5 minutes.")
                    await asyncio.sleep(300)

                    await channel.edit(category=dkp_review_category)
                    return await calculate_DKP(channel, channel_name, window - 1)

# Build this function out to handle calculating dkp and listen for late x's in the channel
async def calculate_DKP(channel, channel_name, w):
    await channel.send("!DKPExport")

async def handle_hnm_command(ctx, hnm, hq, day: int, timestamp):
    original_hnm = hnm  # Store the original HNM name

    if hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
        hnm = "GroundKings"
    if hnm in ["Jormungand", "Tiamat", "Vrtra"]:
        hnm = "GrandWyrm"

    day = int(day) + 1


    channel_id = hnm_times
    channel = bot.get_channel(channel_id)
    bot_channel = bot.get_channel(bot_commands)

    # Error handling when user doesnt enter a time after the day.
    if timestamp == None:
        await ctx.author.send(f"No date/time provided for {original_hnm}.\nPlease resend the command in {bot_channel.metion}")
    # List of accepted date formats
    date_formats = [
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
        try:
            # Try parsing the timestamp with the current format
            parsed_datetime = time_zone.localize(datetime.strptime(timestamp, date_format))
            valid_format = True
            break
        except ValueError:
            pass

    # If the timestamp does not match any accepted formats, try parsing with the '%H%M%S' format
    if not valid_format:
        for time_format in time_formats:
            try:
                # Try parsing the timestamp with the current format
                parsed_time = datetime.strptime(timestamp, time_format).time()
                parsed_datetime = time_zone.localize(datetime.combine(current_date, parsed_time))
                valid_format = True
                break
            except ValueError:
                pass

    if valid_format:
        # Check if the parsed datetime is in the future
        if parsed_datetime > datetime.now(time_zone):
            # Subtract one day from the current date
            current_date -= timedelta(days=1)
        if "GrandWyrm" not in hnm:
            parsed_datetime = time_zone.localize(datetime.combine(current_date, parsed_datetime.time()))

        unix_timestamp = int(parsed_datetime.timestamp())
    else:
        await ctx.author.send(f"Incorrect timestamp format for {original_hnm}.\nPlease resend the command in {bot_channel.mention}")

    # la_time = time_zone.localize(parsed_datetime)
    # unix_timestamp = int(la_time.timestamp())

    try:
        if original_hnm in ["Fafnir", "Adamantoise", "Behemoth", "King Arthro", "Simurgh"]:
            unix_timestamp += (22 * 3600)  # Add 22 hours for GroundKings and KA
        elif original_hnm in ["Jormungand", "Tiamat", "Vrtra"]:
            unix_timestamp += (84 * 3600)  # Add 84 hours for GrandWyrms and KA
        else:
            unix_timestamp += (21 * 3600)  # Add 21 hours for other HNMs
    except (ValueError, OverflowError):
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

    await sort(ctx)  # Trigger the sort command after handling the hnm command

def get_utc_timestamp(message):
    if "<t:" not in message.content:
        return 0
    timestamp_start = message.content.index("<t:") + 3
    timestamp_end = message.content.index(":T>", timestamp_start)
    timestamp = message.content[timestamp_start:timestamp_end]
    return int(timestamp)

def ref(text):
    # Remove any formatting (e.g., **bold**, *italic*, __underline__, ~~strikethrough~~, etc.)
    pattern = r'(\*\*|\*|__|~~)(.*?)(\*\*|\*|__|~~)'
    stripped_text = re.sub(pattern, r'\2', text)

    return stripped_text

bot.run(bot_id)