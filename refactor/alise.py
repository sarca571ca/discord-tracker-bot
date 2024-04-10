import discord
from src import client, settings

def main():
    token  = settings.TOKEN
    intents = discord.Intents.all()
    bot = client.Alise(command_prefix="!", intents=intents)

    bot.add_commands()

    bot.run(token)

if __name__ == "__main__":
    main()
