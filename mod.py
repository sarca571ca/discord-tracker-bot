import discord
from discord.ext import commands
import time
import datetime
import re

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)
# Variables for the server
guild_id = 876434275661135982  # Replace with your guild ID
hnm_times = 1110052586561744896 # Replace with the HNM TIMES channel ID

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

    channel_id = hnm_times
    channel = bot.get_channel(channel_id)

    date_format = "%Y%m%d %H%M%S"
    parse_date = datetime.datetime.strptime(timestamp, date_format)
    unix_timestamp = int(time.mktime(parse_date.timetuple()))

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
