import discord
from discord.ext import commands

intents = discord.Intents.all()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = 'MTExMDM3NjUyNjgwMjg1Mzk3OQ.GxNguG.7r2bQPC8w-USwXEb0VCUKS-gk85266IBF-XcWM'
target_category_name = 'HNM ATTENDANCE'
target_channel_name = 'may23-adama1'

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name}')
    print('Searching for channels...')
    await search_channels()


async def search_channels():
    # Replace 'YOUR_GUILD_ID' with the ID of the guild/server you want to search in
    guild_id = '876434275661135982'
    guild = bot.get_guild(int(guild_id))

    # Find the target category
    category = discord.utils.get(guild.categories, name=target_category_name)

    if category is None:
        print(f"Category '{target_category_name}' not found on the server.")
        return

    # Search for the target channel within the category
    for channel in category.channels:
        if channel.name == target_channel_name:
            print(f"Channel '{channel.name}' found in the '{category.name}' category.")
            break
    else:
        print(f"Channel '{target_channel_name}' not found in the '{category.name}' category.")


bot.run(bot_token)
