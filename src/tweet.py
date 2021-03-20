import tweepy
from discord.ext import commands, tasks
import requests
import os
import asyncio

screen_name = os.getenv("SPLATOON_SCREEN_NAME")
channel = None

class StatusEventListener(tweepy.StreamListener):
    async def handle_status(self, status):
        if status.user.screen_name != screen_name or channel is None:
            return
        print(status.text)
        tweet_url = f"https://twitter.com/{screen_name}/status/{status.id_str}"
        await channel.send(tweet_url)

    def on_status(self, status):
        asyncio.create_task(handle_status())

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

        # returning non-False reconnects the stream, with backoff.

def start_stream():
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    listener = StatusEventListener()
    my_stream = tweepy.Stream(auth=auth, listener=listener)

    my_stream.filter(follow=[os.getenv("SPLATOON_ID")],  is_async=True, stall_warnings=True)

class TweetCog(commands.Cog):
    def __init__(self, bot):
        global channel
        self.bot = bot
        channel = self.bot.get_channel(os.getenv("TWEET_NOTICE_CHANNEL_ID"))
        start_stream()

def setup(bot):
    bot.add_cog(TweetCog(bot))