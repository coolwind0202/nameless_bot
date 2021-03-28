import tweepy
from discord.ext import commands, tasks
import requests
import os
from threading import Thread
from queue import Queue
import asyncio
import traceback

screen_name = os.getenv("SPLATOON_SCREEN_NAME")
channel = None

class StatusEventListener(tweepy.StreamListener):
    def __init__(self, q = Queue()):
        num_worker_threads = 4
        self.q = q
        for _ in range(num_worker_threads):
             t = Thread(target=self.do_stuff)
             t.daemon = True
             t.start()

    def do_stuff(self):
        while True:
            status = self.q.get()
            tweet_url = f"https://twitter.com/{screen_name}/status/{status.id_str}"
            print(tweet_url)
            if status.user.screen_name != screen_name or channel is None:
                continue
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(channel.send(tweet_url))
            except RuntimeError:
                traceback.print_exc()
            self.q.task_done()

    def on_status(self, status):
        self.q.put(status)

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

    my_stream.filter(follow=[os.getenv("SPLATOON_ID")], is_async=True, stall_warnings=True)

class TweetCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        global channel

        self.bot = bot
        channel = self.bot.get_channel(int(os.getenv("TWEET_NOTICE_CHANNEL_ID")))
        start_stream()

def setup(bot):
    bot.add_cog(TweetCog(bot))