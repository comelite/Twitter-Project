from kafka import KafkaProducer
from json import dumps
import tweepy
import datetime
import time

class Ingestor():
    # Class to ingest tweets from the twitter API and send them to a kafka topic in utf-8
    def __init__(self, bearer_token):
        # Class constructor
        # @param bearer_token : the bearer token to access the twitter API
        self.bearer_token = bearer_token
        self.producer = KafkaProducer(bootstrap_servers=[
                                      'localhost:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))
        self.client = tweepy.Client(bearer_token=bearer_token)

    def get_recent_tweets(self, query, limit, start_time=None, end_time=None):
        # Get the recent tweets from the twitter API
        # @param query : the query to search for
        # @param limit : the number of tweets to get
        # @param start_time : the start time of the tweets to get
        # @param end_time : the end time of the tweets to get
        start_time = datetime.datetime.utcnow(
        ) - datetime.timedelta(minutes=10) if start_time is None else start_time
        end_time = datetime.datetime.utcnow(
        ) - datetime.timedelta(seconds=10) if end_time is None else end_time
        tweets = self.client.search_recent_tweets(query=query,
                                                  tweet_fields=[
                                                      'context_annotations', 'created_at', 'lang', 'author_id'],
                                                  start_time=start_time,
                                                  end_time=end_time,
                                                  max_results=limit)
        return tweets

    def send_to_kafka(self, tweets, topic, lang=None, verbose=False):
        # Send the tweets to the kafka topic
        # If the language is not specified, send all the tweets
        # @param tweets : the tweets to send
        # @param topic : the topic to send the tweets to
        # @param lang : the language of the tweets to send
        # @param verbose : if true, print the text of the tweets
        for tweet in tweets.data:
            if lang is None or tweet.lang == lang:
                self.producer.send(topic, {"id":tweet.id,"text":tweet.text,"autor":tweet.author_id,"created_at":tweet.created_at,"lang":tweet.lang})
                if verbose:
                    print(tweet.text)
                    print(tweet.created_at)
                    print(tweet.lang)
                    print(tweet.author_id)
                    print(tweet.id)
        self.producer.flush()

    def get_data_continuously(self, query, limit, topic, lang, timeLimit=0, verbose=False):
        # Get the tweets continuously from the twitter API and send them to the kafka topic
        # Make a pause of 10 seconds between each request
        # @param query : the query to search for
        # @param limit : the number of tweets to get
        # @param topic : the topic to send the tweets to
        # @param lang : the language of the tweets to query
        # @param timeLimit : the time limit to get the tweets
        # @param verbose : if true, print the text of the tweets
        is_time_true = True if timeLimit == 0 else False
        true_end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timeLimit)
        start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=40)
        end_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=30)

        while is_time_true or not true_end_time < datetime.datetime.utcnow():
            tweets = self.get_recent_tweets(query, limit, start_time, end_time)
            self.send_to_kafka(tweets, topic, lang, verbose)
            start_time = end_time
            end_time = start_time + datetime.timedelta(seconds=10)
            print("Pause ! ", true_end_time < datetime.datetime.utcnow())
            time.sleep(10)
