import discord.ext
import typing
import asyncio
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
        async def pop(ctx, *linkshell):
            await channelutil.Manager.pop(ctx, *linkshell)

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
        @self.command(name='continue')
        async def camp_continue(ctx):
            await channelutil.Manager.camp_continue(ctx)

        @self.command(name='stable')
        async def stable(ctx):
            await channelutil.Manager.stable(ctx)

        @self.command(name='enrage')
        async def enrage(ctx, window: typing.Optional[int] = 0):
            category = ctx.channel.category
            awaiting_processing_category = discord.utils.get(ctx.guild.categories, id=settings.AWAITINGPROCESSINGID)
            hnm_times_category = discord.utils.get(ctx.guild.categories, id=settings.HNMCATEGORYID)
            if not category or category.name != awaiting_processing_category.name:
                await ctx.send(f"The command can only be used in the '{awaiting_processing_category}' category.")
                return
            if window == 0:
                await ctx.author.send("Please resend the command !enrage with a number please. eg. !enrage 1")
                return await ctx.message.delete()

            await ctx.channel.edit(category=hnm_times_category)
            enrage_task = asyncio.create_task(channelutil.Manager.enrage(ctx, window))
            enrage_task.set_name(f"wm-{ctx.channel.name}")
            task_name = enrage_task.get_name()
            log_print(f"Window Manager: Task {task_name} has been started.")
            settings.RUNNINGTASKS.append(task_name)
            await ctx.message.delete()

        @self.command() # Archive command used for moving channels from DKP Review Category
        async def archive(ctx, option=None):
            channel = ctx.channel
            category = ctx.channel.category
            dkp_processing_category = discord.utils.get(ctx.guild.categories, id=settings.DKPREVIEWID)
            archive_category = discord.utils.get(ctx.guild.categories, id=settings.ATTENDARCHID)

            if not category or category.name != dkp_processing_category.name:
                await ctx.send(f"The command can only be used in the '{dkp_processing_category}' category.")
                return

            await channelutil.Manager.archive_channels(archive_category, channel, category, option)

        # @self.command(name='debug')
        # async def debug(ctx):
        #     channel = ctx.channel.id
        #     command_channel = settings.BOTCOMMANDS
        #     if channel != command_channel:
        #         await ctx.author.send('Please resubmit this command to the correct channel.')
        #         return await ctx.message.delete()

        #     await botutil.BotUtil.debug(self, ctx)
