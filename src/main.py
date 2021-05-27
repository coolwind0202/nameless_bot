import os
import asyncio
from threading import Thread

import discord
from discord.ext import commands
from discord_slash import SlashCommand

#from web.backend import endpoint

PATHS = (
    "tweet",
    "friend",
    "role",
    "settings",
    "reader"
)

class NameLessBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slash = SlashCommand(self, sync_commands=True)
        for path in PATHS:
            self.load_extension(path)
        
    async def on_ready(self):
        print("ready...")

bot = NameLessBot(command_prefix="/")

#Thread(target=endpoint.setup, args=(bot,)).start()

bot.run(os.getenv("DISCORD_TOKEN"))