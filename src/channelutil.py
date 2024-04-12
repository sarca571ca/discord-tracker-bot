import asyncio
import os
import discord
import pandas as pd
import aiofiles
from src import settings, timeutil, stringutil

log_print = stringutil.StringUtil.log_print

class Times:

    def __init__(self, bot) -> None:
        self.bot = bot

    async def remove(self, hnm, channel):

        async for message in channel.history(limit=None):
            if message.author == self.bot.user and message.content.startswith(f"- {hnm}") or message.content.startswith(f"- **{hnm}"):
                await message.delete()

    async def add(self, hnm, day, mod, timestamp, channel):
        hnm_list = settings.ALL_HNMS[mod]

        for h in hnm_list:
            if h == hnm:
                day_split = hnm_list[hnm][-7:]
                if day_split == '(****):':
                    if day >= 4:
                        hq = settings.HQ[hnm]
                        msg = hnm_list[hnm][:-7]
                        await channel.send(f'- **{hnm}/{hq}** :rotating_light:{msg}{day_split[:3]}{day}{day_split[3:]} <t:{timestamp}:T> <t:{timestamp}:R>')
                    else:
                        msg = hnm_list[hnm][:-7]
                        await channel.send(f'- {hnm} {msg}{day_split[:3]}{day}{day_split[3:]} <t:{timestamp}:T> <t:{timestamp}:R>')
                else:
                    msg = hnm_list[hnm]
                    await channel.send(f'- {hnm} {msg} <t:{timestamp}:T> <t:{timestamp}:R>')
        await Times.sort_timers_channel(self, channel)

    async def sort_timers_channel(self, channel):
        messages = []

        async for message in channel.history(limit=None):
            if message.author == self.bot.user:
                messages.append(message)

        messages.sort(key=lambda m: timeutil.Time.strip_timestamp(m))

        for message in messages:
            await message.delete()
            timestamp, dt = timeutil.Time.strip_timestamp(message)
            unix_now = timeutil.Time.now()
            unix_target = int(dt.timestamp())
            time_diff = unix_now - unix_target
            if any(keyword in message.content for keyword in ['Jormungand', 'Tiamat', 'Vrtra']) and time_diff > 86400 * 3:
                continue
            if not any(keyword in message.content for keyword in ['Jormungand', 'Tiamat', 'Vrtra']) and time_diff > 86400:
                continue
            else:
                await channel.send(message.content)

class Tasks:

    def __init__(self) -> None:
        pass

    # Looks kinda sloppy let's looksat this latter to clean it up some. Can even setup the restart channel
    # tasks to inherit some of this funcstions stuff to reduce bloat. I think i have to make it a class :/
    async def start_channel_tasks(guild, channel_name, category, utc, hnm_name):
        channel = await guild.create_text_channel(channel_name, category=category, topic=f"<t:{utc}:T> <t:{utc}:R>")
        category_channels = category.text_channels
        last_channel = category_channels[-1]
        await channel.edit(position=last_channel.position + 1)
        await channel.send(f"{hnm_name}")

        for name in settings.HNMINFO:
            if name in channel_name:
                await channel.send(settings.HNMINFO[name])
        if 'shi' in channel_name:
            with open('images/shiki.png', 'rb') as f:
                picture = discord.File(f)
                await channel.send(file=picture)

        wttask = asyncio.create_task(Tasks.warn_ten(channel_name, category))
        wttask.set_name(f"wt-{channel_name}")
        task_name = wttask.get_name()
        log_print(f"Warn Ten: Task for {task_name} has been started.")
        settings.RUNNINGTASKS.append(task_name)
        wmtask = asyncio.create_task(Manager.window_manager(channel_name, category, guild))
        wmtask.set_name(f"wm-{channel_name}")
        task_name = wmtask.get_name()
        log_print(f"Window Manager: Task {task_name} has been started.")
        settings.RUNNINGTASKS.append(task_name)

    # This is gross with all the if and elif statements....
    async def restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel):
        if any(keyword in channel_name.lower() for keyword in ["jor", "vrt", "tia"]):
            if time_diff >= 0 and time_diff <= (24 * 3600) + 300 and not settings.PROCESSEDLIST:
                wmtask = asyncio.create_task(Manager.window_manager(channel_name, category, guild))
                wmtask.set_name(f"wm-{channel_name}")
                task_name = wmtask.get_name()
                log_print(f"Window Manager: Task {task_name} has been started.")
                settings.RUNNINGTASKS.append(task_name)
            else:
                processed_id = False
                for entry in settings.PROCESSEDLIST:
                    if existing_channel.id == entry["id"]:
                        processed_id = True
                        break

                if time_diff >= 0 and time_diff <= (24 * 3600) + 300 and not processed_id:
                    wmtask = asyncio.create_task(Manager.window_manager(channel_name, category, guild))
                    wmtask.set_name(f"wm-{channel_name}")
                    task_name = wmtask.get_name()
                    log_print(f"Window Manager: Task {task_name} has been started.")
                    settings.RUNNINGTASKS.append(task_name)
        else:
            if time_diff >= 0 and time_diff <= 3900 and not settings.PROCESSEDLIST and not settings.KVOPEN:
                wmtask = asyncio.create_task(Manager.window_manager(channel_name, category, guild))
                wmtask.set_name(f"wm-{channel_name}")
                task_name = wmtask.get_name()
                log_print(f"Window Manager: Task {task_name} has been started.")
                settings.RUNNINGTASKS.append(task_name)
            else:
                processed_id = False
                kv_id = False
                for entry in settings.PROCESSEDLIST:
                    if existing_channel.id == entry["id"]:
                        processed_id = True
                        break
                for entry in settings.KVOPEN:
                    if existing_channel.id == entry["id"]:
                        kv_id = True
                        break
                if time_diff >= 0 and time_diff <= 3900 and not processed_id and not kv_id:
                    wmtask = asyncio.create_task(Manager.window_manager(channel_name, category, guild))
                    wmtask.set_name(f"wm-{channel_name}")
                    task_name = wmtask.get_name()
                    log_print(f"Window Manager: Task {task_name} has been started.")
                    settings.RUNNINGTASKS.append(task_name)

    async def warn_ten(channel_name, category):
        # now = datetime.now() # this is date-time object but i convert to int in timeutil.Time.now() so i should change dt to timestamp?
        now = timeutil.Time.format_time(timeutil.Time.now())

        if not category:
            return

        channels = category.channels
        try:
            for channel in channels:
                if isinstance(channel, discord.TextChannel) and channel_name in channel.name and all(keyword not in channel.name for keyword in ['kv', 'tia', 'vrt', 'jor']):
                    async for message in channel.history(limit=1, oldest_first=True):
                        timestamp, dt = timeutil.Time.strip_timestamp(message)
                        dt = timeutil.Time.format_time(timestamp - (20 *60))
                        delay = dt - now
                        if delay.total_seconds() > 0:
                            await asyncio.sleep(delay.total_seconds())
                        window_in_ten = stringutil.StringUtil.format_window_heading("Window opens in 20 Minutes x-in")
                        await channel.send(window_in_ten)
                        await channel.send(settings.WINDOWMEASSAGE)

                        return
                elif isinstance(channel, discord.TextChannel) and channel_name in channel.name and any(keyword in channel.name for keyword in ["kv"]):
                    async for message in channel.history(limit=1, oldest_first=True):
                        timestamp, dt = timeutil.Time.strip_timestamp(message)
                        dt = timeutil.Time.format_time(timestamp - (20 * 60))
                        delay = dt - now
                        if delay.total_seconds() > 0:
                            await asyncio.sleep(delay.total_seconds())
                        window_in_ten = stringutil.StringUtil.format_window_heading("Window opens in 20 Minutes")
                        await channel.send(window_in_ten)
                        await channel.send(settings.WINDOWMEASSAGE)

                        return
                elif isinstance(channel, discord.TextChannel) and channel_name in channel.name and any(keyword in channel.name for keyword in ["jor", "vrt", "tia"]):
                    async for message in channel.history(limit=1, oldest_first=True):
                        timestamp, dt = timeutil.Time.strip_timestamp(message)
                        dt = timeutil.Time.format_time(timestamp - (20 * 60))
                        delay = dt - now
                        if delay.total_seconds() > 0:
                            await asyncio.sleep(delay.total_seconds())
                        window_in_ten = stringutil.StringUtil.format_window_heading("Window opens in 20 Minutes")
                        await channel.send(window_in_ten)
                        await channel.send(settings.WINDOWMEASSAGE)

                        return
        except asyncio.CancelledError:
            log_print(f"Warn Ten: Task for channel {channel_name} was cancelled.")

class Manager():

    def __init__(self, bot) -> None:
        self.bot = bot
    #!! Too many statements, makes it hard to follow
    async def window_manager(channel_name, category, guild):
        if not category:
            return

        channels = category.channels

        try:
            for channel in channels:
                if isinstance(channel, discord.TextChannel) and channel_name in channel.name:
                    async for message in channel.history(limit=1, oldest_first=True):
                        timestamp, dt = timeutil.Time.strip_timestamp(message)

                        unix_now = timeutil.Time.now()

                        time_diff = unix_now - timestamp
                        sleep_time = timestamp - unix_now
                        gw_time = time_diff + 300
                        gw_sleep_time = (timestamp - unix_now) - 300

                        # Should make a dictionary for window messages and loop through instead of using if statements....
                        if time_diff <= -0 and not any(keyword in channel.name for keyword in ["jor", "vrt", "tia"]):
                            await asyncio.sleep(sleep_time)
                            time_diff = timeutil.Time.now() - timestamp
                        elif  gw_time <= -0 and any(keyword in channel.name for keyword in ["jor", "vrt", "tia"]):
                            await asyncio.sleep(gw_sleep_time)
                            window = round(time_diff / 3600) + 1
                            first_window = stringutil.StringUtil.format_window_heading(f"Window {window} in 5-Minutes x-in")
                            await channel.send(first_window)
                            await channel.send("```Remember a proper hold party is required for DKP \nAll x-in's should be x-job, eg. x-blm```")
                            gw_time = timeutil.Time.now() - timestamp

                        if any(keyword in channel.name for keyword in ["jor", "vrt", "tia"]):
                            while time_diff >= -1200 and time_diff <= (25 * 60 * 60): # 25 windows * 60 minute * 60 seconds = total time in seconds
                                window = round(time_diff / 3600) + 1
                                window_open = time_diff + 300 #300
                                window_close = time_diff - 60 #360
                                if window_open % 3600 == 0:
                                    window_number_open = stringutil.StringUtil.format_window_heading(f"Window {window} in 5-Minutes x-in")
                                    await channel.send(window_number_open)
                                    await channel.send("```Remember a proper hold party is required for DKP \nAll x-in's should be x-job, eg. x-blm```")
                                if window_close % 3600 == 0:
                                    window_number_close = stringutil.StringUtil.format_window_heading(f"Window {window} closed no more x-in")
                                    await channel.send(window_number_close)

                                await asyncio.sleep(1)
                                time_diff = timeutil.Time.now() - timestamp

                                if window == 26:
                                    break

                            poptask = asyncio.create_task(Manager.dkp_review(guild, channel, channel_name, dt, timestamp))
                            poptask.set_name(f"pop-{channel_name}")
                            task_name = poptask.get_name()
                            log_print(f"Pop: Task for {task_name} has been started.")
                            settings.RUNNINGTASKS.append(task_name)
                        elif any(keyword in channel.name for keyword in ["kv"]):
                            if time_diff >= 0 and time_diff <= 3600 and time_diff % 600 == 0:
                                kv_open = stringutil.StringUtil.format_window_heading("King Vinegarroon Window is open")
                                await channel.send(kv_open)

                                existing_task = asyncio.all_tasks()

                                kv_dict = {
                                    "id": channel.id,
                                    "utc": timestamp,
                                    "processed": True
                                }

                                settings.KVOPEN.append(kv_dict)

                                for task in existing_task:
                                    if task.get_name() == f"wm-{channel_name}" or task.get_name() == f"wt-{channel_name}":
                                        task.cancel()
                                        log_print(f"Window Manager: WM/WT-Task for channel {channel_name} was completed.")
                        else:
                            while time_diff >= 0 and time_diff <= 3600:
                                if time_diff % 600 == 0:
                                    window = round(time_diff / 600) + 1
                                    if "shi" in channel.name:
                                        shiki_spawn = stringutil.StringUtil.format_window_heading("Shikigami Weapon has spawned")
                                        await channel.send(shiki_spawn)
                                        poptask = asyncio.create_task(Manager.dkp_review(guild, channel, channel_name, dt, timestamp))
                                        poptask.set_name(f"pop-{channel_name}")
                                        task_name = poptask.get_name()
                                        log_print(f"Pop: Task for {task_name} has been started.")
                                        settings.RUNNINGTASKS.append(task_name)
                                    # elif "kv" in channel.name:
                                    #     kv_open = stringutil.StringUtil.format_window_heading("King Vinegarroon Window is open")
                                    #     await channel.send(kv_open)
                                    else:
                                        window_count = stringutil.StringUtil.format_window_heading(f"Window {window}")
                                        await channel.send(window_count)
                                        await asyncio.sleep(5)
                                await asyncio.sleep(1)
                                time_diff = timeutil.Time.now() - timestamp

                            poptask = asyncio.create_task(Manager.dkp_review(guild, channel, channel_name, dt, timestamp))
                            poptask.set_name(f"pop-{channel_name}")
                            task_name = poptask.get_name()
                            log_print(f"Pop: Task for {task_name} has been started.")
                            settings.RUNNINGTASKS.append(task_name)
        except asyncio.CancelledError:
            log_print(f"Window Manager: Task for channel {channel_name} was cancelled.")

    #!! Dear god save me it's so bad!
    async def close_manager(channel_name, category, guild):
        if not category:
            return

        channels = category.channels

        try:
            for channel in channels:
                if isinstance(channel, discord.TextChannel) and channel_name in channel.name:
                    async for message in channel.history(limit=1, oldest_first=True):
                        timestamp, dt = timeutil.Time.strip_timestamp(message)

                        unix_now = timeutil.Time.now()
                        unix_target = int(dt.timestamp())

                        time_diff = unix_now - unix_target
                        sleep_time = unix_target - unix_now
                        if time_diff <= -0:
                            await asyncio.sleep(sleep_time)
                            time_diff = timeutil.Time.now() - unix_target

                        while time_diff >= 0 and time_diff <= 3600:
                            if time_diff % 600 == 0:
                                if "shi" in channel.name:
                                    poptask = asyncio.create_task(Manager.dkp_review(guild, channel, channel_name, dt, timestamp))
                                    poptask.set_name(f"pop-{channel_name}")
                                    task_name = poptask.get_name()
                                    log_print(f"Pop: Task for {task_name} has been started.")
                                    settings.RUNNINGTASKS.append(task_name)
                                else:
                                    await asyncio.sleep(5)
                            await asyncio.sleep(1)
                            time_diff = timeutil.Time.now() - unix_target

                        poptask = asyncio.create_task(Manager.dkp_review(guild, channel, channel_name, dt, timestamp))
                        poptask.set_name(f"pop-{channel_name}")
                        task_name = poptask.get_name()
                        log_print(f"Pop: Task for {task_name} has been started.")
                        settings.RUNNINGTASKS.append(task_name)
        except asyncio.CancelledError:
            log_print(f"Window Manager: Task for channel {channel_name} was cancelled.")

    async def dkp_review(guild, channel, channel_name, dt, utc):
        existing_task = asyncio.all_tasks()

        process_dict = {
            "id": channel.id,
            "utc": utc,
            "processed": True
        }
        settings.PROCESSEDLIST.append(process_dict)

        for task in existing_task:
            if task.get_name() == f"wm-{channel_name}" or task.get_name() == f"wt-{channel_name}":
                task.cancel()
                log_print(f"Calc DKP: WM/WT-Task for channel {channel_name} was completed.")

        await channel.send("Moving channel for dkp review in 5 minutes.")
        await asyncio.sleep(300)
        category = discord.utils.get(guild.categories, id=settings.DKPREVIEWID)
        await channel.edit(category=category)
        dkp_review = stringutil.StringUtil.format_window_heading("DKP Review")
        await channel.send(dkp_review)

        for task in existing_task:
            if task.get_name() == f"pop-{channel_name}" or task.get_name() == f"close-{channel_name}":
                task.cancel()
                log_print(f"Calc DKP: Pop-Task for channel {channel_name} was completed.")

    async def open(ctx):
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            timestamp, dt = timeutil.Time.strip_timestamp(message)

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
                "utc": timestamp,
                "processed": False
            }

            settings.PROCESSEDLIST.remove(process_dict)
            await ctx.message.delete()
            open_x = stringutil.StringUtil.format_window_heading("Open x-in")
            await ctx.send(open_x)
            log_print(f"Open: {ctx.author.display_name} opened {ctx.channel.name}.")
            async for message in ctx.channel.history(limit=None, oldest_first=True):
                if message.content.startswith("- "):
                    timestamp, dt = timeutil.Time.strip_timestamp(message)
                    unix_now = timeutil.Time.now()
                    unix_target = int(dt.timestamp())
                    time_diff = unix_now - unix_target
                    await Tasks.restart_channel_tasks(ctx.guild, ctx.channel.name, ctx.channel.category, time_diff, ctx.channel)

    async def close(ctx):
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            timestamp, dt = timeutil.Time.strip_timestamp(message)

        existing_task = asyncio.all_tasks()
        for task in existing_task:
            if task.get_name() == f"wm-{ctx.channel.name}" or task.get_name() == f"wt-{ctx.channel.name}":
                task.cancel()

        process_dict = {
            "id": ctx.channel.id,
            "utc": timestamp,
            "processed": False
        }

        settings.PROCESSEDLIST.append(process_dict)
        await ctx.message.delete()
        closed = stringutil.StringUtil.format_window_heading("Closed")
        await ctx.send(closed)
        log_print(f"Close: {ctx.author.display_name} closed {ctx.channel.name}.")
        closetask = asyncio.create_task(Manager.close_manager(ctx.channel.name, ctx.channel.category, ctx.guild))
        closetask.set_name(f"close-{ctx.channel.name}")
        task_name = closetask.get_name()
        log_print(f"Close: Task for {task_name} has been started.")
        settings.RUNNINGTASKS.append(task_name)

    async def pop(ctx, *linkshell):
        if linkshell:
            linkshell = ' '.join(linkshell)
        else:
            linkshell = None

        async for message in ctx.channel.history(limit=1, oldest_first=True):
            timestamp, dt = timeutil.Time.strip_timestamp(message)

        if isinstance(ctx.channel.name, discord.TextChannel):
            log_print(f"Pop: Channel {ctx.channel.name} is not a text channel. Ignoring.")
            return

        if not ctx.channel.category or ctx.channel.category_id != settings.HNMCATEGORYID:
            log_print(f"Pop: Channel {ctx.channel.name} is not in HNM Attendance category. Ignoring.")
            return

        if ctx.author.bot:
            log_print("Pop: Bot user issued command. Ignoring.")
            return
        for entry in settings.PROCESSEDLIST:
            if ctx.channel.id == entry["id"]:
                log_print(f"Pop: {ctx.channel.name} has already been processed. Ignoring.")
                return

        await ctx.message.delete()
        log_print(f"Pop: {ctx.author.display_name} issued !pop command in {ctx.channel.name}.")

        window = await stringutil.StringUtil.find_last_window(ctx)

        channel_name_lower = ctx.channel.name.lower()

        if any(keyword in channel_name_lower for keyword in ["faf", "beh", "ada"]):
            linkshell = linkshell if linkshell else "Linkshell Unknown"
            heading = stringutil.StringUtil.format_window_heading(f"POP: {window} | {linkshell}")
        else:
            heading = stringutil.StringUtil.format_window_heading("POP")

        await ctx.channel.send(heading)

        poptask = asyncio.create_task(Manager.dkp_review(ctx.guild, ctx.channel, ctx.channel.name, dt, timestamp))
        poptask.set_name(f"pop-{ctx.channel.name}")
        task_name = poptask.get_name()
        log_print(f"Pop: Task for {task_name} has been started.")
        settings.RUNNINGTASKS.append(task_name)

    async def archive_channels(archive_category, archive_channel, category, option):
        data_dir = "data"
        backups_dir = "backups"
        category_folder = f"{category}"

        dir_structure = [data_dir, backups_dir, category_folder]

        current_path = ''
        for directory in dir_structure:
            current_path = os.path.join(current_path, directory)
            if not os.path.exists(current_path):
                os.mkdir(current_path)

        log_file_path = os.path.join(current_path, 'log.txt')

        if option == "delete":
            channel = archive_channel
            file_name = os.path.join(current_path, f"{channel.name}.csv")

            data = []
            async for message in channel.history(limit=None, oldest_first=True):
                data.append({
                    "Author": message.author.display_name,
                    "Content": message.content,
                    "Timestamp": message.created_at
                })

            df = pd.DataFrame(data)
            df.to_csv(file_name, index=False)

            log_message = f"Channel '{channel.name}' has been archived at {timeutil.Time.format_time(timeutil.Time.now())}"
            async with aiofiles.open(log_file_path, "a") as file:
                await file.write(log_message + "\n")

            await channel.delete()

        elif option == "all":  # 'all' argument will archive all channels in the category
            channels = category.channels

            for channel in channels:
                if isinstance(channel, (discord.VoiceChannel, discord.CategoryChannel)):
                    continue

                file_name = os.path.join(current_path, f"{channel.name}.csv")

                data = []
                async for message in channel.history(limit=None, oldest_first=True):
                    data.append({
                        "Author": message.author.display_name,
                        "Content": message.content,
                        "Timestamp": message.created_at
                    })

                df = pd.DataFrame(data)
                df.to_csv(file_name, index=False)

                if archive_category:
                    await channel.edit(category=archive_category)
                else:
                    await channel.send("The 'Archive' category does not exist.")

                log_message = f"Channel '{channel.name}' has been archived at {timeutil.Time.format_time(timeutil.Time.now())}"
                async with aiofiles.open(log_file_path, "a") as file:
                    await file.write(log_message + "\n")

        else:
            channel = archive_channel
            file_name = os.path.join(current_path, f"{channel.name}.csv")

            data = []
            async for message in channel.history(limit=None, oldest_first=True):
                data.append({
                    "Author": message.author.display_name,
                    "Content": message.content,
                    "Timestamp": message.created_at
                })

            df = pd.DataFrame(data)
            df.to_csv(file_name, index=False)

            if archive_category:
                await channel.edit(category=archive_category)
            else:
                await channel.send("The 'Archive' category does not exist.")

            log_message = f"Channel '{channel.name}' has been archived at {timeutil.Time.format_time(timeutil.Time.now())}"
            async with aiofiles.open(log_file_path, "a") as file:
                await file.write(log_message + "\n")

    async def sort_channels(ctx):
        if ctx.channel.id != settings.BOTCOMMANDS:
            return

        # Get the guild
        guild = ctx.guild

        # Find the category by name
        category = discord.utils.get(guild.categories, name=settings.DKPREVIEWID)


        # Sort the channels in the category by creation time
        sorted_channels = sorted(category.channels, key=lambda c: c.created_at)

        # Reorder the channels from newest to oldest
        sorted_channels.reverse()
        log_print(f"Sort Channels: {ctx.author.display_name} issued !sort_channels.")
        # Move the channels to the correct positions
        for index, channel in enumerate(sorted_channels):
            await channel.edit(position=index)
            await asyncio.sleep(2)

        log_print("Sort Channels: Complete.")
