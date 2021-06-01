import os
import sqlite3
from threading import Thread
from collections import UserDict
from typing import Dict, List
import dataclasses
import asyncio
import secrets
import ast
from discord import message

from flask import Flask, redirect, url_for, g
from flask.templating import render_template
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized, AccessDenied
from flask_restful import Resource, Api, reqparse
from jwt.exceptions import DecodeError

import discord as discordpy
from discord.ext import commands

app = Flask(__name__, static_folder="../frontend/dist/static", template_folder="../frontend/dist")
api = Api(app)

app.config["SECRET_KEY"] = app.secret_key = secrets.token_bytes(32)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.

app.config["DISCORD_CLIENT_ID"] = 822365434128891924    # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = "jkNFlQmTf9i-ALTX6NzJnUtLwbRAtR3S"                # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://localhost:5000/callback"                 # URL to your callback endpoint.
app.config["DISCORD_BOT_TOKEN"] = "ODIyMzY1NDM0MTI4ODkxOTI0.YFRNfg.hICYm4H9IgSMnnmBoLrqbiEt5Kw"                    # Required to access BOT resources.


discord = DiscordOAuth2Session(app)

@dataclasses.dataclass()
class RoleData:
    role_id: str
    role_summary: str
    role_emoji: str

    def to_dict(self):
        return {
            "role_id": self.role_id,
            "role_summary": self.role_summary,
            "role_emoji": self.role_emoji,
        }

class RoleDB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS role_message(message_id BIGINT UNSIGNED PRIMARY KEY, summary STRING, description STRING, color_value INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS role(role_id BIGINT UNSIGNED PRIMARY KEY, message_id BIGINT UNSIGNED, role_summary STRING, role_emoji STRING)")

    def get_message_data(self, message_id: int) -> Dict:
        summary, description, color_value = self.cur.execute("SELECT summary, description, color_value, FROM role_message WHERE message_id = ?", (message_id,))
        data = {
            "message_id": message_id,
            "summary": summary,
            "description": description,
            "color_value": color_value,
            "roles": []
        }
        
        for (role_id, role_summary, role_emoji) in self.cur.execute("SELECT role_id, role_summary, role_emoji FROM role WHERE message_id = ?", (message_id,)):
            data["roles"].append({
                "role_id": role_id,
                "role_summary": role_summary,
                "role_emoji": role_emoji
            })
        return data

    def get_all_message_data(self) -> List[Dict]:
        data_list: List[Dict] = []

        '''
        for x in self.cur.execute("SELECT * FROM role_message"):
            print(x)
        '''

        role_messages = self.cur.execute("SELECT * FROM role_message").fetchall()
        
        for (message_id, summary, description, color_value) in role_messages:
            print(message_id)
            data = {
                "message_id": message_id,
                "summary": summary,
                "description": description,
                "color_value": color_value,
                "roles": []
            }
        
            for (role_id, role_summary, role_emoji) in self.cur.execute("SELECT role_id, role_summary, role_emoji FROM role WHERE message_id = ?", (message_id,)):
                data["roles"].append({
                    "role_id": role_id,
                    "role_summary": role_summary,
                    "role_emoji": role_emoji
                })

            data_list.append(data)
        return data_list

    def add_message_data(self, message_id: int, summary: str, description: str, color_value: int, roles: List[RoleData]):
        self.cur.execute("INSERT INTO role_message values(?, ?, ?, ?)", (message_id, summary, description, color_value))
        for role in roles:
            self.cur.execute("INSERT INTO role values(?, ?, ?, ?)", (role.role_id, message_id, role.role_summary, role.role_emoji))
        self.conn.commit()

    def update_message_data(self, message_id: int, summary: str, description: str, color_value:int, roles: List[RoleData]):
        self.cur.execute("UPDATE role_message SET summary = ?, description = ?, color_value = ? WHERE message_id = ?", (summary, description,color_value, message_id))
        for role in roles:
            self.cur.execute("UPDATE role SET role_summary = ?, message_id = ?, role_emoji = ? WHERE role_id = ?", (role.role_summary, message_id, role.role_emoji, role.role_id))
        self.conn.commit()

    def exists_message_data(self, message_id: int):
        self.cur.execute("SELECT message_id FROM role_message WHERE message_id = ?", (message_id,))
        exists = self.cur.fetchone()
        return exists is not None

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = RoleDB("rolelist.db")
    return db

def get_guild():
    # os.getenv("LUCIDA_GUILD_ID")
    guild = discord.bot.get_guild(int(os.getenv("LUCIDA_GUILD_ID")))
    return guild

class Roles(Resource):
    parser = reqparse.RequestParser()
    help_txt = "cannnot be blank."
    parser.add_argument("summary", required=True, help=f"summary {help_txt}")
    parser.add_argument("description", required=True, help=f"description {help_txt}")
    parser.add_argument("id", required=True, help=f"data of message id {help_txt}")
    parser.add_argument("color", required=True, help=f"color {help_txt}")
    parser.add_argument("roles", required=True, help=f"data of roles {help_txt}", action="append")

    def get(self):
        data = get_db().get_all_message_data()
        print(data)
        for (index, message_data) in enumerate(data):
            data[index]["message_id"] = str(message_data["message_id"])
            data[index]["color_value"] = str(discordpy.Color(message_data["color_value"]))

            for (order, role) in enumerate(message_data["roles"]):
                data[index]["roles"][order]["role_id"] = str(role["role_id"])
        return data

    def post(self):
        args = self.parser.parse_args()
        db = get_db()
        guild = get_guild()
        if guild is None:
            return '', 404

        summary = args["summary"]
        description = args["description"]
        color_value = int(args["color"][1:], 16)

        role_data_list = []
        for role_raw_data in args["roles"]:
            role = ast.literal_eval(role_raw_data)
            role_data_list.append(RoleData(role["id"]["rawID"], role["summary"], role["emoji"]))

        message_id_data = ast.literal_eval(args["id"])
        embed = create_embed(summary, description, color_value, role_data_list)

        if message_id_data["isDiscordID"]:
            # すでにメッセージを過去に投稿しているので、上書きする
            message_id = int(message_id_data["rawID"])
            db.update_message_data(message_id, summary, description, color_value, role_data_list)
            future = asyncio.run_coroutine_threadsafe(edit_message(message_id, embed), discord.bot.loop)
            return '', 201
        else:
            # 新規に投稿し、IDを返す.
            
            future: asyncio.Future = asyncio.run_coroutine_threadsafe(send_message(embed=embed), discord.bot.loop)
            message_id = future.result()
            db.add_message_data(message_id, summary, description, color_value, role_data_list)
            return str(message_id), 201

class RoleDiscordData(Resource):
    def get(self):
        guild = get_guild()
        if guild is None:
            return []

        roles = [role for role in guild.roles if not role.is_default() and not role.is_bot_managed()]
        
        return { str(role.id): { "name": role.name, "color": str(role.color)} for role in roles}

class UserData(Resource):
    def get(self):
        user = discord.fetch_user()
        return { "avatar_url": user.avatar_url, "username": user.username }

api.add_resource(Roles, "/api/roles")
api.add_resource(RoleDiscordData, "/api/roledata")
api.add_resource(UserData, "/api/user")


@app.route("/logout/")
def logout():
    discord.revoke()
    return redirect(url_for("top_page"))

@app.route("/login/")
def login():
    return discord.create_session()

@app.route("/callback")
def callback():
    discord.callback()
    return redirect(url_for(".settings"))

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

@app.errorhandler(AccessDenied)
def redirect_denied(e):
    return redirect(url_for("top_page"))

@app.errorhandler(DecodeError)
def decode_error(e):
    return redirect(url_for("settings"))

@app.route("/")
def top_page():
    return render_template("top.html")

@app.route("/settings/")
@requires_authorization
def settings():
    return render_template('index.html')

async def send_message(embed: discordpy.Embed) -> int:
    channel_id = int(os.getenv("REACTION_CHANNEL_ID"))
    if (channel := discord.bot.get_channel(channel_id)) is None:
        channel = await discord.bot.fetch_channel(channel_id)

    message = await channel.send(embed=embed)
    return message.id

async def edit_message(message_id, embed: discordpy.Embed):
    channel_id = int(os.getenv("REACTION_CHANNEL_ID"))
    if (channel := discord.bot.get_channel(channel_id)) is None:
        channel = await discord.bot.fetch_channel(channel_id)

    message = await channel.fetch_message(message_id)
    await message.edit(embed=embed)

def create_embed(summary, description, color_value, roles: List[RoleData]) -> discordpy.Embed:
    embed = discordpy.Embed(title=summary, description=description, color=discordpy.Color(color_value))
    for role in roles:
        embed.add_field(name=role.role_summary, value=f"<@&{role.role_id}>\n{role.role_emoji}　絵文字を押してください。", inline=False)
    return embed


def setup(bot: commands.Bot):
    discord.bot = bot
    Thread(target=app.run).start()