from discord.ext import commands
import sqlite3
import os
from discord_slash import cog_ext, SlashContext, SlashCommand
import textwrap
import re
import signal
import discord
import emoji

from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType

class FriendDB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS friends(discord_id INTEGER PRIMARY KEY, friend_code STRING)")

    def add_user(self, user_id: int, friend_code: str):
        self.cur.execute("INSERT INTO friends values(?, ?)", (user_id, friend_code))
        self.conn.commit()

    def get_user_friend_code(self, user_id: int):
        self.cur.execute("SELECT friend_code FROM friends WHERE discord_id = ?", (user_id, ))
        result = self.cur.fetchone()
        if result is None:
            return result
        else:
            return result[0]        

    def connect_close(self):
        self.cur.close()
        self.conn.close()

    
def setup(bot):
    slash = SlashCommand(bot, sync_commands=True)

    guild_ids = [813577333516402728] # Put your server ID in this array.

    db_name = os.getenv("FRIEND_DATABASE_NAME")
    db = FriendDB(db_name)
    signal.signal(signal.SIGTERM, db.connect_close)

    @slash.subcommand(
        base="friend",
        name="add", 
        description="フレンドコードを追加します。",
        base_desc="フレンドコードに関する機能を提供します。",
        guild_ids=guild_ids,
        options=[
            create_option(
                "フレンドコード",
                "登録するフレンドコード。",
                option_type=SlashCommandOptionType.STRING,
                required=True
            )
        ])
    async def _friend_add(ctx: SlashContext, friend_code_raw: str):
        await ctx.respond()
        code = db.get_user_friend_code(ctx.author.id)
        if code is not None:
            await ctx.send(content="すでにフレンドコードが登録されています。")
            return

        result = re.match(r"\d{4}-\d{4}-\d{4}", friend_code_raw)
        if not result:
            await ctx.send(
                content="適切な形式のフレンドコードが送信されませんでした。正しい形式でもう一度送信してください。\n コードの例： `1234-5678-9012`"
                )
            return

        db.add_user(ctx.author.id, result.group())
        await ctx.send(content="フレンドコードをデータベースに登録しました。")

    @slash.subcommand(
        base="friend",
        name="show",
        description="ユーザーのフレンドコードを表示します。",
        base_desc="フレンドコードに関する機能を提供します。",
        guild_ids=guild_ids,
        options=[
            create_option(
                "ユーザー",
                "フレンドコードを取得するユーザー。",
                option_type=SlashCommandOptionType.USER,
                required=True
            )
        ]
    )
    async def _friend_show(ctx: SlashContext, user: discord.Member):
        await ctx.respond()
        code = db.get_user_friend_code(user.id)

        if code is None:
            await ctx.send(embed=discord.Embed(
                title="検索結果",
                description=emoji.emojize(
                    f"ユーザー {user.mention} のフレンドコードは見つかりませんでした :cry:\nまだフレンドコードが登録されていない可能性があります。", 
                    use_aliases=True),
                color=discord.Color.red()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="検索結果",
                description=f"ユーザー {user.mention} さん のフレンドコードは {code} です。",
                color=discord.Color.green()
            ))