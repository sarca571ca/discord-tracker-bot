# Discord DKP Bot
Simple bot that calculates DKP based on user input.....hopefully
## ToDo

ToD Managment
- Uses commands to set individual ToD's for DKP mobs
    - ~~Ground Kings - HQ System 22hr respawn 7 windows every 10 mins~~ done
    - HQ sytem for Ground Kings needs to be implemented
    - ~~KA - 21hr respawn 7 windows every 10 minutes?~~ - done
    - ~~KV - 21hr respawn spawns only during earth weather~~ - done
    - ~~Shiki - 21hr respawn exactly~~ - done
    - Grand Wyvrn - 84hr respawn 25 windows every 1hrs
        - Needs a specialized tracking system implemented
- Commands need to be more robust to handle various time/date formats
- Days currently have to be manually inputed
  - Need to be able to ignore the day entry or independtly update it

Channel Management
- ~~Creates channels 10 minutes prior to 1st window~~ - done
- ~~Moves the channels 4 hours after 1st window~~ - done
- Change the channel move 4 hours from 1st window to last window
  - This will allow the system to be compaitable with any dkp mobs that have special reqs on spawns
  - might cause issues with KV
- King Ving will need special reqs to open a window im not to sure tbh
- Insert window notification when a window open in the correct channel
  - x's during a window will log the window and help determine the amount of windows camped
  - o's will remove players from future windows until another x is used
  - Grand Wyvrn system will be different and require an x every window

DKP System
- Read's channel entries for x's and prints an report that can be copied right into the spreadsheet
- any x after the report will be tracked seperately for review by an officer to determine its validity
- Need to be able to update a yaml to save dkp values
- Should we do away with the spreadsheet altogether?
- We can initially set everyones current values in a csv and save that as the start point

![Image](./images/workflow.png)