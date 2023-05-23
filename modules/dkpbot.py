import discord
from discord.ext import commands, tasks
import time
import datetime
import re

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=1)
async def create_channel_task():
    guild_id = 876434275661135982  # Replace with your guild ID
    category_name = "HNM ATTENDANCE"
    output_channel_id = 1110425188962676786  # Replace with your output channel ID
    hnm_times_channel_id = 1110052586561744896  # Replace with your hnm-times channel ID

    guild = bot.get_guild(guild_id)
    category = discord.utils.get(guild.categories, name=category_name)
    output_channel = bot.get_channel(output_channel_id)
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

                # Subtract 10 minutes from the posted time and compare it to target_time
                hnm_time = datetime.datetime.fromtimestamp(utc - (10 * 60))

                # Create the channel inside the category with the calculated time
                if hnm_time <= target_time:
                    channel_name = f"{date}-{hnm}{day}".lower()
                    existing_channel = discord.utils.get(guild.channels, name=channel_name)

                    if not existing_channel:
                        channel = await guild.create_text_channel(channel_name, category=category,
                                                                  topic="\nPlease x in to have your dkp recorded!")
                        await channel.edit(position=hnm_times_channel.position + 1)

def ref(text):
    # Remove any formatting (e.g., **bold**, *italic*, __underline__, ~~strikethrough~~, etc.)
    pattern = r'(\*\*|\*|__|~~)(.*?)(\*\*|\*|__|~~)'
    stripped_text = re.sub(pattern, r'\2', text)

    return stripped_text

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    create_channel_task.start()

@bot.event
async def on_message(message):
    if message.channel.name == 'bot-commands':
        await message.delete()

    await bot.process_commands(message)


@bot.command(aliases=["faf", "fafnir"])
async def Fafnir(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "Fafnir", day, timestamp)


@bot.command(aliases=["ad", "ada", "adam", "adamantoise"])
async def Adamantoise(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "Adamantoise", day, timestamp)


@bot.command(aliases=["be", "behe", "behemoth"])
async def Behemoth(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "Behemoth", day, timestamp)


@bot.command(aliases=["ka"])
async def KingArthro(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "King Arthro", day, timestamp)


@bot.command(aliases=["sim"])
async def Simurgh(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "Simurgh", day, timestamp)


@bot.command(aliases=["shi", "shiki", "shikigami"])
async def ShikigamiWeapon(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "Shikigami Weapon", day, timestamp)

@bot.command(aliases=["kv", "kingv", "kingvine"])
async def KingVinegarroon(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "King Vinegarroon", day, timestamp)


@bot.command(aliases=["vrt", "vrtr", "vrtra"])
async def Vrtra(ctx, day: str = None, *, timestamp: str = "xx:xx:xx"):
    await handle_hnm_command(ctx, "Vrtra", day, timestamp)

async def handle_hnm_command(ctx, hnm: str, day: str, timestamp: str):
    original_hnm = hnm  # Store the original HNM name

    if hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
        hnm = "GroundKings"

    if day is None:
        await ctx.author.send(f"Please provide the day and timestamp for {original_hnm}:")
        response = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        input_parts = response.content.split(maxsplit=1)
        day = input_parts[0]
        timestamp = input_parts[1]

    channel_id = 1110052586561744896
    channel = bot.get_channel(channel_id)

    date_format = "%Y%m%d %H%M%S"
    parse_date = datetime.datetime.strptime(timestamp, date_format)
    unix_timestamp = int(time.mktime(parse_date.timetuple()))

    try:
        if original_hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
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
    channel_id = 1110052586561744896
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

def get_utc_timestamp(message):
    if "<t:" not in message.content:
        return 0
    timestamp_start = message.content.index("<t:") + 3
    timestamp_end = message.content.index(":T>", timestamp_start)
    timestamp = message.content[timestamp_start:timestamp_end]
    return int(timestamp)

bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos') # wd-dkp-bot
