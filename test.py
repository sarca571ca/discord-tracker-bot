import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)
allowed_channel_id = 1108667680774422579

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command()
async def test(ctx):
    if ctx.channel.id == allowed_channel_id:
        await ctx.send('This is a test message.')

bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos')