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
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

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

def setup(bot):
    bot.add_cog(TweetCog(bot))