import discord
from discord.ext import commands, tasks
import time
import datetime
import re
import ss             # Server specific variables see the ss.py and insert your values
import os
import pandas as pd
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)
# Variables for the server
guild_id = ss.guild                # Replace with your guild ID
hnm_times =  ss.hnm_times          # Replace with the HNM TIMES channel ID
bot_commands = ss.bot_commands     # Replace with bot-commands channel ID
bot_id = ss.wd_tod                    # Replace with Bot Token

async def task_window_manager(channel_name):
    await window_manager(channel_name)

async def task_warn_ten(channel_name):
    await warn_ten(channel_name)

@tasks.loop(minutes=1)
async def create_channel_task():
#######################################################################################
# create_channel_task _________________________________________________________________
# Task currently creates a channel 30 minutes prior to window and notifies everyone.
# ToDo:
#   - Grand Wyrvn management still needs to be implemented
#   - Grand Wyrvn's will be managed by guild memembers
#   - Need to set a priority system based on LS rules or
########################################################################################

    category_name = "HNM ATTENDANCE"
    hnm_times_channel_id = hnm_times

    guild = bot.get_guild(guild_id)
    category = discord.utils.get(guild.categories, name=category_name)
    hnm_times_channel = bot.get_channel(hnm_times_channel_id)

    if not category:
        category = await guild.create_category(category_name)

    now = int(time.time())
    target_time = datetime.datetime.fromtimestamp(now)

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

            if any(keyword in message.content for keyword in ss.ignore_create_channels):
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
                    channel_name = f"{nq}{hq}"

            # Extract UTC timestamp
            utc_start = message.content.find("<t:")
            utc_end = message.content.find(":T>")
            if utc_start != -1 and utc_end != -1:
                utc = int(message.content[utc_start + 3:utc_end])
                dt = datetime.datetime.utcfromtimestamp(utc)
                date = dt.strftime("%b%d").lower()
                hnm = channel_name.upper()
                hnm_name = message.content

                # Subtract 10 minutes from the posted time and compare it to target_time
                hnm_time = datetime.datetime.fromtimestamp(utc - (ss.make_channel * 60))
                hnm_window_end = datetime.datetime.fromtimestamp(utc + (1 * 3600))

                # Create the channel inside the category with the calculated time
                if hnm_window_end >= target_time:
                    if hnm_time <= target_time:
                        if any(keyword in message.content for keyword in ["Fafnir", "Adamantoise", "Behemoth"]):
                            channel_name = f"{date}-{hnm}{day}".lower()
                        else:
                            channel_name = f"{date}-{hnm}".lower()

                        existing_channel = discord.utils.get(guild.channels, name=channel_name)
                        if not existing_channel:
                            channel = await guild.create_text_channel(channel_name, category=category, topic=f"<t:{utc}:T> <t:{utc}:R>")
                            await channel.edit(position=hnm_times_channel.position + 1)
                            await channel.send(f"{hnm_name}")
                            await channel.send(f"@everyone First window in {ss.make_channel}-Minutes")
                            asyncio.create_task(task_warn_ten(channel_name)) # Starts a task to post in channel 10-minutes before window
                            asyncio.create_task(task_window_manager(channel_name))  # Starts a task to manage the window


@tasks.loop(minutes=30)
async def move_for_review():
#######################################################################################
# move_for_review______________________________________________________________________
# Moves the channel's for DKP Review 3-hours from spawn time
########################################################################################
    target_channel_id = hnm_times  # Replace with your target channel ID
    dkp_review_category_name = "DKP REVIEW"  # Replace with the name of your DKP review category

    guild = bot.get_guild(guild_id)
    target_channel = bot.get_channel(target_channel_id)
    dkp_review_category = discord.utils.get(guild.categories, name=dkp_review_category_name)

    now = int(time.time())
    target_time = datetime.datetime.fromtimestamp(now)

    async for message in target_channel.history(limit=None, oldest_first=True):
        if message.content.startswith("-"):
            channel_name = message.content[2:5].strip()

            # Extract the day
            day_start = message.content.find("(")
            day_end = message.content.find(")")
            if day_start != -1 and day_end != -1:
                raw_day = message.content[day_start + 1:day_end].strip()
                day = ref(raw_day)
            else:
                day = None

            if any(keyword in message.content for keyword in ss.ignore_create_channels):
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
                    channel_name = f"{nq}{hq}"

            # Extract UTC timestamp
            utc_start = message.content.find("<t:")
            utc_end = message.content.find(":T>")
            if utc_start != -1 and utc_end != -1:
                utc = int(message.content[utc_start + 3:utc_end])
                dt = datetime.datetime.utcfromtimestamp(utc)
                date = dt.strftime("%b%d").lower()
                hnm = channel_name.upper()
                hnm_name = message.content

                # Time to move channels
                hnm_time = datetime.datetime.fromtimestamp(utc + (ss.move_review * 3600))

                # Move channels if 4 hours has passed the hnm camp time
                if not hnm_time >= target_time:
                    if any(keyword in message.content for keyword in ["Fafnir", "Adamantoise", "Behemoth"]):
                        channel_name = f"{date}-{hnm}{day}".lower()
                    else:
                        channel_name = f"{date}-{hnm}".lower()
                    existing_channel = discord.utils.get(guild.channels, name=channel_name)
                    if existing_channel:
                        await existing_channel.edit(category=dkp_review_category)

@tasks.loop(hours=24)  # Task runs every 24 hours
async def delete_old_channels():
    archive_category = discord.utils.get(bot.guilds[0].categories, name="ARCHIVE")  # Assuming the bot is in only one guild
    if archive_category:
        for channel in archive_category.channels:
            if isinstance(channel, discord.TextChannel):
                now = datetime.datetime.now(datetime.timezone.utc)  # Make datetime.now() offset-aware
                if (now - channel.created_at).days >= ss.archive_wait:  # Check if the channel is older than ss.archive_wait
                    await channel.delete()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    create_channel_task.start()
    move_for_review.start()
    delete_old_channels.start()

@bot.event
async def on_message(message):
    bot_channel = bot.get_channel(bot_commands)

    # Check if the message is from a DM channel
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith('!help'):
            await message.author.send("This is the help command response.")
        else:
            await message.author.send(f"Please use the `!help` command in {bot_channel.mention}")

    # else:
    #     # Check if the message is sent in the 'bot-commands' channel
    #     if message.channel.name == 'bot-commands':
    #         await message.delete()

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

# Archive command used for moving channels from DKP Review Category
@bot.command()
async def archive(ctx, option=None):
    target_channel_ids = [bot_commands, hnm_times]  # Replace with the actual channel IDs

    # Check if the category is "DKP REVIEW"
    category = ctx.channel.category

    if not category or category.name != "DKP REVIEW":
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
                    "Author": message.author.name,
                    "Content": message.content,
                    "Timestamp": message.created_at
                })

            df = pd.DataFrame(data)

            # Write the DataFrame to a CSV file
            df.to_csv(file_name, index=False)

            # Move the channel to the "Archive" category
            archive_category = discord.utils.get(ctx.guild.categories, name="Archive")
            if archive_category:
                await channel.edit(category=archive_category)
                await ctx.send(f"Channel '{channel.name}' has been archived.")
            else:
                await ctx.send("The 'Archive' category does not exist.")

            # Append log message to the log file
            log_message = f"Channel '{channel.name}' has been archived at {datetime.now()}"
            with open(log_file, "a") as file:
                file.write(log_message + "\n")

        await ctx.send("All channels in the 'DKP REVIEW' category have been archived.")

        # Append log message to the log file
        log_message = f"All channels in the 'DKP REVIEW' category have been archived at {datetime.now()}"
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
                "Author": message.author.name,
                "Content": message.content,
                "Timestamp": message.created_at
            })

        df = pd.DataFrame(data)

        # Write the DataFrame to a CSV file
        df.to_csv(file_name, index=False)

        # Move the channel to the "Archive" category
        archive_category = discord.utils.get(ctx.guild.categories, name="Archive")
        if archive_category:
            await channel.edit(category=archive_category)
            await ctx.send(f"Channel '{channel.name}' has been archived.")
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

async def warn_ten(channel_name):
    now = datetime.datetime.now()

    # Get the category by name
    guild = bot.get_guild(guild_id)  # Replace with the actual guild ID
    category_name = "HNM ATTENDANCE"
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        return

    channels = category.channels

    for channel in channels:
        if isinstance(channel, discord.TextChannel) and channel_name in channel.name and all(keyword not in channel.name for keyword in ss.ignore_channels):
            async for message in channel.history(limit=1, oldest_first=True):
                # Extract the UTC timestamp
                utc_start = message.content.find("<t:")
                utc_end = message.content.find(":T>")
                if utc_start != -1 and utc_end != -1:
                    utc = message.content[utc_start + 3:utc_end]
                    dt = datetime.datetime.fromtimestamp(int(utc) - (10 * 60))

                    # Determine the delay needed before window opens
                    delay = dt - now
                    # Sends window open message channel
                    if delay.total_seconds() > 0:
                        await asyncio.sleep(delay.total_seconds())
                    await channel.send(f"-------- Window opens in 10-Minutes x in --------")
                    await channel.send(ss.window_message)

                    return

# Helpers can probably move these to a module later on for readability
async def window_manager(channel_name):
#######################################################################################
# window_manager_______________________________________________________________________
# Manages the windows within the channels
# ToDo:
#   - Grand Wyvrn
#       - Open windows 10-minutes prior to spawn and close them 1-minute after spawn
#       - Repeat until it spawns
########################################################################################
    now = datetime.datetime.now()
    target_time = now + datetime.timedelta(minutes=62)

    # Get the category by name
    guild = bot.get_guild(guild_id)  # Replace with the actual guild ID
    category_name = "HNM ATTENDANCE"
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        return

    channels = category.channels

    for channel in channels:
        if isinstance(channel, discord.TextChannel) and channel_name in channel.name and all(keyword not in channel.name for keyword in ss.ignore_channels):
            async for message in channel.history(limit=1, oldest_first=True):
                # Extract the UTC timestamp
                utc_start = message.content.find("<t:")
                utc_end = message.content.find(":T>")
                if utc_start != -1 and utc_end != -1:
                    utc = message.content[utc_start + 3:utc_end]
                    dt = datetime.datetime.fromtimestamp(int(utc))

                    # Calculate the delay until the target time
                    delay = dt - now
                    # Send a "hi" message every 10 minutes until 62 minutes have passed
                    if delay.total_seconds() > 0:
                        await asyncio.sleep(delay.total_seconds())
                    w = 1
                    while now < target_time and w <= 7:
                        async for message in channel.history(limit=None):
                            if message.content.lower() in ["kill", "pop", "claim", "ours"]:
                                # Stop the window manager loop
                                print("Loops Broken")
                                return await calculate_DKP(channel, channel_name, w - 1)

                        await channel.send(f"-------------- Window {w} is now --------------")
                        w += 1
                        await asyncio.sleep(10 * 60)  # 10 minutes delay
                        now = datetime.datetime.now()
                    # break
                    return await calculate_DKP(channel, channel_name, w - 1)

# Build this function out to handle calculating dkp and listen for late x's in the channel
async def calculate_DKP(channel, channel_name, w):
    print("Work in progress, maybe....we'll see.")
    channel.send("~fin")
    # messages = []
    # authors_without_number = set()

    # async for message in channel.history(limit=None, oldest_first=True):
    #     if message.author.name != 'wd-tod':
    #         if 'o' in message.content and not any(char.isdigit() for char in message.content):
    #             messages.append((message.author.display_name, message.content))
    #             authors_without_number.add(message.author.display_name)

    # df = pd.DataFrame(messages, columns=['author', 'message'])

    # # Sort the DataFrame by 'author' and 'message'
    # df_sorted = df.sort_values(['author', 'message'])

    # print(df_sorted)
    # print("Authors without a number following 'o':")
    # for author in authors_without_number:
    #     print(author)

async def handle_hnm_command(ctx, hnm, hq, day: int, timestamp):
    original_hnm = hnm  # Store the original HNM name

    if hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
        hnm = "GroundKings"


    day = int(day) + 1


    channel_id = hnm_times
    channel = bot.get_channel(channel_id)
    bot_channel = bot.get_channel(bot_commands)

    # Error handling when user doesnt enter a time after the day.
    if timestamp == None:
        await ctx.author.send(f"No date/time provided for {original_hnm}.\nPlease resend the command in {bot_channel.metion}")
    # List of accepted date formats
    date_formats = ["%Y-%m-%d %H%M%S", "%Y%m%d %H%M%S", "%y%m%d %H%M%S", "%m%d%Y %H%M%S", "%m%d%Y %H%M%S"]
    time_formats = ["%H%M%S", "%H:%M:%S", "%h:%M:%S"]
    # Current date
    current_date = datetime.date.today()

    # Check if the provided timestamp matches any of the accepted formats
    valid_format = False
    parsed_datetime = None
    for date_format in date_formats:
        try:
            # Try parsing the timestamp with the current format
            parsed_datetime = datetime.datetime.strptime(timestamp, date_format)
            valid_format = True
            break
        except ValueError:
            pass

    # If the timestamp does not match any accepted formats, try parsing with the '%H%M%S' format
    if not valid_format:
        for time_format in time_formats:
            try:
                # Try parsing the timestamp with the current format
                parsed_time = datetime.datetime.strptime(timestamp, time_format).time()
                parsed_datetime = datetime.datetime.combine(current_date, parsed_time)
                valid_format = True
                break
            except ValueError:
                pass

    if valid_format:
        # Check if the parsed datetime is in the future
        if parsed_datetime > datetime.datetime.now():
            # Subtract one day from the current date
            current_date -= datetime.timedelta(days=1)

        # Combine the current date (or previous day) with the parsed time
        parsed_datetime = datetime.datetime.combine(current_date, parsed_datetime.time())

        # Convert the parsed datetime to a Unix timestamp
        unix_timestamp = int(parsed_datetime.timestamp())
    else:
        # Invalid timestamp format provided
        await ctx.author.send(f"Incorrect timestamp format for {original_hnm}.\nPlease resend the command in {bot_channel.mention}")
        print("Invalid timestamp format")


    # parse_date = datetime.datetime.strptime(timestamp, date_format)
    # unix_timestamp = int(time.mktime(parse_date.timetuple()))

    try:
        if original_hnm in ["Fafnir", "Adamantoise", "Behemoth", "King Arthro"]:
            unix_timestamp += (22 * 3600)  # Add 22 hours for GroundKings and KA
        else:
            unix_timestamp += (21 * 3600)  # Add 21 hours for other HNMs
    except (ValueError, OverflowError):
        await ctx.author.send("Invalid date or time format provided.\nAccepted Formats:\nyyyy-mm-dd/yyyymmdd/yymmdd\nhh:mm:ss/hhmmss\nAny combination of the 2.")
        return

    async for message in channel.history(limit=None):
        if message.author == bot.user and message.content.startswith(f"- {original_hnm}"):
            await message.delete()

    if unix_timestamp:
        if original_hnm not in ["Fafnir", "Adamantoise", "Behemoth"]:
            await channel.send(f"- {original_hnm}: <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
        else:
            if int(day) == 8: # Force HQ pop on day 8
                await channel.send(f"- {hq} (**{day}**): <t:{unix_timestamp}:T> <t:{unix_timestamp}:R>")
            elif int(day) >= 4: # Possible HQ or NQ day 4-7
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