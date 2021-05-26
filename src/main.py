import discord
from discord.ext import commands

import os

PATHS = (
    "tweet",
    "friend",
    "role",
    "settings",
    "enter_member",
    "reader",
)

class NameLessBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for path in PATHS:
            self.load_extension(path)
        
    async def on_ready(self):
        print("ready...")

bot = NameLessBot(command_prefix="/")
bot.run(os.getenv("DISCORD_TOKEN"))