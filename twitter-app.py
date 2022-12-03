from kafka import KafkaProducer
import tweepy
import datetime
import json

with open("secrets.txt","r") as f:
    secrets =f.read().splitlines()
    
    api_key = secrets[0].split()[1]
    api_secret = secrets[1].split()[1]
    bearer_token = secrets[2].split()[1]
    access_token = secrets[3].split()[1]
    access_token_secret = secrets[4].split()[1]

class tweetsListener():
    def __init__(self,bearer_token):
        self.bearer_token = bearer_token
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        self.client = tweepy.Client(bearer_token=bearer_token)

    def get_recent_tweets(self,query,limit):
        start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=40)
        end_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
        tweets = self.client.search_recent_tweets(query=query,
                                            tweet_fields=['context_annotations', 'created_at', 'lang'],
                                            start_time=start_time,
                                            end_time=end_time,
                                            max_results=limit)
        return tweets
    
    def send_to_kafka(self,tweets,topic,lang,verbose=False):
        for tweet in tweets.data:
            if tweet.lang == lang:
                tweet_text = json.dumps(tweet.text).encode('utf-8')
                self.producer.send(topic,tweet_text)
                if verbose:
                    print(tweet_text)
        self.producer.flush()

tl = tweetsListener(bearer_token)
tweets = tl.get_recent_tweets("covid",10)
tl.send_to_kafka(tweets,"tweets","en")