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
        if message.channel != 813598124387860580:
            return

        voice_path = f"{message.channel.id}{message.id}.wav"

        with tempfile.NamedTemporaryFile(mode='w+') as tmp:
            tmp.write(message.content)
            tmp.seek(0)
            command = f"open_jtalk -x {self.dic_path} -m {self.model_path} -r 1.0 -ow {voice_path} {tmp.name}"
            print(command)
            proc = subprocess.run(
                command,
                shell  = True,
            )

            source = discord.FFmpegOpusAudio(voice_path)
            voice: discord.VoiceClient = await message.author.voice.channel.connect()
            voice.play(source)

def setup(bot):
    bot.add_cog(ReaderCog(bot))