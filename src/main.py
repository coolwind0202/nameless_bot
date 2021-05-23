import discord
from discord.ext import commands

import os

PATHS = (
    #"tweet",
    "friend",
    "role",
    "settings",
)

class NameLessBot(commands.Bot):
    async def on_ready(self):
        for path in PATHS:
            self.load_extension(path)
        self.reaction_channel = self.get_channel(813583047609942026)
        print("ready...")

bot = NameLessBot(command_prefix="/")
bot.run(os.getenv("DISCORD_TOKEN"))