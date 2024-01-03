# Configuration file
kv_open = []
processed_channels_list = []
running_tasks = []

# Alias descriptions
day = "Used for HQ system, can be set to 0 for mobs that do not HQ"
timestamp = "ToD of the mob in your TZ."

# Define tables for used for determining the pop location
location_tables = {
    "faf": {
        "z": "Zi'Tah",
        "zi": "Zi'Tah",
        "zitah": "Zi'Tah",
        "r": "Ro'Maeve",
        "ro": "Ro'Maeve",
        "romaeve": "Ro'Maeve",
        "a": "Aery",
        "da": "Aery",
        "aery": "Aery",
        "t": "Tree",
        "tr": "Tree",
        "tree": "Tree"
    },
    "ada": {
        "c": "Cape",
        "cape": "Cape",
        "terrigan": "Cape",
        "v": "VoS",
        "vos": "VoS",
        "valley": "VoS",
        "k": "Kuftal",
        "kuf": "Kuftal",
        "kuftal": "Kuftal",
        "g": "Gustav",
        "gus": "Gustav",
        "gustav": "Gustav"
    },
    "beh": {
        "r": "Rolanberry",
        "rolan": "Rolanberry",
        "rolanberry": "Rolanberry",
        "b": "Batallia",
        "bat": "Batallia",
        "batallia": "Batallia",
        "s": "Sauromugue",
        "sau": "Sauromugue",
        "sauro": "Sauromugue",
        "d": "Dominion",
        "bd": "Dominion",
        "dom": "Dominion"
    }
}
