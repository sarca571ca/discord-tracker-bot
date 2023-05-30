import discord
from discord.ext import commands, tasks
import time
import datetime
import re
import serversettings

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)
# Variables for the server
guild_id = 1111122500038967316  # Replace with your guild ID
hnm_times = 1111122932379422877 # Replace with the HNM TIMES channel ID
bot_id = serversettings.wd_dkp_bot
@tasks.loop(minutes=1)
async def create_channel_task():
    category_name = "HNM ATTENDANCE"
    hnm_times_channel_id = hnm_times
    executed_channels = set()

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
            channel_name = message.content[2:7].strip()

            # Extract the day
            day_start = message.content.find("(")
            day_end = message.content.find(")")
            if day_start != -1 and day_end != -1:
                raw_day = message.content[day_start + 1:day_end].strip()
                day = ref(raw_day)

            # Extract UTC timestamp
            utc_start = message.content.find("<t:")
            utc_end = message.content.find(":T>")
            if utc_start != -1 and utc_end != -1:
                utc = int(message.content[utc_start + 3:utc_end])
                dt = datetime.datetime.utcfromtimestamp(utc)
                date = dt.strftime("%b%d").lower()
                hnm = channel_name.upper()
                hnm_name = message.content[:message.content.find("(")].strip()

                # Subtract 10 minutes from the posted time and compare it to target_time
                hnm_time = datetime.datetime.fromtimestamp(utc - (30 * 60))

                # Create the channel inside the category with the calculated time
                if hnm_time <= target_time:
                    channel_name = f"{date}-{hnm}{day}".lower()
                    existing_channel = discord.utils.get(guild.channels, name=channel_name)

                    if not existing_channel:
                        channel = await guild.create_text_channel(channel_name, category=category)
                        await channel.edit(position=hnm_times_channel.position + 1)
                        await channel.send(f"@everyone First window in 30-Minutes {hnm_name}")

                        if channel.id not in executed_channels:
                            await channel.send("Window in 10-Minutes 'x' in.\n----------------------------------------------------")
                            executed_channels.add(channel.id)

@tasks.loop(hours=1)
async def move_for_review():
    target_channel_id = hnm_times  # Replace with your target channel ID
    dkp_review_category_name = "DKP REVIEW"  # Replace with the name of your DKP review category

    guild = bot.get_guild(guild_id)
    target_channel = bot.get_channel(target_channel_id)
    dkp_review_category = discord.utils.get(guild.categories, name=dkp_review_category_name)

    now = int(time.time())
    target_time = datetime.datetime.fromtimestamp(now)

    async for message in target_channel.history(limit=None, oldest_first=True):
        if message.content.startswith("-"):
            channel_name = message.content[2:7].strip()

            # Extract the day
            day_start = message.content.find("(")
            day_end = message.content.find(")")
            if day_start != -1 and day_end != -1:
                raw_day = message.content[day_start + 1:day_end].strip()
                day = ref(raw_day)

            # Extract UTC timestamp
            utc_start = message.content.find("<t:")
            utc_end = message.content.find(":T>")
            if utc_start != -1 and utc_end != -1:
                utc = int(message.content[utc_start + 3:utc_end])
                dt = datetime.datetime.utcfromtimestamp(utc)
                date = dt.strftime("%b%d").lower()
                hnm = channel_name.upper()

                # Addding 4 hours to compare to the target_time
                hnm_time = datetime.datetime.fromtimestamp(utc + (4 * 3600))

                # Move channels if 4 hours has passed the hnm camp time
                if not hnm_time >= target_time:
                    channel_name = f"{date}-{hnm}{day}".lower()
                    existing_channel = discord.utils.get(guild.channels, name=channel_name)
                    if existing_channel:
                        await existing_channel.edit(category=dkp_review_category)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    create_channel_task.start()
    move_for_review.start()

@bot.event
async def on_message(message):
    if message.channel.name == 'bot-commands':
        await message.delete()

    await bot.process_commands(message)

# This is a test mob to help with testing
@bot.command(aliases=["t"])
async def test(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "Test", day, timestamp)

@bot.command(aliases=["faf", "fafnir"])
async def Fafnir(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "Fafnir", day, timestamp)

@bot.command(aliases=["ad", "ada", "adam", "adamantoise"])
async def Adamantoise(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "Adamantoise", day, timestamp)

@bot.command(aliases=["be", "behe", "behemoth"])
async def Behemoth(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "Behemoth", day, timestamp)

@bot.command(aliases=["ka", "kinga"])
async def KingArthro(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "King Arthro", day, timestamp)

@bot.command(aliases=["sim"])
async def Simurgh(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "Simurgh", day, timestamp)

@bot.command(aliases=["shi", "shiki", "shikigami"])
async def ShikigamiWeapon(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "Shikigami Weapon", day, timestamp)

@bot.command(aliases=["kv", "kingv", "kingvine"])
async def KingVinegarroon(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "King Vinegarroon", day, timestamp)

@bot.command(aliases=["vrt", "vrtr", "vrtra"])
async def Vrtra(ctx, day, *, timestamp):
    await handle_hnm_command(ctx, "Vrtra", day, timestamp)

# Various command tools to help testing/management of the bot
# Deletes all messages in the channel of the command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearch(ctx):
    channel = ctx.channel
    await ctx.message.delete()  # Delete the command message

    deleted_messages = 0
    async for message in channel.history(limit=None):
        await message.delete()
        deleted_messages += 1

    print(f'Deleted {deleted_messages} messages in {channel.name}')

# Deletes all channels except target_channel_ids. Used for testing only removed before production.
@bot.command()
async def rc(ctx):
    guild = ctx.guild
    category_name = "HNM ATTENDANCE"
    target_channel_ids = [1110076161201020949, 1110052586561744896]  # Replace with the actual channel IDs

    # Check if the category exists
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        await ctx.send("Category does not exist.")
        return

    # Get all channels in the category
    channels = category.channels

    # Remove channels that are not in the target channel IDs
    channels_to_remove = [channel for channel in channels if channel.id not in target_channel_ids]

    for channel in channels_to_remove:
        await channel.delete()

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

# Helpers can probably move these to a module later on for readability
async def handle_hnm_command(ctx, hnm, day, timestamp):
    original_hnm = hnm  # Store the original HNM name

    if hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
        hnm = "GroundKings"

    channel_id = hnm_times
    channel = bot.get_channel(channel_id)

    # date_format = "%Y%m%d %H%M%S"

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
        print("Invalid timestamp format")

    # parse_date = datetime.datetime.strptime(timestamp, date_format)
    # unix_timestamp = int(time.mktime(parse_date.timetuple()))

    try:
        if original_hnm in ["Fafnir", "Adamantoise", "Behemoth", "King Arthro"]:
            unix_timestamp += (22 * 3600)  # Add 22 hours for GroundKings
        else:
            unix_timestamp += (21 * 3600)  # Add 21 hours for other HNMs
    except (ValueError, OverflowError):
        await ctx.author.send("Invalid date or time format provided.\nAccepted Formats:\nyyyy-mm-dd/yyyymmdd/yymmdd\nhh:mm:ss/hhmmss\nAny combination of the 2.")
        return

    async for message in channel.history(limit=None):
        if message.author == bot.user and message.content.startswith(f"- {original_hnm}"):
            await message.delete()

    if unix_timestamp:
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

bot.run(bot_id) # wd-dkp-bot