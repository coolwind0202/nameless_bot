import discord
import os
from discord.ext import commands
import traceback
import datetime

PATHS = (
    "tweet",
)

class NameLessBot(commands.Bot):
    async def on_ready(self):
        for path in PATHS:
            self.load_extension(path)
        print("ready...")

    async def on_error(self, error):
        orig_error = getattr(error, "original", error)
        error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
        print(f"エラーが発生 ( {datetime.datetime.now()} )：")
        print(error_msg)
    

bot = NameLessBot(command_prefix="/")
bot.run(os.getenv("DISCORD_TOKEN"))