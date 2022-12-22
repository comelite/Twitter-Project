# import classes from the class folder
from classes import secrets, ingestor, retriever, analyser, user_information

# if __name__ == "__main__":

#     # Create a class to decode the secrets
#     keys = secrets.Secrets()

#     # Create a class to analyse the tweets
#     feed = ingestor.Ingestor(keys.bearer_token)

#     # Get 10 recent tweets from the topic "russia"
#     tweets = feed.get_recent_tweets("russia", 10)

#     # Send them to the kafka topic "test_tweets"
#     feed.send_to_kafka(tweets, "test_tweets", "en", False)

#     # Retrieve the tweets from the kafka topic "tweets" as a generator
#     test_tweets = retriever.Retriever("test_tweets")
#     test_tweets_generator = test_tweets.retrieve_tweets(10)

#     # Analyse the tweets
#     at = analyser.Cloud()
#     sentiment = analyser.Sentiment()

#     for tweet in test_tweets_generator:
#         at.tweet_to_tokens(tweet, "english")
#         print(tweet)
#         print("Sentiment: ", "positive" if sentiment.tweet_to_sentiment(
#             tweet) else "negative")
#     at.most_common_token_to_img()

keys = secrets.Secrets()

user_informations = user_information.User_Information(keys.bearer_token)

ui = user_informations.get_user_information_from_username("elonmusk")

user_tweets = user_informations.get_user_tweets(ui.data.id, 10)
print(user_tweets)

