import tweepy
import datetime
import time
from classes import ingestor

class User_Information():
    def __init__(self, bearer_token):
        # Class constructor
        # @param bearer_token : the bearer token to access the twitter API
        self.bearer_token = bearer_token
        self.client = tweepy.Client(bearer_token=bearer_token)
        
    def get_user_tweets(self, user_id, limit):
        # Get the recent tweets from the twitter API
        # @param user_id : the id of the user to get the tweets from
        # @param limit : the number of tweets to get
        feed = ingestor.Ingestor(self.bearer_token)
        tweets = self.client.get_users_tweets(user_id, tweet_fields=['context_annotations', 'created_at', 'lang'], max_results=limit)
        # Send the tweets to the kafka topic user_id_tweets
        topic = f"{user_id}_tweets"
        feed.send_to_kafka_from_dict(tweets.data, topic)
        return topic
    
    def get_user_relations(self, user_id, limit):
        # Get the recent tweets from the twitter API
        # @param user_id : the id of the user to get the tweets from
        # @param limit : the number of tweets to get
        relations = self.client.get_users_following(user_id, max_results=limit)
        return relations

    def get_user_information_from_username(self, username):
        # Get the recent tweets from the twitter API
        # @param username : the username of the user to get the tweets from
        # @param limit : the number of tweets to get
        user = self.client.get_user(username = username)
        return user

    def get_user_information_from_id(self, id):
        # Get the recent tweets from the twitter API
        # @param id : the id of the user to get the tweets from
        # @param limit : the number of tweets to get
        user = self.client.get_user(id = id)
        return user.data
