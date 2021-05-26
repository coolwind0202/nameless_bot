import subprocess
import tempfile

import discord
from discord.ext import commands

class ReaderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dic_path = "/var/lib/mecab/dic/open-jtalk/naist-jdic/"
        self.model_path = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != 813598124387860580:
            return

        voice_path = f"{message.channel.id}{message.id}.wav"

        content: str = message.content
        command = f"open_jtalk -x {self.dic_path} -m {self.model_path} -r 1.0 -ow {voice_path}"
        print(command)
        proc = subprocess.run(
            command, shell = True, input=content.encode()
        )

        source = discord.FFmpegOpusAudio(voice_path)
        if message.guild.voice_client is None:
            voice: discord.VoiceClient = await message.author.voice.channel.connect()
        else:
            voice: discord.VoiceClient = message.guild.voice_client
        voice.play(source)

def setup(bot):
    bot.add_cog(ReaderCog(bot))