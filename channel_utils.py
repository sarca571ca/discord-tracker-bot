import discord
import pytz
import asyncio

from discord.ext import commands
from datetime import datetime

import config
from string_utils import load_settings, calculate_time_diff, log_print

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Settings
ss = load_settings()
guild_id = ss['guild']                         # Replace with your guild ID
hnm_times =  ss['hnm_times']                   # Replace with the HNM TIMES channel ID
bot_commands = ss['bot_commands']              # Replace with bot-commands channel ID
dkp_review_category_name = "DKP REVIEW"
hnm_att_category_name = "HNM ATTENDANCE"
att_arch_category_name = "ATTENDANCE ARCHIVE"
time_zone = pytz.timezone('America/Los_Angeles')

async def warn_ten(channel_name, category):
    now = datetime.now()

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
        log_print(f"Warn Ten: Task for channel {channel_name} was cancelled.")

async def window_manager(channel_name, category, guild):
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
                                poptask = asyncio.create_task(calculate_DKP(guild, channel, channel_name, dt, utc))
                                poptask.set_name(f"pop-{channel_name}")
                                task_name = poptask.get_name()
                                log_print(f"Pop: Task for {task_name} has been started.")
                                config.running_tasks.append(task_name)
                            else:
                                await channel.send(f"------------------- Window {window} is now ------------------")
                                await asyncio.sleep(5)
                        await asyncio.sleep(1)
                        time_diff = int(datetime.now().timestamp()) - unix_target

                    poptask = asyncio.create_task(calculate_DKP(guild, channel, channel_name, dt, utc))
                    poptask.set_name(f"pop-{channel_name}")
                    task_name = poptask.get_name()
                    log_print(f"Pop: Task for {task_name} has been started.")
                    config.running_tasks.append(task_name)
    except asyncio.CancelledError:
        log_print(f"Window Manager: Task for channel {channel_name} was cancelled.")


async def calculate_DKP(guild, channel, channel_name, dt, utc):
    dkp_review_category = discord.utils.get(guild.categories, name=dkp_review_category_name)
    existing_task = asyncio.all_tasks()

    process_dict = {
        "id": channel.id,
        "utc": utc,
        "processed": True
    }
    config.processed_channels_list.append(process_dict)

    for task in existing_task:
        if task.get_name() == f"wm-{channel_name}" or task.get_name() == f"wt-{channel_name}":
            task.cancel()
            log_print(f"Calc DKP: WM/WT-Task for channel {channel_name} was completed.")

    await channel.send("Moving channel for dkp review in 5 minutes.")
    await asyncio.sleep(300)
    await channel.edit(category=dkp_review_category)
    await channel.send("--------------------- DKP Review ---------------------")

    for task in existing_task:
        if task.get_name() == f"pop-{channel_name}" or task.get_name() == f"close-{channel_name}":
            task.cancel()
            log_print(f"Calc DKP: Pop-Task for channel {channel_name} was completed.")


async def start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name):
    channel = await guild.create_text_channel(channel_name, category=category, topic=f"<t:{utc}:T> <t:{utc}:R>")
    await channel.edit(position=hnm_times_channel.position + 1)
    await channel.send(f"{hnm_name}")
    await channel.send(f"@everyone First window in {ss['make_channel']}-Minutes")
    wttask = asyncio.create_task(warn_ten(channel_name, category))
    wttask.set_name(f"wt-{channel_name}")
    task_name = wttask.get_name()
    log_print(f"Warn Ten: Task for {task_name} has been started.")
    config.running_tasks.append(task_name)
    wmtask = asyncio.create_task(window_manager(channel_name, category, guild))
    wmtask.set_name(f"wm-{channel_name}")
    task_name = wmtask.get_name()
    log_print(f"Window Manager: Task {task_name} has been started.")
    config.running_tasks.append(task_name)

async def restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel):
    if time_diff >= 0 and time_diff <= 3900 and not config.processed_channels_list:
        wmtask = asyncio.create_task(window_manager(channel_name, category, guild))
        wmtask.set_name(f"wm-{channel_name}")
        task_name = wmtask.get_name()
        log_print(f"Window Manager: Task {task_name} has been started.")
        config.running_tasks.append(task_name)
    else:
        processed_id = False
        for entry in config.processed_channels_list:
            if existing_channel.id == entry["id"]:
                processed_id = True
                break

        if time_diff >= 0 and time_diff <= 3900 and not processed_id:
            wmtask = asyncio.create_task(window_manager(channel_name, category, guild))
            wmtask.set_name(f"wm-{channel_name}")
            task_name = wmtask.get_name()
            log_print(f"Window Manager: Task {task_name} has been started.")
            config.running_tasks.append(task_name)

async def close_manager(channel_name, category, guild):
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
                            if "shi" in channel.name:
                                poptask = asyncio.create_task(calculate_DKP(guild, channel, channel_name, dt, utc))
                                poptask.set_name(f"pop-{channel_name}")
                                task_name = poptask.get_name()
                                log_print(f"Pop: Task for {task_name} has been started.")
                                config.running_tasks.append(task_name)
                            else:
                                await asyncio.sleep(5)
                        await asyncio.sleep(1)
                        time_diff = int(datetime.now().timestamp()) - unix_target

                    poptask = asyncio.create_task(calculate_DKP(guild, channel, channel_name, dt, utc))
                    poptask.set_name(f"pop-{channel_name}")
                    task_name = poptask.get_name()
                    log_print(f"Pop: Task for {task_name} has been started.")
                    config.running_tasks.append(task_name)
    except asyncio.CancelledError:
        log_print(f"Window Manager: Task for channel {channel_name} was cancelled.")
