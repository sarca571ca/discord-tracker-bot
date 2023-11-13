import discord
import re
import yaml
from datetime import datetime
import config
import asyncio

from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

def load_settings():
    with open('settings/settings.yaml', 'r') as f:
        ss = yaml.safe_load(f)
    return ss

def ref(text): # Remove any formatting (e.g., **bold**, *italic*, __underline__, ~~strikethrough~~, etc.)
    pattern = r'(\*\*|\*|__|~~)(.*?)(\*\*|\*|__|~~)'
    stripped_text = re.sub(pattern, r'\2', text)

    return stripped_text
# working on a new method of stripping the text
def ref2(text):
    # Remove emojis
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00026000-\U00027BFF\U0001F1E0-\U0001F1FF\u2022\u3030]+")
    text = emoji_pattern.sub('', text)

    # Remove formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)

    return text.strip()

def extract_info(text):
    # Remove emojis and formatting
    cleaned_text = ref2(text)

    # Split the cleaned_text by whitespace to get individual words
    words = cleaned_text.split()

    # Strip the first 3 letters from the first word and save it in a variable
    first_word_stripped = words[0][:3].lower()

    # Extract the number from parentheses and save it in another variable
    number = re.search(r'\((\d+)\)', cleaned_text)
    number = int(number.group(1)) if number else None

    return first_word_stripped, number
# These functions are near identical i need to modify
# the code to use one or the other not both
def get_utc_timestamp(message):
    if "<t:" not in message.content:
        return 0
    timestamp_start = message.content.index("<t:") + 3
    timestamp_end = message.content.index(":T>", timestamp_start)
    timestamp = message.content[timestamp_start:timestamp_end]
    return int(timestamp)

def calculate_time_diff(message_content):
    # Extract the UTC timestamp
    utc_start = message_content.find("<t:")
    utc_end = message_content.find(":T>")
    if utc_start != -1 and utc_end != -1:
        utc = int(message_content[utc_start + 3:utc_end])
        dt = datetime.fromtimestamp(utc)
        return dt, utc
    else:
        return None, None  # If no valid timestamp found, return None

async def log_to_discord_channel(msg):
    
    ss = load_settings()
    LOG_CHANNEL_ID = ss['log_channel_id']
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:  # Check if the channel exists and the bot can access it
        await channel.send(msg)
        
def log_print(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] [ALISE   ]")
    log_message = f"{timestamp} {msg}"
    print(log_message)

    # As the log_to_discord_channel function is asynchronous, 
    # you need to create a task to run it if you're not in an async context
    # bot.loop.create_task(log_to_discord_channel(log_message))
    # log_to_discord_channel(log_message)

async def find_last_window(ctx):
    window_pattern = await format_window_heading("Window (\d+)")
    
    # Constructing the regex pattern based on the expected format
    regex_pattern = r'^-+ Window (\d+) -+$'
    
    async for message in ctx.channel.history(limit=None, oldest_first=False):
        match = re.search(regex_pattern, message.content)
        if match:
            window_number = match.group(1)  # Extract the window number
            window = f"Window {window_number}"
            return window

async def format_window_heading(word):
    word = word[:48]
    
    # Calculate the number of dashes needed on each side
    dash_count = (54 - len(word)) // 2
    
    # Create the formatted string
    heading = '-' * dash_count + ' ' + word + ' ' + '-' * dash_count
    
    return heading

def find_hnm_location(ctx, channel, loc):
    for keyword, keyword_dict in config.location_tables.items():
        if keyword in channel:
            for sub_keyword, sub_location in keyword_dict.items():
                if sub_keyword in loc:
                    return sub_location

    # If we reach here, no location was found
    log_print("Pop: Location not found in channel name.")

    # Send the DM with the available locations
    available_locations_key = []
    available_locations_value = []
    for keyword, keyword_dict in config.location_tables.items():
        if keyword in channel:
            available_locations_key.extend(list(keyword_dict.keys()))
    
    for keyword, keyword_dict in config.location_tables.items():
        if keyword in channel:
            available_locations_value.extend(list(keyword_dict.values()))

    if available_locations_key and available_locations_value:
        combined = [f"{value} - {key}" for key, value in zip(available_locations_key, available_locations_value)]
        combined_str = "\n".join(combined)
        available_value = "\n".join(available_locations_value)
        dm_msg = (f"Invalid location argument provided. "
                  f"Here are the available locations for {channel}:\n{combined_str}")
        asyncio.create_task(ctx.author.send(dm_msg))

    return None
