import discord
from discord.ext import commands, tasks
from dateutil import parser
import datetime

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

# Task that creates channels automaticaly
@tasks.loop(minutes=1)
async def create_channel_task():
    guild_id = 876434275661135982  # Replace with your guild ID
    category_name = "HNM ATTENDANCE"
    output_channel_id = 1110425188962676786  # Replace with your output channel ID
    hnm_times_channel_id = 1110052586561744896  # Replace with your hnm-times channel ID

    guild = bot.get_guild(guild_id)
    category = discord.utils.get(guild.categories, name=category_name)
    output_channel = bot.get_channel(output_channel_id)
    hnm_times_channel = bot.get_channel(hnm_times_channel_id)

    if not category:
        category = await guild.create_category(category_name)

    current_time = datetime.datetime.now()
    target_time = current_time - datetime.timedelta(minutes=10)

    async for message in hnm_times_channel.history(limit=None, oldest_first=True):
        if message.content.startswith("-"):
            channel_name = message.content[2:7].strip()

            day_start = message.content.find("(")
            day_end = message.content.find(")")
            if day_start != -1 and day_end != -1:
                day = message.content[day_start + 1:day_end].strip()

            utc_start = message.content.find("<t:")
            utc_end = message.content.find(":T>")
            if utc_start != -1 and utc_end != -1:
                utc = int(message.content[utc_start + 3:utc_end])
                dt = datetime.datetime.utcfromtimestamp(utc)
                date = dt.strftime("%b%d").lower()
                hnm = channel_name.upper()

                hnm_time = datetime.datetime.utcfromtimestamp(utc - (10 * 60))

                if hnm_time <= target_time:
                    channel_name = f"{date}-{hnm}{day}"
                    channel = await guild.create_text_channel(channel_name, category=category,
                                                              topic="\nPlease x in to have your dkp recorded!")
                    await channel.edit(position=hnm_times_channel.position + 1)
                    await output_channel.send(f"Channel {channel.mention} created.")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# This section isn't working correctly, need to make sure its using the original hnm names maybe?
# review and maybe rewrite the code yourself. It does seem to delete the channel after 10 minutes.
# instead of deleting we need to move the channel to the archive category maybe? not sure about
# this though. explore different options, the channel should alway be able to review. might have
# to add options in the future to allow for DKP adjustments.

@bot.command()
async def cc(ctx):
    guild = ctx.guild
    category_name = "HNM ATTENDANCE"
    target_channel_ids = [1110076161201020949, 1110052586561744896]  # These channels are safe from deletiong using the !rc command

    # Check if the category exists
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        # Create the category if it doesn't exist
        category = await guild.create_category(category_name)

    # Get the target channels
    target_channels = [bot.get_channel(channel_id) for channel_id in target_channel_ids]
    target_channels = [channel for channel in target_channels if isinstance(channel, discord.TextChannel)]

    # Read messages from the target channels
    for target_channel in target_channels:
        async for message in target_channel.history(limit=None, oldest_first=True):
            if message.content.startswith("-"):
                channel_name = message.content[2:7].strip()

            # Extract the day
            day_start = message.content.find("(")
            day_end = message.content.find(")")
            if day_start != -1 and day_end != -1:
                day = message.content[day_start + 1:day_end].strip()

            # Extract UTC timestamp
            utc_start = message.content.find("<t:")
            utc_end = message.content.find(":T>")
            if utc_start != -1 and utc_end != -1:
                utc = int(message.content[utc_start + 3:utc_end])
                dt = datetime.datetime.utcfromtimestamp(utc)
                date = dt.strftime("%b%d").lower()

                hnm = channel_name.upper()

                # Create the channel inside the category
                channel = await guild.create_text_channel(f"{date}-{hnm}{day}", category=category)


    # The line below is for testing only and can be deleted later on
    await ctx.author.send(f"Channel {channel.mention} created in category {category.name}")

# Deletes all channels except target_channel_ids. Used for testing only removed before production.
@bot.command()
async def rc(ctx):
    guild = ctx.guild
    category_name = "HNM ATTENDANCE"
    target_channel_ids = [1110076161201020949, 1110052586561744896]  # Replace with the actual channel IDs

    # Check if the category exists
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        await ctx.send("Category does not exist.")
        return

    # Get all channels in the category
    channels = category.channels

    # Remove channels that are not in the target channel IDs
    channels_to_remove = [channel for channel in channels if channel.id not in target_channel_ids]

    for channel in channels_to_remove:
        await channel.delete()

bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos') # wd-dkp-bot
