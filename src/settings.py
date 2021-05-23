from typing import Dict, Set
import discord
from discord.ext import commands
import re
import json
import os
import aiohttp

class SettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def parse_message(self, message: str):
        match: re.Match = re.match(r"```json\n(.+)\n```", message)
        if match is None:
            return None
        raw_json: str = match.group(1)

        return json.loads(raw_json)

    def create_reaction_embed(self, data: Dict, guild: discord.Guild):
        embed = discord.Embed(title=data["title"], description=data["description"])
        colorHex = data["colorHex"][1:]
        embed.color = discord.Color(int(colorHex, 16))

        for datum in data["roleData"]:
            role: discord.Role = discord.utils.get(guild.roles, name=datum["roleName"])
            if role is None:
                return datum["roleName"]
            embed.add_field(name=datum["roleSummary"], value=f"{role.mention}\n{datum['roleEmoji']}　絵文字を押してください。", inline=False)

        if data["isExclusive"]:
            embed.set_footer(text="これらの役職は同時に複数取得できません。")
        return embed

    async def edit_reaction(self, embed: discord.Embed, data: Dict, message_id: int):
        if message_id is not None:
            message: discord.Message = await self.bot.reaction_channel.fetch_message(message_id)
            await message.edit(embed=embed)
        else:
            message: discord.Message = await self.bot.reaction_channel.send(embed=embed)
            gspread_app_url = os.getenv("GSPREAD_APP_URL")
            async with aiohttp.ClientSession() as session:
                await session.post(gspread_app_url, data={"sheetIndex": data["sheetIndex"], "messageId": message.id})

        await message.clear_reactions()
        for datum in data["roleData"]:
            await message.add_reaction(datum["roleEmoji"])

    @commands.Cog.listener(name="on_message")
    async def setting(self, message: discord.Message):
        if message.channel.id == 829630617133121546 and message.author.id == 845206507665489920:
            data = self.parse_message(message.content)
            if data is None:
                await message.channel.send("エラー：JSONデータが不正でした。")
                return

            send_payload = self.create_reaction_embed(data, message.guild)
            if not isinstance(send_payload, discord.Embed):
                await message.channel.send(f"エラー： {send_payload} という名前のロールは存在しません。Discordの サーバー管理 ＞ ロール管理 から名前をコピーしてください。")
                return

            if data["type"] == "reaction":
                await self.edit_reaction(send_payload, data, data["messageId"])
            

def setup(bot):
    bot.add_cog(SettingsCog(bot))