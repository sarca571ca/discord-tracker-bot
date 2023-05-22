# This is a working timestamp converter.
# - Now we need to iterate this to make it replace the posted time automatically.

import discord
from discord.ext import commands
import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    timestamp_args = message.content.split()
    if len(timestamp_args) != 2:
        return

    date_str, time_str = timestamp_args
    timestamp = f"{date_str} {time_str}"
    try:
        datetime_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        utc_timestamp = int(datetime_obj.timestamp())  # Convert to integer
        await message.channel.send(f'Universal timestamp for {timestamp} is: <t:{utc_timestamp}:f>')
    except ValueError:
        pass

    await bot.process_commands(message)

bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos')