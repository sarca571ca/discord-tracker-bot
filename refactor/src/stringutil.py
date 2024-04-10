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
            if mod != ['n', 'a', 'd', 't'] and day != ['n', 'a', 'd', 't']:
                timestamp = mod
                mod = 'n'
            else:
                timestamp = mod
                mod = day
                day = 0
        return day, mod, timestamp

    def remove_formating(text): # Remove any formatting (e.g., **bold**, *italic*, __underline__, ~~strikethrough~~, etc.)
        pattern = r'(\*\*|\*|__|~~)(.*?)(\*\*|\*|__|~~)'
        stripped_text = re.sub(pattern, r'\2', text)
        return stripped_text

    def log_print(msg):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] [ALISE   ]")
        log_message = f"{timestamp} {msg}"
        print(log_message)
