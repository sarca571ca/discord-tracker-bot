bot_token = 'Put your bot tokken here'                                                      # Bot token goes in this field

guild = 1234                                                                                # Guild ID
hnm_times = 1234                                                                            # Channel ID where the camp times are posted
bot_commands = 1234                                                                         # Designated bot-commands channel for setting ToD's
clear_bot_commands = False                                                                   # True or False determines whether bot-commands issued in the bot-commnads channel are deleted
make_channel = 30                                                                           # Makes a channel 30-Minutes before window
move_review = 3                                                                             # Moves the channel for DKP Review 3-hours after last window
archive_channel = 4                                                                         # Archive the channel as a csv on the bot server after 4 hours after review or when command !archive is issued.
archive_wait = 5                                                                            # The amount aof days a channel can sit in the archive channel. This counts from when the channel was created.
ignore_channels = ['kv', 'shi', 'tia', 'vrt']                                               # Used the prevent the sending of window messages to certain channels
ignore_create_channels = ['King Vinegarroon', 'Tiamat', 'Vrtra']                            # Used to prevent the creation of certain channels eg. KV because its random

# This message will display when channel opens windows for x-ins 10 minutes prior
window_message = """
```This is where you would put any channel creation notes.
Examples:
- Channel will stay open 3-hours after creation after which will be moved
to the DKP REVIEW section
- Instructions on how to handle x-ins x1, x3, x7 xout @ 3, whatever rules you want to use.```
"""