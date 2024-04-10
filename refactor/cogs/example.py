from discord.ext import commands, tasks

# class ExampleCog(commands.Cog):
#     def __init__(self, bot: commands.Bot) -> None:
#         self.bot = bot
	
#     @commands.Cog.listener()
#     async def on_ready(self) -> None:
#         pass
	
#     @commands.command()
#     async def command(self, ctx: commands.Context) -> None:
#         pass

# async def setup(bot: commands.Bot) -> None:
#     await bot.add_cog(ExampleCog(bot))

class TaskTest(commands.Cog):
    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        print(self.index)
        self.index += 1

class TaskTest1(commands.Cog):
    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        print(self.index)
        self.index += 1

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TaskTest())
    await bot.add_cog(TaskTest1())
    print("Tasks Loaded!")