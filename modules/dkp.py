# import discord
# from discord.ext import commands

# intents = discord.Intents.default()
# intents.members = True  # Enable the 'members' intent to access member-related events

# bot = commands.Bot(command_prefix='!', intents=intents)

# dkp_data = {}  # A dictionary to store DKP data

# @bot.event
# async def on_ready():
#     print(f'Logged in as {bot.user.name}')

# @bot.command()
# async def add_dkp(ctx, player: discord.Member, points: int):
#     """Add DKP points to a player."""
#     if player.id not in dkp_data:
#         dkp_data[player.id] = 0

#     dkp_data[player.id] += points
#     await ctx.send(f'{player.display_name} has been awarded {points} DKP.')

# @bot.command()
# async def check_dkp(ctx, player: discord.Member = None):
#     """Check DKP points for a player or all players if none is specified."""
#     if player is None:
#         message = "DKP standings:\n"
#         for member_id, points in dkp_data.items():
#             member = ctx.guild.get_member(member_id)
#             if member is not None:
#                 message += f'{member.display_name}: {points} DKP\n'
#     else:
#         if player.id in dkp_data:
#             message = f'{player.display_name} has {dkp_data[player.id]} DKP.'
#         else:
#             message = f'{player.display_name} has no DKP data.'

#     await ctx.send(message)

# bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos')

# import discord
# from discord.ext import commands

# intents = discord.Intents.default()
# intents.members = True  # Enable the 'members' intent to access member-related events

# bot = commands.Bot(command_prefix='!', intents=None)

# @bot.event
# async def on_ready():
#     print(f'Logged in as {bot.user.name}')

# @bot.command()
# async def hello(ctx):
#     await ctx.send('Hello, I am your Discord bot!')

# bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos')

import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True  # Enable the 'members' intent to access member-related events

bot = commands.Bot(command_prefix='!', intents=intents)

allowed_channel_id = 1108667680774422579  # Replace with the ID of the desired channel

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def add_dkp(ctx, player: discord.Member, points: int):
    """Add DKP points to a player."""
    if ctx.channel.id == allowed_channel_id:
        if player.id not in dkp_data:
            dkp_data[player.id] = 0

        dkp_data[player.id] += points
        await ctx.send(f'{player.display_name} has been awarded {points} DKP.')
    else:
        await ctx.send("This command can only be used in the designated channel.")

@bot.command()
async def check_dkp(ctx, player: discord.Member = None):
    """Check DKP points for a player or all players if none is specified."""
    if ctx.channel.id == allowed_channel_id:
        if player is None:
            message = "DKP standings:\n"
            for member_id, points in dkp_data.items():
                member = ctx.guild.get_member(member_id)
                if member is not None:
                    message += f'{member.display_name}: {points} DKP\n'
        else:
            if player.id in dkp_data:
                message = f'{player.display_name} has {dkp_data[player.id]} DKP.'
            else:
                message = f'{player.display_name} has no DKP data.'

        await ctx.send(message)
    else:
        await ctx.send("This command can only be used in the designated channel.")


bot.run('MTEwODY1MTQxMDI4NDg4ODA2NA.GfstjG.Kdu97sk1ktv43ukZ82NmnrCsnrI0nL46HqQNos')
