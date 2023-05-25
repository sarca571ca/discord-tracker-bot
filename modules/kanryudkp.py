import os
import discord
from discord.ext import commands
import pandas as pd

# List of folks allowed to trigger the command.
DKP_Processors = [
    #Kanryu
    206209267819085824,
    #Sundrix
    49689034397581312,
    #Izual
    77382766802501632,
    #Setsuko
    220032311721197570,
    #Asri
    # 701072612431757353
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
guild = discord.Guild

debugmode = True

#Simple method handler for debug message toggles.
def debugmsg(msg):
    if debugmode:
        print(msg)

#Processes if the person making the request is a member of the DKP team
def DKPProcessor(id):
    if id in DKP_Processors:
        debugmsg('Approved and trained DKP processor.')
        return True
    else:
        debugmsg('Processor not found.')
        return False

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    debugmsg('Message found. Beginning process.')
    if message.author == client.user:
        debugmsg('Bot is the client. Leaving.')
        return
    elif message.content.startswith('!'):
        debugmsg('Source was not the bot but sent a command.')

        cmd = message.content.split()[0].replace("!", "")
        if len(message.content.split()) > 1:
            parameters = message.content.split()[1:]

        if cmd == 'x':
            debugmsg('Command !x triggered.')

            # Delete the user's message
            await message.delete()

            # Get the author's display name
            author_display_name = message.author.display_name

            # Get the Unix timestamp of the message
            timestamp_unix = int(message.created_at.timestamp())

            # Format the response message with display name and timestamp
            response = f"Author: {author_display_name}\nTimestamp (Unix): {timestamp_unix}"

            # Send the response message to the channel
            await message.channel.send(response)

    if message.author == client.user:
        debugmsg('Bot is the client. Leaving.')
        return
    elif message.content.startswith('!') and DKPProcessor(message.author.id):
        debugmsg('Source was not the bot but is an approved DKP processor.')

        cmd = message.content.split()[0].replace("!","")
        if len(message.content.split()) > 1:
            parameters = message.content.split()[1:]

        if cmd == 'DKPExport':
            debugmsg('Scan requested. Starting export.')

            # Sets up the initial dataframe
            data = pd.DataFrame(columns=['Player', 'Timestamp', 'Message'])
            
            # Checking if the message is a command call
            def is_command (msg): 
                if len(msg.content) == 0:
                    return False
                elif msg.content.split()[0] == '!DKPExport':
                    return True
                else:
                    return False

            display_names = []
            times = []
            message_content = []

            #Process channel contents to simplify DKP process
            debugmsg('Beginning to process the loop.')
            async for msg in message.channel.history(limit=10000): # Limit to set to 10000 entries
                if msg.author != client.user:                                  
                    if not is_command(msg):                                
                        display_names.append(msg.author.display_name)
                        times.append(msg.created_at.strftime('%Y-%m-%d %H:%M:%S'))
                        message_content.append(msg.content)
                
            # Create DataFrame out of the finalized channel processing
            data = pd.DataFrame({'Player':display_names,
                                  'Timestamp':times, 
                                  'Message':message_content})
            
            # Sort in ascending order by message time
            data.sort_values(by='Timestamp', ascending = True, inplace = True)

            # Check if HNM DKP
            if message.channel.category_id == 1071272453164249128:
                debugmsg('HNM event for DKP')
                file_path = r"c://Users//rmacleod//Documents//GitHub//discord-dkp-bot//data//hnm//" + message.channel.name + "\\"
            # If it isn't HNM assume it is Event DKP
            else:
                debugmsg('Not HNM so must be event DKP')
                file_path = r"c://Users//rmacleod//Documents//GitHub//discord-dkp-bot//data//event//" + message.channel.name + "\\"

            # Check for and create the filepath if it is non-existant. 
            if not os.path.exists(file_path):
                debugmsg('File Path doesn\'t exist. Creating new folder. ')
                os.makedirs(file_path)

            # Sets the finalized file location and name.  
            file_location = file_path + message.channel.name+ ".csv"
            debugmsg('Output location is ' + file_location)

            # Exports the file as an excel document.
            data.to_csv(file_location, index=False)
            debugmsg('Content successfully output. Good job.')
    
    # A bad command was passed to the bot or an irrelevant message was seen.         
    else: debugmsg('Something went wrong. We reached the end.')

# @bot.command()
# async def x(ctx):
#     debugmsg('Command !x triggered.')

#     # Delete the user's message
#     await ctx.delete()

#     # Get the author's display name
#     author_display_name = ctx.author.display_name

#     # Get the Unix timestamp of the message
#     timestamp_unix = int(ctx.created_at.timestamp())

#     # Format the response message with display name and timestamp
#     response = f"Author: {author_display_name}\nTimestamp (Unix): {timestamp_unix}"

#     # Send the response message to the channel
#     await ctx.channel.send(response)


#Bot Token to connect to Discord via WD_DKP_Processor
client.run('MTExMDM3NjUyNjgwMjg1Mzk3OQ.GxNguG.7r2bQPC8w-USwXEb0VCUKS-gk85266IBF-XcWM')