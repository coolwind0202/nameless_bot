import sqlite3
import os
import re
import signal
import dataclasses
import asyncio

import emoji
import discord
from discord.ext import commands

from discord_slash import SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType

@dataclasses.dataclass
class FriendCodeObject:
    code: str
    memo: str

class FriendDB:
    """
    データベースの一般的な処理を定義します。
    """

    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS friend_code(code STRING PRIMARY KEY, user_id INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS friend_code_memo(code STRING PRIMARY KEY, memo STRING)")

    def exists_friend_code(self, friend_code: str) -> bool:
        """
        指定されたフレンドコード friend_code がすでにデータベースに登録されているかどうかを返します。
        """
        self.cur.execute("SELECT code FROM friend_code WHERE code = ?", (friend_code, ))
        exists = self.cur.fetchone()
        return exists is not None

    def exists_memo(self, friend_code: str) -> bool:
        """
        指定されたフレンドコード friend_code に備考が設定されているかどうかを返します。
        """
        self.cur.execute("SELECT memo FROM friend_code_memo WHERE code = ?", (friend_code, ))
        exists = self.cur.fetchone()
        return exists is not None

    def add_memo(self, friend_code: str, memo: str) -> None:
        """
        指定されたフレンドコード friend_code に対して、内容が memo の備考を設定します。
        """
        self.cur.execute("INSERT INTO friend_code_memo values(?, ?)", (friend_code, memo))
    
    def update_memo(self, friend_code: str, memo: str) -> None:
        """
        指定されたフレンドコード friend_code に対して、内容が memo の備考を上書きします。
        """
        self.cur.execute("UPDATE friend_code_memo SET memo = ? WHERE code = ?", (memo, friend_code))

    def set_memo(self, friend_code:str, memo: str) -> None:
        """
        指定されたフレンドコード friend_code に対して、内容が memo の備考を設定します。
        もしフレンドコードが存在している場合には UPDATE 文を使用するので、通常はこのメソッドを使います。
        """
        if self.exists_memo(friend_code):
            self.update_memo(friend_code, memo)
        else:
            self.add_memo(friend_code, memo)
        self.conn.commit()

    def add_user_friend_code(self, user_id: int, friend_code: str) -> None:
        """
        指定されたユーザーID user_id に対して、フレンドコード friend_code を設定します。
        """
        self.cur.execute("INSERT INTO friend_code values(?, ?)", (friend_code, user_id))
        self.conn.commit()

    def remove_user_friend_code(self, friend_code: str) -> None:
        """
        指定されたフレンドコード friend_code を削除します。
        """
        self.cur.execute("DELETE FROM friend_code WHERE code = ?", (friend_code, ))
        self.cur.execute("DELETE FROM friend_code_memo WHERE code = ?", (friend_code, ))
        self.conn.commit()

    def get_user_friend_codes(self, user_id: int):
        """
        指定されたユーザーID user_id から、該当ユーザーのフレンドコードとその備考をまとめたオブジェクトの、リストを返します。
        """
        self.cur.execute("SELECT code FROM friend_code WHERE user_id = ?", (user_id, ))
        codes_wrapped = self.cur.fetchall()
        code_objects = []
        for code_wrapped in codes_wrapped:
            raw_code = code_wrapped[0]
            self.cur.execute("SELECT memo FROM friend_code_memo WHERE code = ?", (raw_code, ))
            memo = self.cur.fetchone()
            if memo is not None:
                raw_memo = memo[0]
                code_objects.append(FriendCodeObject(raw_code, raw_memo))
            else:
                code_objects.append(FriendCodeObject(raw_code, ""))
        return code_objects

    def connect_close(self) -> None:
        """
        データベースとの接続を閉じます。
        """
        
        self.cur.close()
        self.conn.close()
    
def setup(bot):
    slash = SlashCommand(bot, sync_commands=True)

    guild_ids = [813577333516402728] # コマンドを追加するサーバーのIDリスト

    db_name = os.getenv("FRIEND_DATABASE_NAME")
    db = FriendDB(db_name)
    signal.signal(signal.SIGTERM, db.connect_close) # プログラムの終了直前にデータベースとの接続を閉じておく
    
    @slash.subcommand(
        base="friend",
        name="add", 
        description="フレンドコードを追加します。",
        base_desc="フレンドコードに関する機能を提供します。",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="フレンドコード",
                description="登録するフレンドコード。",
                option_type=SlashCommandOptionType.STRING,
                required=True
            )
        ])
    async def _friend_add(ctx: SlashContext, friend_code_raw: str):
        await ctx.respond()

        result = re.match(r"\d{4}-\d{4}-\d{4}", friend_code_raw)
        if not result:
            await ctx.send(
                content="適切な形式のフレンドコードが送信されませんでした。正しい形式でもう一度送信してください。\n コードの例： `1234-5678-9012`"
                )
            return

        db.add_user_friend_code(ctx.author.id, result.group())
        await ctx.send(content="フレンドコードをデータベースに登録しました。")
        await ctx.send(
            content="ヒント： `/friend memo` コマンドを使って、フレンドコードにメモを設定できます。メインアカウントとサブアカウントの区別などにお使いください。",
            hidden=True)

    @slash.subcommand(
        base="friend",
        name="delete",
        description="既存のフレンドコードを削除します。",
        base_desc="フレンドコードに関する機能を提供します。",
        guild_ids=guild_ids
    )
    async def _friend_delete(ctx: SlashContext):
        await ctx.respond()

        codes: list[FriendCodeObject] = db.get_user_friend_codes(ctx.author.id)
        if not codes:
            await ctx.send(content="まだフレンドコードが登録されていません。")
            return
        embed = discord.Embed()
        numbers_emoji_raw = [":one:", ":two:", ":three:", ":four:"]
        numbers_emoji = []
        for code_object, number in zip(codes, numbers_emoji_raw):
            em = emoji.emojize(number, use_aliases=True)
            embed.add_field(name=em, value=f"{code_object.code} / {code_object.memo}")
            numbers_emoji.append(em)

        bot_message = await ctx.send(content="削除するフレンドコードを、リアクションで指定してください。", embed=embed)
        
        for em in numbers_emoji:
            await bot_message.add_reaction(em)

        def reaction_check(reaction: discord.Reaction, user: discord.User):
            return user == ctx.author and reaction.message.id == bot_message.id

        reaction, _ = await bot.wait_for("reaction_add", check=reaction_check)
        select_index = numbers_emoji.index(str(reaction.emoji))
        target_code = codes[select_index].code

        db.remove_user_friend_code(target_code)
        await ctx.send("フレンドコードの削除が完了しました。")

    @slash.subcommand(
        base="friend",
        name="memo",
        description="既存のフレンドコードにメモを設定します。",
        base_desc="フレンドコードに関する機能を提供します。",
        options=[
            create_option(
                name="メモ内容",
                description="設定するメモの内容",
                option_type=SlashCommandOptionType.STRING, 
                required=True
            )
        ],
        guild_ids=guild_ids)
    async def _friend_memo(ctx: SlashContext, memo):
        await ctx.respond()

        codes: list[FriendCodeObject] = db.get_user_friend_codes(ctx.author.id)
        if not codes:
            await ctx.send(content="まだフレンドコードが登録されていません。")
            return

        embed = discord.Embed()
        numbers_emoji_raw = [":one:", ":two:", ":three:", ":four:"]
        numbers_emoji = []
        for code_object, number in zip(codes, numbers_emoji_raw):
            em = emoji.emojize(number, use_aliases=True)
            embed.add_field(name=em, value=f"{code_object.code} / {code_object.memo}")
            numbers_emoji.append(em)

        bot_message = await ctx.send(content="メモを設定するフレンドコードを、リアクションで指定してください。", embed=embed)
        
        for em in numbers_emoji:
            await bot_message.add_reaction(em)

        def reaction_check(reaction: discord.Reaction, user: discord.User):
            return user == ctx.author and reaction.message.id == bot_message.id

        reaction, _ = await bot.wait_for("reaction_add", check=reaction_check)
        select_index = numbers_emoji.index(str(reaction.emoji))
        target_code = codes[select_index].code

        db.set_memo(target_code, memo)
        await ctx.send("メモ内容の設定が完了しました。")

    @slash.subcommand(
        base="friend",
        name="show",
        description="ユーザーのフレンドコードを表示します。",
        base_desc="フレンドコードに関する機能を提供します。",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="ユーザー",
                description="フレンドコードを取得するユーザー。",
                option_type=SlashCommandOptionType.USER,
                required=True
            )
        ]
    )
    async def _friend_show(ctx: SlashContext, user: discord.Member):
        await ctx.respond()
        codes: list[FriendCodeObject] = db.get_user_friend_codes(user.id)

        if not codes:
            await ctx.send(embed=discord.Embed(
                title="検索結果",
                description=emoji.emojize(
                    f"ユーザー {user.mention} さんのフレンドコードは見つかりませんでした :cry:\nまだフレンドコードが登録されていない可能性があります。", 
                    use_aliases=True),
                color=discord.Color.red()
            ))
            return
        content = "\n".join([code.code + (f" ( {code.memo} )" if code.memo else "") for code in codes]) # フレンドコードリスト用文字列

        await ctx.send(embed=discord.Embed(
            title="検索結果",
            description=f"ユーザー {user.mention} さんのフレンドコードが {len(codes)} 件見つかりました。\n\n{content}",
            color=discord.Color.green()
        ))