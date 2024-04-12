import discord.ext
import typing
from discord.ext import commands
import discord.ext.commands
from src import settings, stringutil, hnmutil, channelutil, botutil

log_print = stringutil.StringUtil.log_print

class Alise(commands.Bot):

    async def on_ready(self):
        msg = log_print(f"Logged in as {self.user.name}")

        guild = self.get_guild(settings.GUILDID)
        member = guild.get_member(self.user.id)

        if member:
            display_name = "Alise"
            await member.edit(nick=display_name)
            msg = log_print(f"Display name set to: {display_name}")
        # Load in our cogs
        try:
            await self.load_extension('cogs.tasks')
        except discord.ext.commands.errors.ExtensionAlreadyLoaded as error:
            msg = log_print(error)
            await channelutil.LogPrint.print(self, msg)

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

        @self.command(name='open')
        async def open(ctx):
            await channelutil.Manager.open(ctx)

        @self.command(name='close')
        async def close(ctx):
            await channelutil.Manager.close(ctx)

        @self.command(name='pop')
        async def pop(ctx):
            await channelutil.Manager.pop(ctx)

        @self.command(name='sort_channels', help='Sort channels in a category from newest to oldest.')
        async def sort_channels(ctx):
            channel = ctx.channel.id
            command_channel = settings.BOTCOMMANDS
            if channel != command_channel:
                await ctx.author.send('Please resubmit this command to the correct channel.')
                return await ctx.message.delete()

            await channelutil.Manager.sort_channels(ctx)

        @self.command(name='restart') # Restarts the bot from discord.
        async def restart(ctx):
            channel = ctx.channel.id
            command_channel = settings.BOTCOMMANDS
            if channel != command_channel:
                await ctx.author.send('Please resubmit this command to the correct channel.')
                return await ctx.message.delete()

            await botutil.BotUtil.restart(ctx)

        # @self.command(name='debug')
        # async def debug(ctx):
        #     channel = ctx.channel.id
        #     command_channel = settings.BOTCOMMANDS
        #     if channel != command_channel:
        #         await ctx.author.send('Please resubmit this command to the correct channel.')
        #         return await ctx.message.delete()

        #     await botutil.BotUtil.debug(self, ctx)
