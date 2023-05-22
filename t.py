
import asyncio
import discord
from discord.ext import commands, tasks
from dateutil import parser
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
        timestamp = input_parts[1] if len(input_parts) > 1 else "xx:xx:xx"

    channel_id = 1110052586561744896
    channel = bot.get_channel(channel_id)

    try:
        datetime_obj = parser.parse(timestamp)

        utc_timestamp = int(datetime_obj.timestamp())
        if original_hnm in ["Fafnir", "Adamantoise", "Behemoth"]:
            utc_timestamp += (22 * 3600)  # Add 22 hours for GroundKings
        else:
            utc_timestamp += (21 * 3600)  # Add 21 hours for other HNMs
    except (ValueError, OverflowError):
        await ctx.author.send("Invalid date or time format provided.\nAccepted Formats:\nyyyy-mm-dd/yyyymmdd/yymmdd\nhh:mm:ss/hhmmss\nAny combination of the 2.")
        return

    async for message in channel.history(limit=None):
        if message.author == bot.user and message.content.startswith(f"- {original_hnm}"):
            await message.delete()

    if utc_timestamp:
        await channel.send(f"- {original_hnm} (**{day}**): <t:{utc_timestamp}:T> <t:{utc_timestamp}:R>")
    else:
        await channel.send(f"- {original_hnm}")

    await resend(ctx)  # Trigger the resend command after handling the hnm command

# This section isn't working correctly, need to make sure its using the original hnm names maybe?
# review and maybe rewrite the code yourself. It does seem to delete the channel after 10 minutes.
# instead of deleting we need to move the channel to the archive category maybe? not sure about
# this though. explore different options, the channel should alway be able to review. might have
# to add options in the future to allow for DKP adjustments.

@tasks.loop(minutes=1)
async def check_hnm_attendance():
    guild_id = 1110052586561744896  # Replace with your guild ID
    guild = bot.get_guild(guild_id)
    if guild is None:
        return

    category_name = "HNM ATTENDANCE"
    category = discord.utils.get(guild.categories, name=category_name)
    if category is None:
        category = await guild.create_category(category_name)

    current_time = datetime.datetime.utcnow()

    async for channel in category.text_channels:
        parts = channel.name.split("-")
        if len(parts) != 2:
            continue

        utc_timestamp_str, hnm_day = parts
        try:
            utc_timestamp = int(utc_timestamp_str.lower(), base=36)
            hnm_time = datetime.datetime.utcfromtimestamp(utc_timestamp)
            if current_time > hnm_time + datetime.timedelta(minutes=10):
                await channel.delete()
        except ValueError:
            continue


@check_hnm_attendance.before_loop
async def before_check_hnm_attendance():
    await bot.wait_until_ready()

@bot.command()
async def resend(ctx):
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


# async def check_hnm_attendance(ctx, hnm: str, day: str, utc_timestamp: int):
#     guild = ctx.guild

#     category_name = "HNM ATTENDANCE"
#     category = discord.utils.get(guild.categories, name=category_name)
#     if category is None:
#         category = await guild.create_category(category_name)

#     channel_name = f"May23{hnm}{day}"
#     new_channel = await category.create_text_channel(channel_name)

#     # Calculate the time when the new channel should be created (10 minutes before the HNM)
#     creation_time = datetime.datetime.utcfromtimestamp(utc_timestamp) - datetime.timedelta(minutes=10)

#     # Wait until the creation time and then delete the channel
#     await asyncio.sleep((creation_time - datetime.datetime.utcnow()).total_seconds())
#     await new_channel.delete()

bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos')
