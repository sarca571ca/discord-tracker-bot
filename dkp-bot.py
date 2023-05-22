import discord
from discord.ext import commands
from datetime import datetime, timedelta

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hnm(ctx, hnm_name, day, time):
    # Convert day and time to UTC
    utc_time = convert_to_utc(day, time)

    # Send DM to the user
    await ctx.author.send(f'UTC time for {hnm_name}: {utc_time}')

    # Post the result in a channel
    channel = bot.get_channel(1110052586561744896)  # Replace `channel_id` with your desired channel ID
    await channel.send(f'{hnm_name}: {utc_time}')

def convert_to_utc(day, time):
    # Assuming day is in the format "YYYY-MM-DD" and time is in the format "HH:MM"
    dt = datetime.strptime(f'{day} {time}', '%Y-%m-%d %H:%M:%S')

    # Convert to UTC
    utc_dt = dt - timedelta(hours=dt.hour)

    return utc_dt.strftime('%Y-%m-%d %H:%M')

bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos')