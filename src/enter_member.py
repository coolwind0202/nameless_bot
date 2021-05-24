import asyncio
import os

import discord
from discord.ext import commands

import emoji

class EnterMemberCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        asyncio.get_event_loop().create_task(self.set_rule_channel_and_role())
    
    async def set_rule_channel_and_role(self):
        await self.bot.wait_until_ready()
        self.rule_channel = self.bot.get_channel(int(os.getenv("RULE_CHANNEL_ID")))
        self.rule_role = discord.utils.get(self.rule_channel.guild.roles, name="メンバー")

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def approve_member(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id != self.rule_channel.id:
            return

        if str(payload.emoji) == emoji.emojize(":thumbsup:", use_aliases=True):
            await payload.member.add_roles(self.rule_role)

def setup(bot):
    bot.add_cog(EnterMemberCog(bot))