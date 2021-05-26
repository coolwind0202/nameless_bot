import asyncio
from asyncio.queues import Queue
import subprocess
import tempfile
import dataclasses

import discord
from discord import guild
from discord.ext import commands

from discord_slash import SlashContext, SlashCommand

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
        await asyncio.sleep(0)
        element: QueueElement = await self.message_queue.get()
        voice = element.guild.voice_client

        if voice is None:
            return
        
        output =  tempfile.NamedTemporaryFile(suffix=".wav")
        command = f"open_jtalk -x {self.dic_path} -m {self.model_path} -r 1.0 -ow {output.name}"
        print(command)
        proc = subprocess.run(
            command, shell = True, input=element.content.encode()
        )
        output.seek(0)

        source = discord.FFmpegOpusAudio(output.name)

        def after(e):
            output.close()
            self.bot.loop.create_task(self.worker())

        voice.play(source, after=after)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.voice_client is None:
            return
        await self.message_queue.put(QueueElement(message.guild, message.content))

def setup(bot):
    slash = SlashCommand(bot, sync_commands=True)
    guild_ids = [813577333516402728]

    @slash.slash(
        name="join",
        guild_ids = guild_ids,
        description="このコマンドを実行したメンバーのボイスチャンネルで、読み上げを開始します。"
    )
    async def _join(ctx: SlashContext):
        if ctx.author.voice and ctx.author.voice.channel:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send(content="このコマンドは、ボイスチャンネルに参加してから実行してください。")
            return
        await ctx.send(content=f"チャンネル {ctx.author.voice.channel.name} に参加しました。")
    
    @slash.slash(
        name="leave",
        guild_ids = guild_ids,
        description="読み上げを終了します。"
    )
    async def _leave(ctx: SlashContext):
        if ctx.guild.voice_client is not None:
            await ctx.guild.voice_client.disconnect()
        
        await ctx.send(content=f"チャンネル {ctx.guild.name} での読み上げを終了しました。")

    bot.add_cog(ReaderCog(bot))