import discord
from discord.ext import commands
import time
import datetime

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


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

bot.run('MTExMDM3NjUyNjgwMjg1Mzk3OQ.GxNguG.7r2bQPC8w-USwXEb0VCUKS-gk85266IBF-XcWM') # wd-tod token