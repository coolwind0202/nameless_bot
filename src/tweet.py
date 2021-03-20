import tweepy
from discord.ext import commands, tasks
import requests


class StatusEventListener(tweepy.StreamListener):
    def on_status(self, status):
        screen_name = "SplatoonJP"
        if status.user.screen_name != screen_name:
            return
        print(status.text)
        tweet_url = f"https://twitter.com/{screen_name}/status/{status.id_str}"
        webhook = "https://discord.com/api/webhooks/822715010622816256/xl3q5NcET_uKkB7zjDpndH5IloVUJdP7OttFlKQBltm_EbvFVIq_iYWySuYYggXQkAUm"
        requests.post(webhook, data={
            "content": tweet_url
        })

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

        # returning non-False reconnects the stream, with backoff.

def start_stream():
    consumer_key = "LaSNO4AVIF2NdfVJ2OTIoxBVS"
    consumer_secret = "FReciwWnBuKrg19gDzutcyWRS457LJzmf9LQqD70Ue1iTOAb9P"

    access_token = "1108637385972043781-ogbNnPqStiRRaJGQ9oHDfhQ0ZRjAdq"
    access_token_secret = "e97oo8UuvK4Ww9XasgsbvWAqsc0SHGuy3eI9VHXytQl3e"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    listener = StatusEventListener()
    my_stream = tweepy.Stream(auth=auth, listener=listener)

    my_stream.filter(follow=["2888006497"],  is_async=True)
class TweetCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        start_stream()

    @tasks.loop(minutes=15.0)
    async def fetch_tweets(self):

        for status in api.user_timeline(id="SplatoonJP"):
            print(status.text)

def setup(bot):
    bot.add_cog(TweetCog(bot))