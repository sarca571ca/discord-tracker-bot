import discord
from discord.ext import commands
import asyncio

# List of names
name_list = ['wd-tod','John', 'Alice', 'Bob', 'Jeff', 'Austin']

# Bot setup
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await send_x_messages()

@bot.event
async def on_message(message):
    if message.author == bot.user and message.content == 'x':
        current_index = name_list.index(bot.user.name)
        if current_index != -1:
            next_index = (current_index + 1) % len(name_list)
            await change_display_name(next_index)
            await send_x_messages()
    await bot.process_commands(message)

async def change_display_name(index):
    new_name = name_list[index]
    await bot.user.edit(username=new_name)
    print(f'Display name changed to {new_name}')

async def send_x_messages():
    for _ in range(len(name_list)):
        await asyncio.sleep(1)  # Delay between messages
        await bot.get_channel(1110806918190092298).send('x')

bot.run('MTExMDM3NjUyNjgwMjg1Mzk3OQ.GxNguG.7r2bQPC8w-USwXEb0VCUKS-gk85266IBF-XcWM') # wd-tod
