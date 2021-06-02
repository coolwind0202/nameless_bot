import os
import asyncio
from threading import Thread

import discord
from discord.ext import commands
from discord_slash import SlashCommand

PATHS = (
    "tweet",
    "friend",
    "role",
    "settings",
    "reader",
    "web.backend.endpoint",
)

class NameLessBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slash = SlashCommand(self, sync_commands=True)
        for path in PATHS:
            self.load_extension(path)
        
    async def on_ready(self):
        print("ready...")

bot = NameLessBot(command_prefix="/", intents=discord.Intents.all())

bot.run(os.getenv("DISCORD_TOKEN"))