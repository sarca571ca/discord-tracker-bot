from src import settings, timeutil

class ChannelUtil:

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
                        await channel.send(f'- {hnm}/{hq} :rotating_light:{msg}{day_split[:3]}{day}{day_split[3:]} <t:{timestamp}:T> <t:{timestamp}:R>')
                    else:
                        msg = hnm_list[hnm][:-7]
                        await channel.send(f'- {hnm} {msg}{day_split[:3]}{day}{day_split[3:]} <t:{timestamp}:T> <t:{timestamp}:R>')
                else:
                    msg = hnm_list[hnm]
                    await channel.send(f'- {hnm} {msg} <t:{timestamp}:T> <t:{timestamp}:R>')
        await self.sort_timers_channel(channel)

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
            elif not any(keyword in message.content for keyword in ['Jormungand', 'Tiamat', 'Vrtra']) and time_diff > 86400:
                continue
            else:
                await channel.send(message.content)

    async def start_channel_tasks(guild, channel_name, category, utc, hnm_times_channel, hnm_name):
        pass

    async def restart_channel_tasks(guild, channel_name, category, time_diff, existing_channel):
        pass