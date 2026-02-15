"""
Settings file
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _get_env(key, cast_type, required=True):
    value = os.getenv(key)
    if required and not value:
        raise ValueError(f"{key} not set in .env file")
    if value and cast_type:
        if cast_type == str:
            return value
        try:
            return cast_type(value)
        except ValueError as exc:
            raise ValueError(f"{key} must be a valid {cast_type.__name__}") from exc
    return value


# Server Globals
TOKEN = _get_env("TOKEN", str)
GUILDID = _get_env("GUILDID", int)  # uses int default
# Channels
HNMTIMES = _get_env("HNMTIMES", int)
BOTCOMMANDS = _get_env("BOTCOMMANDS", int)
CAMPPINGS = _get_env("CAMPPINGS", int)
BOTLOGS = _get_env("BOTLOGS", int)
# Categories
HNMCATEGORYID = _get_env("HNMCATEGORYID", int)
AWAITINGPROCESSINGID = _get_env("AWAITINGPROCESSINGID", int)
DKPREVIEWID = _get_env("DKPREVIEWID", int)
ATTENDARCHID = _get_env("ATTENDARCHID", int)
VIPCATID = _get_env("VIPCATID", int)


# Command Gloabals
FAFNIR = ["faf", "fafnir"]
ADAMANTOISE = ["ad", "ada", "adam", "adamantoise"]
BEHEMOTH = ["beh", "behe", "behemoth"]
KA = ["ka", "kinga"]
SIM = ["sim"]
SHIKI = ["shi", "shiki", "shikigami"]
KV = ["kv", "kingv", "kingvine"]
BLOODSUCKER = ["bs", "blo", "bloodsucker"]
VRTRA = ["vrt", "vrtr", "vrtra"]
TIAMAT = ["tia", "tiam", "tiamat"]
JORM = ["jor", "jorm", "jormundgand"]

ALIASES = [FAFNIR, ADAMANTOISE, BEHEMOTH, KA, SIM, SHIKI, KV, VRTRA, TIAMAT, JORM]
HNMCOMMANDS = (
    FAFNIR
    + ADAMANTOISE
    + BEHEMOTH
    + KA
    + SIM
    + SHIKI
    + KV
    + BLOODSUCKER
    + VRTRA
    + TIAMAT
    + JORM
)

# Time Related Globals
DATEFORMATS = [  # List of accepted date formats
    "%Y-%m-%d %I%M%S %p",
    "%Y%m%d %I%M%S %p",
    "%y%m%d %I%M%S %p",
    "%m%d%Y %I%M%S %p",
    "%m%d%Y %I%M%S %p",
    "%Y-%m-%d %I:%M:%S %p",
    "%Y%m%d %I:%M:%S %p",
    "%y%m%d %I:%M:%S %p",
    "%m%d%Y %I:%M:%S %p",
    "%m%d%Y %I:%M:%S %p",
    "%Y-%m-%d %H%M%S",
    "%Y%m%d %H%M%S",
    "%y%m%d %H%M%S",
    "%m%d%Y %H%M%S",
    "%m%d%Y %H%M%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y%m%d %H:%M:%S",
    "%y%m%d %H:%M:%S",
    "%m%d%Y %H:%M:%S",
    "%m%d%Y %H:%M:%S",
    "%Y-%m-%d %h%M%S",
    "%Y%m%d %h%M%S",
    "%y%m%d %h%M%S",
    "%m%d%Y %h%M%S",
    "%m%d%Y %h%M%S",
    "%Y-%m-%d %h:%M:%S",
    "%Y%m%d %h:%M:%S",
    "%y%m%d %h:%M:%S",
    "%m%d%Y %h:%M:%S",
    "%m%d%Y %h:%M:%S",
]

TIMEFORMATS = ["%I%M%S %p", "%I:%M:%S %p", "%H%M%S", "%H:%M:%S", "%h:%M:%S"]

TZ = "America/Los_Angeles"

# Genral Setting Globals
MAKECHANNEL = 20
ARCHIVEWAIT = 5

WINDOWMEASSAGE = """```
Note:
    - Channel will be open for 5-Minutes after pop/last window.
    - Channel is moved to Awaiting Processing category.
    - Late x-in's (within reason) or corrections to your camp status can be made after its moved.
    - DO NOT X-IN before arriving to camp. This means in position and buffed.
```"""

WINDOWMEASSAGEKV = """```
Note:
    - Channel is manually managed, please ensure there will be weather before x-in.
    - The !pop command will work within this channel.
    - Late x-in's (within reason) or corrections to your camp status can be made after its moved.
```"""

WINDOWMEASSAGEGW = """```
Note:
    - Channel is manually managed, a valid hold party must be present for dkp.
    - Conditions for valid hold party are: Tank (w/ Resist Set), BRD, WHM, 2 Sleeps
    - The !pop command will work within this channel.
    - Windows will be opened 5-Minutes prior to window and closed 1-Minute after window.
    - Late x-in's won't be allowed due to the nature of this camp.
```"""

# Storage Globals
KVOPEN = []
PROCESSEDLIST = []
RUNNINGTASKS = []
EXTENDEDTASK = []

# HNM Related Globals
GREATER_THAN_DAY = ["Jormungand", "Tiamat", "Vrtra", "Bloodsucker"]
GK = ["Fafnir", "Adamantoise", "Behemoth"]
HQ = {"Fafnir": "Nidhogg", "Adamantoise": "Aspidochelone", "Behemoth": "King Behemoth"}
SPAWNGOUP1 = GK + ["King Arthro", "Simurgh"]  # 22HR Spawns
SPAWNGOUP2 = ["Shikigami Weapon", "King Vinegarroon"]

HNMINFO = {
    "faf": "Can't miss him.",
    "ada": "https://media.discordapp.net/attachments/1175180691550523452/1261704293166092368/image.png?ex=66953eb0&is=6693ed30&hm=ba8558476bd46f7996b6a93233a2b8548ca8528eaa2ffe828ac02b997b3dfbdb&=&format=webp&quality=lossless",
    "beh": "https://cdn.discordapp.com/attachments/1175180586030202940/1261506701153275926/image.png?ex=6695d82b&is=669486ab&hm=20d64d9dae37e141db381b5fe9db3653474971e1d6dadecd49b56a4441bf4bb3&",
    "kv": "---> [FFERA - Western Altepa Desert Weather](https://ffera.com/index.php?p=zone&id=125) <--- Please check if there is upcoming weather.",
}
ALL_HNMS = {
    "n": {
        "Fafnir": ":dragon_face: (****):",
        "Adamantoise": ":turtle: (****):",
        "Behemoth": ":zap: (****):",
        "King Arthro": ":crab::",
        "King Vinegarroon": ":scorpion::",
        "Bloodsucker": ":drop_of_blood::",
        "Shikigami Weapon": ":japanese_ogre::",
        "Simurgh": ":bird::",
        "Jormungand": ":ice_cube::chicken::ice_cube::",
        "Tiamat": ":fire::chicken::fire::",
        "Vrtra": ":skull::chicken::skull::",
    },
    "a": {
        "Fafnir": ":grey_question::dragon_face::grey_question: (****):",
        "Adamantoise": ":grey_question::turtle::grey_question: (****):",
        "Behemoth": ":grey_question::zap::grey_question: (****):",
        "King Arthro": ":grey_question::crab::grey_question::",
        "King Vinegarroon": ":grey_question::scorpion::grey_question::",
        "Bloodsucker": ":grey_question::drop_of_blood::grey_question::",
        "Shikigami Weapon": ":grey_question::japanese_ogre::grey_question::",
        "Simurgh": ":grey_question::bird::grey_question::",
        "Jormungand": ":grey_question::ice_cube::chicken::ice_cube::grey_question::",
        "Tiamat": ":grey_question::fire::chicken::fire::grey_question::",
        "Vrtra": ":grey_question::skull::chicken::skull::grey_question::",
    },
    "d": {
        "Fafnir": ":moneybag::dragon_face::moneybag: (****):",
        "Adamantoise": ":moneybag::turtle::moneybag: (****):",
        "Behemoth": ":moneybag::zap::moneybag: (****):",
    },
    "t": {
        "Fafnir": ":gem::dragon_face::gem: (****):",
        "Adamantoise": ":gem::turtle::gem: (****):",
        "Behemoth": ":gem::zap::gem: (****):",
    },
}
