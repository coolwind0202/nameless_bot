import discord
import os
from discord.ext import commands
import traceback
import datetime
from discord_slash import SlashCommand

import re
import signal

from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType
from discord_slash import cog_ext, SlashContext
from friend import FriendDB

PATHS = (
    #"tweet",
    "friend",
)

class NameLessBot(commands.Bot):
    async def on_ready(self):
        for path in PATHS:
            self.load_extension(path)
        print("ready...")
    

bot = NameLessBot(command_prefix="/")


print(os.getenv("DISCORD_TOKEN"))




bot.run(os.getenv("DISCORD_TOKEN"))