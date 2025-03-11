import pytz
from src import settings, stringutil
from datetime import datetime, timedelta, timezone

log_print = stringutil.StringUtil.log_print

class Time:

    def parse_time(hnm, timestamp):
        time_zone = Time.bot_tz()
        current_date = datetime.now(time_zone).date()
        valid_format = False
        parsed_datetime = None

        try:
            for date_format in settings.DATEFORMATS:
                try:
                    parsed_datetime = time_zone.localize(datetime.strptime(timestamp, date_format))
                    valid_format = True
                    break
                except ValueError:
                    pass

            if not valid_format:
                for time_format in settings.TIMEFORMATS:
                    try:
                        parsed_time = datetime.strptime(timestamp, time_format).time()
                        parsed_datetime = time_zone.localize(datetime.combine(current_date, parsed_time))
                        valid_format = True
                        break
                    except ValueError:
                        pass

            if valid_format:
                if parsed_datetime > datetime.now(time_zone):
                    current_date -= timedelta(days=1)
                if hnm not in settings.GW:
                    parsed_datetime = time_zone.localize(datetime.combine(current_date, parsed_datetime.time()))

                unix_timestamp = int(parsed_datetime.timestamp())

        except (ValueError, OverflowError, UnboundLocalError):
            if timestamp == None:
                err_msg = f"No date/time provided for {hnm}.\nUse the !help command for a list of commands and how to use them."
                log_print("Parse Time: No timestamp provided.")
            else:
                err_msg = f"Incorrect time format for {hnm}.\nUse the !help command for a list of commands and how to use them."
                log_print("Parse Time: Incorrect timestamp format was provided.")
            return err_msg

        try:
            if hnm in ["Fafnir", "Adamantoise", "Behemoth", "King Arthro", "Simurgh"]:
                unix_timestamp += (22 * 3600)  # Add 22 hours for GroundKings and KA
            elif hnm in ["Jormungand", "Tiamat", "Vrtra"]:
                unix_timestamp += (84 * 3600)  # Add 84 hours for GrandWyrms and KA
            elif hnm in ["Bloodsucker"]:
                unix_timestamp += (72 * 3600)  # Add 84 hours for GrandWyrms and KA
            else:
                unix_timestamp += (21 * 3600)  # Add 21 hours for other HNMs
        except (UnboundLocalError):
            log_print("Parse Time: No timestamp provided.")
            return
        except (ValueError, OverflowError):
            log_print("Parse Time: HNM provided does not exist.")
            return
        return unix_timestamp

    def strip_timestamp(message):
        if "<t:" not in message.content:
            return 0
        timestamp_start = message.content.index("<t:") + 3
        timestamp_end = message.content.index(":T>", timestamp_start)
        timestamp = int(message.content[timestamp_start:timestamp_end])
        dt = datetime.fromtimestamp(timestamp)
        return timestamp, dt

    def now():
        current_time = int(datetime.now().timestamp())
        return current_time

    def bot_now():
        current_time = int(datetime.now(pytz.timezone(settings.TZ)).timestamp())
        return current_time

    def bot_tz(): # Timezone of the bot
        return pytz.timezone(settings.TZ)

    def discord_tz():
        return datetime.now(timezone.utc)

    def format_time(time: int):
        return datetime.fromtimestamp(time)