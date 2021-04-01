import tweepy
from discord.ext import commands, tasks
import requests
import os
from threading import Thread
from queue import Queue
import asyncio
import traceback
import urllib3
import http

screen_name = os.getenv("SPLATOON_SCREEN_NAME")
print(screen_name)
channel = None

class StatusEventListener(tweepy.StreamListener):
    def __init__(self, loop, error_callback, q = Queue()):
        super().__init__()
        self.loop = loop
        self.error_callback = error_callback
        self.q = q
        num_worker_threads = 4
        for _ in range(num_worker_threads):
             t = Thread(target=self.do_stuff)
             t.daemon = True
             t.start()

    def do_stuff(self):
        while True:
            status = self.q.get()
            tweet_url = f"https://twitter.com/{screen_name}/status/{status.id_str}"
            if status.user.screen_name != screen_name or channel is None:
                continue
            rt = status._json.get("retweeted_status")
            if rt is not None:
                if rt["user"]["name"] != screen_name:
                    tweet_content = f"{status.user.name} さんがリツイートしました： {tweet_url}"
            else:
                tweet_content = f"{status.user.name} さんがツイートしました： {tweet_url}"

            asyncio.run_coroutine_threadsafe(channel.send(tweet_content), self.loop)
            self.q.task_done()
            
    def on_status(self, status):
        self.q.put(status)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            print("error-code: 420")
            return False

        # returning non-False reconnects the stream, with backoff.

    def on_exception(self, info):
        asyncio.run_coroutine_threadsafe(channel.send(f"Error: ツイートのストリーミングに失敗しました\n `{info}`"), self.loop)
        self.error_callback()

    def on_disconnect(self, s):
        print(s)


def run(auth, listener):
    my_stream = tweepy.Stream(auth=auth, listener=listener)
    my_stream.filter(follow=[os.getenv("SPLATOON_ID")], is_async=True)

def start_stream():
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    loop = asyncio.get_event_loop()
    listener = StatusEventListener(loop=loop, error_callback=lambda: run(auth, listener))
    run(auth, listener)
    
class TweetCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        global channel

        self.bot = bot
        channel = self.bot.get_channel(int(os.getenv("TWEET_NOTICE_CHANNEL_ID")))
        start_stream()
        

def setup(bot):
    bot.add_cog(TweetCog(bot))