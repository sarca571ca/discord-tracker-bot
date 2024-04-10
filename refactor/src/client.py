import typing
from discord.ext import commands
from src import settings, stringutil, hnmutil

log_print = stringutil.StringUtil.log_print

class Alise(commands.Bot):

    async def on_ready(self):
        log_print(f"Logged in as {self.user.name}")

        # Load in our cogs
        await self.load_extension('cogs.tasks')

    # Function to add in all our commands
    def add_commands(self):
        @self.command(name="hnm", aliases=settings.HNMCOMMANDS, description="Used for processing HNM death timers.")
        async def hnm(ctx, day: typing.Optional[int] = 0, mod: typing.Optional[str] = None,
                *, timestamp: typing.Optional[str] = None
                ):
            channel = ctx.channel.id
            command_channel = settings.BOTCOMMANDS
            if channel != command_channel:
                await ctx.author.send('Please resubmit this command to the correct channel.')
                return await ctx.message.delete()

            hnm = hnmutil.HandleHNM(self)
            msg = ctx.message.content[1:].split(" ")
            cmd = msg[0]

            day, mod, timestamp = stringutil.StringUtil.sort_hnm_args(day, mod, timestamp)

            await hnm.find(ctx, cmd, day, mod, timestamp)
