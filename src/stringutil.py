import re
from datetime import datetime

class StringUtil():

    def __init__(self) -> None:
        pass

    def sort_hnm_args(day, mod, timestamp):
        if mod is None and timestamp is None:
            timestamp = str(day)
            day = 0
            mod = 'n'
        elif timestamp is None:
            if mod != ['n', 'a', 'd', 't'] and day != ['n', 'a', 'd', 't'] and len(str(day)) <= 2:
                timestamp = mod
                mod = 'n'
            elif len(mod) > 1:
                timestamp = str(day) + ' ' + mod
                mod = 'n'
                day = 0
            else:
                timestamp = mod
                mod = day
                day = 0
        return day, mod, timestamp

    def remove_formating(text): # Remove any formatting (e.g., **bold**, *italic*, __underline__, ~~strikethrough~~, etc.)
        pattern = r'(\*\*|\*|__|~~)(.*?)(\*\*|\*|__|~~)'
        stripped_text = re.sub(pattern, r'\2', text)
        return stripped_text

    def format_window_heading(word): # was async before but shouldnt need to be?
        word = word[:48]

        # Calculate the number of dashes needed on each side
        dash_count = (54 - len(word)) // 2

        # Create the formatted string
        heading = '-' * dash_count + ' ' + word + ' ' + '-' * dash_count

        return heading

    async def find_last_window(ctx):
        window_pattern = StringUtil.format_window_heading("Window (\d+)")

        # Constructing the regex pattern based on the expected format
        regex_pattern = r'^-+ Window (\d+) -+$'

        async for message in ctx.channel.history(limit=None, oldest_first=False):
            match = re.search(regex_pattern, message.content)
            if match:
                window_number = match.group(1)  # Extract the window number
                window = f"Window {window_number}"
                return window

    def log_print(msg):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] [ALISE   ]")
        log_message = f"{timestamp} {msg}"
        print(log_message)
        return log_message
