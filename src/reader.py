import asyncio
from asyncio.queues import Queue
import subprocess
import tempfile
import dataclasses

import discord
from discord.ext import commands

@dataclasses.dataclass
class QueueElement:
    guild: discord.Guild
    content: str

class ReaderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dic_path = "/var/lib/mecab/dic/open-jtalk/naist-jdic/"
        self.model_path = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"
        self.message_queue = asyncio.Queue()
        self.bot.loop.create_task(self.worker())

    async def worker(self):
        while True:
            await asyncio.sleep(0)
            element: QueueElement = await self.message_queue.get()
            voice = QueueElement.guild.voice_client

            if voice is None:
                continue
            
            output =  tempfile.NamedTemporaryFile(suffix=".wav")
            command = f"open_jtalk -x {self.dic_path} -m {self.model_path} -r 1.0 -ow {output.name}"
            print(command)
            proc = subprocess.run(
                command, shell = True, input=element.content.encode()
            )
            output.seek(0)

            source = discord.FFmpegOpusAudio(output.name)
            voice.play(source, after=lambda e: output.close())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != 813598124387860580:
            return
        await self.message_queue.put(QueueElement(message.guild, message.content))        

def setup(bot):
    bot.add_cog(ReaderCog(bot))