# Server Globals
TOKEN = ''
GUILDID = 876434275661135982
HNMTIMES = 1110052586561744896
BOTCOMMANDS = 1110076161201020949
CAMPPINGS = 1138678403730526379
HNMCATEGORYID = 1110230423272952008

# Command Gloabals
FAFNIR = ['faf', 'fafnir']
ADAMANTOISE = ['ad', 'ada', 'adam', 'adamantoise']
BEHEMOTH = ['beh', 'behe', 'behemoth']
KA = ['ka', 'kinga']
SIM = ['sim']
SHIKI = ['shi', 'shiki', 'shikigami']
KV = ['kv', 'kingv', 'kingvine']
VRTRA = ['vrt', 'vrtr', 'vrtra']
TIAMAT = ['tia', 'tiam', 'tiamat']
JORM = ['jor', 'jorm', 'jormundgand']

ALIASES = [FAFNIR, ADAMANTOISE, BEHEMOTH, KA, SIM, SHIKI, KV, VRTRA, TIAMAT, JORM]
HNMCOMMANDS = FAFNIR + ADAMANTOISE + BEHEMOTH + KA + SIM + SHIKI + KV + VRTRA + TIAMAT + JORM

# Time Related Globals
DATEFORMATS = [ # List of accepted date formats
            "%Y-%m-%d %I%M%S %p", "%Y%m%d %I%M%S %p", "%y%m%d %I%M%S %p", "%m%d%Y %I%M%S %p", "%m%d%Y %I%M%S %p",
            "%Y-%m-%d %I:%M:%S %p", "%Y%m%d %I:%M:%S %p", "%y%m%d %I:%M:%S %p", "%m%d%Y %I:%M:%S %p", "%m%d%Y %I:%M:%S %p",
            "%Y-%m-%d %H%M%S", "%Y%m%d %H%M%S", "%y%m%d %H%M%S", "%m%d%Y %H%M%S", "%m%d%Y %H%M%S",
            "%Y-%m-%d %H:%M:%S", "%Y%m%d %H:%M:%S", "%y%m%d %H:%M:%S", "%m%d%Y %H:%M:%S", "%m%d%Y %H:%M:%S",
            "%Y-%m-%d %h%M%S", "%Y%m%d %h%M%S", "%y%m%d %h%M%S", "%m%d%Y %h%M%S", "%m%d%Y %h%M%S",
            "%Y-%m-%d %h:%M:%S", "%Y%m%d %h:%M:%S", "%y%m%d %h:%M:%S", "%m%d%Y %h:%M:%S", "%m%d%Y %h:%M:%S"
        ]

TIMEFORMATS = [
            "%I%M%S %p", "%I:%M:%S %p", "%H%M%S", "%H:%M:%S", "%h:%M:%S"
        ]

TZ = 'America/Los_Angeles'

# Genral Setting Globals
MAKECHANNEL = 20
ARCHIVEWAIT = 5

# HNM Related Globals
GW = ["Jormungand", "Tiamat", "Vrtra"]
GK = ["Fafnir", "Adamantoise", "Behemoth"]
HQ = {'Fafnir': 'Nidhogg', 'Adamantoise': 'Aspidochelone', 'Behemoth': 'King Behemoth'}
SPAWNGOUP1 = GK + ["King Arthro", "Simurgh"] # 22HR Spawns
SPAWNGOUP2 = ["Shikigami Weapon", "King Vinegarroon"]
ALL_HNMS = {
    'n':{
        'Fafnir':           ':dragon_face: (****):',
        'Adamantoise':      ':turtle: (****):',
        'Behemoth':         ':zap: (****):',
        'King Arthro':      ':crab::',
        'King Vinegarroon': ':scorpion::',
        'Shikigami Weapon': ':japanese_ogre::',
        'Simurgh':          ':bird::',
        'Jormungand':       ':ice_cube::chicken::ice_cube::',
        'Tiamat':           ':fire::chicken::fire::',
        'Vrtra':            ':skull::chicken::skull::',
        },
    'a':{
        'Fafnir':           ':grey_question::dragon_face::grey_question: (****):',
        'Adamantoise':      ':grey_question::turtle::grey_question: (****):',
        'Behemoth':         ':grey_question::zap::grey_question: (****):',
        'King Arthro':      ':grey_question::crab::grey_question::',
        'King Vinegarroon': ':grey_question::scorpion::grey_question::',
        'Shikigami Weapon': ':grey_question::japanese_ogre::grey_question::',
        'Simurgh':          ':grey_question::bird::grey_question::',
        'Jormungand':       ':grey_question::ice_cube::chicken::ice_cube::grey_question::',
        'Tiamat':           ':grey_question::fire::chicken::fire::grey_question::',
        'Vrtra':            ':grey_question::skull::chicken::skull::grey_question::',
        },
    'd':{
        'Fafnir':           ':moneybag::dragon_face::moneybag: (****):',
        'Adamantoise':      ':moneybag::turtle::moneybag: (****):',
        'Behemoth':         ':moneybag::zap::moneybag: (****):',
        },
    't':{
        'Fafnir':           ':gem::dragon_face::gem: (****):',
        'Adamantoise':      ':gem::turtle::gem: (****):',
        'Behemoth':         ':gem::zap::gem: (****):',
        },
    }