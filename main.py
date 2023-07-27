import discord
import time
import asyncio
import pytz
import asyncio

from datetime import datetime, timezone
from discord.ext import commands, tasks

import config
from string_utils import ref, load_settings, calculate_time_diff, log_print
from channel_utils import calculate_DKP, close_manager, restart_channel_tasks
from command_utils import handle_hnm_command, sort_hnm_times_channel, get_channels, process_hnm_window, archive_channels

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
    guild = bot.get_guild(guild_id)
    category = discord.utils.get(guild.categories, name=hnm_att_category_name)
    hnm_times_channel = bot.get_channel(hnm_times)

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

                await process_hnm_window(hnm_window_end, target_time, hnm, hnm_time, date,
                                         day, message, guild, category, utc, hnm_times_channel,
                                         hnm_name, time_diff)
            pass
    except discord.errors.DiscordServerError as e:
        if e.code == 0 and e.status == 503:
            log_print("Service Unavailable error. Retrying in 60 seconds...")
            await asyncio.sleep(60)
            create_channel_task.start()
        else:
            log_print(f"DiscordServerError: {e}")
    except Exception as e:
        log_print(f"Error: {e}")


@tasks.loop(hours=24)
async def delete_old_channels():
    try:
        archive_category = discord.utils.get(bot.guilds[0].categories, name=att_arch_category_name)
        if archive_category:
            for channel in archive_category.channels:
                if isinstance(channel, discord.TextChannel):
                    now = datetime.now(timezone.utc)
                    if (now - channel.created_at).days >= ss['archive_wait']:
                        await archive_channels(archive_category, channel, archive_category, option="delete")
        pass
    except discord.errors.DiscordServerError as e:
        if e.code == 0 and e.status == 503:
            log_print("Service Unavailable error. Retrying in 60 seconds...")
            await asyncio.sleep(60)
            delete_old_channels.start()
        else:
            log_print(f"DiscordServerError: {e}")
    except Exception as e:
        log_print(f"Error: {e}")

@bot.event
async def on_ready():
    log_print(f"Logged in as {bot.user.name}")
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
        log_print(f"Display name set to: {display_name}")

@bot.command(aliases=["faf", "fafnir"])
async def Fafnir(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Fafnir", "Nidhogg", day, timestamp, channel, bot_channel, bot.user)
Fafnir.brief = f"Used to set the ToD of Fafnir/Nidhogg."
Fafnir.usage = "<day> <timestamp>"

@bot.command(aliases=["ad", "ada", "adam", "adamantoise"])
async def Adamantoise(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Adamantoise", "Aspidochelone", day, timestamp, channel, bot_channel, bot.user)
Adamantoise.brief = f"Used to set the ToD of Adamantoise/Aspidochelone."
Adamantoise.usage = "<day> <timestamp>"

@bot.command(aliases=["be", "behe", "behemoth"])
async def Behemoth(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Behemoth", "King Behemoth", day, timestamp, channel, bot_channel, bot.user)
Behemoth.brief = f"Used to set the ToD of Behemoth/King Behemoth."
Behemoth.usage = "<day> <timestamp>"

@bot.command(aliases=["ka", "kinga"])
async def KingArthro(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "King Arthro", None, day, timestamp, channel, bot_channel, bot.user)
KingArthro.brief = f"Used to set the ToD of King Arthro."
KingArthro.usage = "<day> <timestamp>"

@bot.command(aliases=["sim"])
async def Simurgh(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Simurgh", None, day, timestamp, channel, bot_channel, bot.user)
Simurgh.brief = f"Used to set the ToD of Simurgh."
Simurgh.usage = "<day> <timestamp>"

@bot.command(aliases=["shi", "shiki", "shikigami"])
async def ShikigamiWeapon(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Shikigami Weapon", None, day, timestamp, channel, bot_channel, bot.user)
ShikigamiWeapon.brief = f"Used to set the ToD of Shikigami Weapon."
ShikigamiWeapon.usage = "<day> <timestamp>"

@bot.command(aliases=["kv", "kingv", "kingvine"])
async def KingVinegarroon(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "King Vinegarroon", None, day, timestamp, channel, bot_channel, bot.user)
KingVinegarroon.brief = f"Used to set the ToD of King Vinegarroon."
KingVinegarroon.usage = "<day> <timestamp>"

@bot.command(aliases=["vrt", "vrtr", "vrtra"])
async def Vrtra(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Vrtra", None, day, timestamp, channel, bot_channel, bot.user)
Vrtra.brief = f"Used to set the ToD of Vrtra."
Vrtra.usage = "<day> <timestamp>"

@bot.command(aliases=["tia", "tiam", "tiamat"])
async def Tiamat(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Tiamat", None, day, timestamp, channel, bot_channel, bot.user)
Tiamat.brief = f"Used to set the ToD of Tiamat."
Tiamat.usage = "<day> <timestamp>"

@bot.command(aliases=["jor", "jorm", "jormungand"])
async def Jormungand(ctx, day: str = commands.parameter(default="Day", description=config.day),
                *, timestamp: str = commands.parameter(default="Timestamp", description=config.timestamp)
                ):
    channel, bot_channel = get_channels(bot, ctx)

    await handle_hnm_command(ctx, "Jormungand", None, day, timestamp, channel, bot_channel, bot.user)
Jormungand.brief = f"Used to set the ToD of Jormungand."
Jormungand.usage = "<day> <timestamp>"

@bot.command()
async def sort(ctx): # Command used to sort the hnm-times
    channel_id = hnm_times
    channel = bot.get_channel(channel_id)

    await sort_hnm_times_channel(channel, bot.user)

@bot.command(name='pop')
async def pop(ctx):
    async for message in ctx.channel.history(limit=1, oldest_first=True):
        if message.content.startswith("- "):
            dt, utc = calculate_time_diff(message.content)

    if isinstance(ctx.channel.name, discord.TextChannel):
        log_print(f"Pop: Channel {ctx.channel.name} is not a text channel. Ignoring.")
        return

    if not ctx.channel.category or ctx.channel.category.name != hnm_att_category_name:
        log_print(f"Pop: Channel {ctx.channel.name} is not in {hnm_att_category_name} category. Ignoring.")
        return

    if ctx.author.bot:
        log_print("Pop: Bot user issued command. Ignoring.")
        return
    for entry in config.processed_channels_list:
        if ctx.channel.id == entry["id"]:
            log_print(f"Pop: {ctx.channel.name} has already been processed. Ignoring.")
            return

    await ctx.message.delete()
    log_print(f"Pop: {ctx.author.display_name} issued !pop command.")
    await ctx.channel.send(f"------------------------- POP ------------------------")
    poptask = asyncio.create_task(calculate_DKP(ctx.guild, ctx.channel, ctx.channel.name, dt, utc))
    poptask.set_name(f"pop-{ctx.channel.name}")
    task_name = poptask.get_name()
    log_print(f"Pop: Task for {task_name} has been started.")
    config.running_tasks.append(task_name)
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

    config.processed_channels_list.append(process_dict)
    await ctx.message.delete()
    await ctx.send("----------------------- Closed -----------------------")
    log_print(f"Close: {ctx.author.display_name} closed {ctx.channel.name}.")
    closetask = asyncio.create_task(close_manager(ctx.channel.name, ctx.channel.category, ctx.guild))
    closetask.set_name(f"close-{ctx.channel.name}")
    task_name = closetask.get_name()
    log_print(f"Close: Task for {task_name} has been started.")
    config.running_tasks.append(task_name)
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
        elif task.get_name() == f"close-{ctx.channel.name}":
            task.cancel()
            log_print(f"Open: Close-Task for channel {ctx.channel.name} was cancelled.")

    if not task_running:
        process_dict = {
            "id": ctx.channel.id,
            "utc": utc,
            "processed": False
        }

        config.processed_channels_list.remove(process_dict)
        await ctx.message.delete()
        await ctx.send("---------------------- Open x-in ---------------------")
        log_print(f"Open: {ctx.author.display_name} opened {ctx.channel.name}.")
        async for message in ctx.channel.history(limit=None, oldest_first=True):
            if message.content.startswith("- "):
                dt, utc = calculate_time_diff(message.content)
                unix_now = int(datetime.now().timestamp())
                unix_target = int(dt.timestamp())
                time_diff = unix_now - unix_target
                await restart_channel_tasks(ctx.guild, ctx.channel.name, ctx.channel.category, time_diff, ctx.channel)
open.brief = f"Used to close channels."
open.usage = ""



@bot.command() # Archive command used for moving channels from DKP Review Category
async def archive(ctx, option=None):
    channel = ctx.channel
    category = ctx.channel.category
    archive_category = discord.utils.get(ctx.guild.categories, name=att_arch_category_name)

    if not category or category.name != dkp_review_category_name:
        await ctx.send("The command can only be used in the 'DKP REVIEW' category.")
        return

    await archive_channels(archive_category, channel, category, option)

bot.run(bot_id)