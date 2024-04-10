import discord.utils
import asyncio

from src import settings, channelutil, timeutil

class HandleHNM:

    def __init__(self, bot):
        self.bot = bot
    # Turn this garbage into a loop, it looks so bad
    async def find(self, ctx, cmd, day: int, mod: str, timestamp):
        if cmd in settings.FAFNIR:
            await HandleHNM.process(self.bot, ctx, 'Fafnir', day, mod, timestamp)
        elif cmd in settings.ADAMANTOISE:
            await HandleHNM.process(self.bot, ctx, 'Adamantoise', day, mod, timestamp)
        elif cmd in settings.BEHEMOTH:
            await HandleHNM.process(self.bot, ctx, 'Behemoth', day, mod, timestamp)
        elif cmd in settings.KA:
            await HandleHNM.process(self.bot, ctx, 'King Arthro', day, mod, timestamp)
        elif cmd in settings.SHIKI:
            await HandleHNM.process(self.bot, ctx, 'Shikigami Weapon', day, mod, timestamp)
        elif cmd in settings.SIM:
            await HandleHNM.process(self.bot, ctx, 'Simurgh', day, mod, timestamp)
        elif cmd in settings.KV:
            await HandleHNM.process(self.bot, ctx, 'King Vinegarroon', day, mod, timestamp)
        elif cmd in settings.TIAMAT:
            await HandleHNM.process(self.bot, ctx, 'Tiamat', day, mod, timestamp)
        elif cmd in settings.VRTRA:
            await HandleHNM.process(self.bot, ctx, 'Vrtra', day, mod, timestamp)
        elif cmd in settings.JORM:
            await HandleHNM.process(self.bot, ctx, 'Jormungand', day, mod, timestamp)

    async def process(self, ctx, hnm, day, mod, timestamp):

        channel = self.get_channel(settings.HNMTIMES)
        day = int(day) + 1
        unix_timestamp = timeutil.Time.parse_time(hnm, timestamp)

        channel_util = channelutil.ChannelUtil(self)
        await channel_util.remove(hnm, channel)
        await channel_util.add(hnm, day, mod, unix_timestamp, channel)

    async def process_hnm_window(hnm_window_end, target_time, hnm, hnm_time, date,
                             day, message, guild, category, utc, hnm_times_channel,
                             hnm_name, time_diff):
        hnm_category = discord.utils.get(guild.categories, id=settings.HNMCATEGORYID)
        if hnm_window_end >= target_time:
            if hnm_time <= target_time:
                if any(keyword in message.content for keyword in ["Fafnir", "Adamantoise", "Behemoth"]):
                    channel_name = f"{date}-{hnm}{day}".lower()
                else:
                    channel_name = f"{date}-{hnm}".lower()

                existing_channel = discord.utils.get(guild.channels, name=channel_name)
                if existing_channel:
                    async for message in existing_channel.history(limit=1, oldest_first=True):
                        channel_utc, channel_dt = timeutil.Time.strip_timestamp(message)
                    if channel_utc == utc and category != hnm_category:
                        return
                    elif channel_utc == utc and category == hnm_category:
                        await asyncio.sleep(5)
                        for task in asyncio.all_tasks():
                            if task.get_name() == f"wm-{channel_name}":
                                break
                        else:
                            if existing_channel.category == hnm_category:
                                await channelutil.ChannelUtil.restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel)
                    else:
                        channel_name = f"{channel_name}1"
                        existing_channel = discord.utils.get(guild.channels, name=channel_name)
                        if existing_channel:
                            await asyncio.sleep(5)
                            for task in asyncio.all_tasks():
                                if task.get_name() == f"wm-{channel_name}":
                                    break
                            else:
                                if str(existing_channel.category_id) == hnm_category:
                                    await channelutil.ChannelUtil.restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel)
                        else:
                            await channelutil.ChannelUtil.start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)
                else:
                    await channelutil.ChannelUtil.start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name)
