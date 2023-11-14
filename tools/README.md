# Discord DKP Bot
Simple bot that calculates DKP based on user input.....hopefully
## ToDo

ToD Managment
- Grand Wyvrn - 84hr respawn 25 windows every 1hrs
  - Needs a specialized tracking system implemented

Channel Management
- Need to make channel management for use with Grand Wyvrns so officer use the !open and !close commands in the channel and the appropriate headings happens ie ---- Window x: Time of Window ----

DKP System 
- currently on hold as we handle dkp independent of this bot

Refactoring
- Need to make more functions for things that are repeated a lot through the code
- Clean up the code and reorganize the sturcture some.
- Change the proccess_hnm_window() to look in the channel.topic instead of message.content for timestamps
  - This will fix errors with manually created channels as the bot can always change to topic but not the first comment.
  - This will enable to bot to retroactively fix incorrectly inputed timestamps also.

![Image](./images/workflow.png)