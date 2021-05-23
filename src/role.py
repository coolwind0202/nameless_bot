import re

import discord
from discord.ext import commands

import emoji

class RoleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def find_roles(self, embed: discord.Embed, guild: discord.Guild):
        reaction_to_role = {}
        for field in embed.fields:
            emoji_list = emoji.emoji_lis(field.value)
            if not emoji_list:
                continue

            reaction = emoji_list[0]["emoji"]

            match: re.Match = re.match(r"<@&(.+)>",field.value)
            if match is None:
                continue
            role_id: str = match.group(1)
            role: discord.Role = guild.get_role(int(role_id))
            if role is not None:
                reaction_to_role[reaction] = role
        return reaction_to_role

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def process_role_reaction(self, payload: discord.RawReactionActionEvent):
        reaction = str(payload.emoji)
        if payload.channel_id != self.bot.reaction_channel.id:
            return

        message: discord.Message = await self.bot.reaction_channel.fetch_message(payload.message_id)
        reaction_to_role = self.find_roles(message.embeds[0], message.guild)
        
        if not reaction_to_role:
            return
        if payload.member != self.bot.user:
            if message.embeds[0].footer != discord.Embed.Empty and message.embeds[0].footer.text != discord.Embed.Empty:
                await payload.member.remove_roles(*reaction_to_role.values())

            role = reaction_to_role.get(reaction)
            if role is not None:
                if role in payload.member.roles:
                    await payload.member.remove_roles(role)
                else:
                    await payload.member.add_roles(role)

            user_reaction = discord.utils.get(message.reactions, emoji=reaction)
            await user_reaction.remove(payload.member)

def setup(bot):
    bot.add_cog(RoleCog(bot))