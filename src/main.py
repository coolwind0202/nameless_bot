import discord
from discord.ext import commands
from discord_slash import SlashCommand

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
        self.slash = SlashCommand(bot, sync_commands=True)
        for path in PATHS:
            self.load_extension(path)
        
    async def on_ready(self):
        print("ready...")

bot = NameLessBot(command_prefix="/")
bot.run(os.getenv("DISCORD_TOKEN"))