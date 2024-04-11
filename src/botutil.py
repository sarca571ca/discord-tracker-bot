import subprocess
from src import stringutil, timeutil, hnmutil, settings

log_print = stringutil.StringUtil.log_print

class BotUtil:

    def __init__(self, bot) -> None:
        self.bot = bot

    async def restart(ctx):
        try:
            output = subprocess.check_output(["/bin/bash", "./restart.sh"])
            log_print(f"Script executed successfully: \n{output.decode('utf-8')}")
        except subprocess.CalledProcessError as e:
            log_print(f"An error occurred: \n{e.output.decode('utf-8')}")

    async def authorize(ctx):
        channel = ctx.channel.id
        command_channel = settings.BOTCOMMANDS
        if channel != command_channel:
            await ctx.author.send('Please resubmit this command to the correct channel.')
            return await ctx.message.delete()

    async def debug(self, ctx):
        now = timeutil.Time.bot_now()
        pst = 15*3600
        log_print("Creating debugging channels")
        await hnmutil.HandleHNM.process(self, ctx, "Fafnir",              3, 'n', str(timeutil.Time.format_time(now + (2 * 3600) + 90)))
        await hnmutil.HandleHNM.process(self, ctx, "Adamantoise",         4, 'n', str(timeutil.Time.format_time(now + (2 * 3600) - 2400 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "Behemoth",            5, 'n', str(timeutil.Time.format_time(now + (2 * 3600) - 1200 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "King Arthro",         0, 'n', str(timeutil.Time.format_time(now + (2 * 3600) + 90 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "Simurgh",             0, 'n', str(timeutil.Time.format_time(now + (2 * 3600) + 90 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "Shikigami Weapon",    0, 'n', str(timeutil.Time.format_time(now + (3 * 3600) + 90 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "King Vinegarroon",    0, 'n', str(timeutil.Time.format_time(now + (3 * 3600) + 90 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "Vrtra",               0, 'n', str(timeutil.Time.format_time(now - (84 * 3600) + 430 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "Tiamat",              0, 'n', str(timeutil.Time.format_time(now - (84 * 3600) - ((24 * 3600) / 2) + 430 - pst)))
        await hnmutil.HandleHNM.process(self, ctx, "Jormungand",          0, 'n', str(timeutil.Time.format_time(now - (84 * 3600) - (24 * 3600) + 430 - pst)))
