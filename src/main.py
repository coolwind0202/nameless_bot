from discord.ext import commands

import os

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
bot.run(os.getenv("DISCORD_TOKEN"))