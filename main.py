# import classes from the class folder
from classes import secrets, ingestor, retriever, analyser

if __name__ == "__main__":

    # Create a class to decode the secrets
    keys = secrets.Secrets()

    # Create a class to analyse the tweets
    feed = ingestor.Ingestor(keys.bearer_token)

    # Get 2 recent tweets from the topic "russia"
    tweets = feed.get_recent_tweets("russia", 10)

    # Send them to the kafka topic "test_tweets"
    feed.send_to_kafka(tweets, "test_tweets", "en", False)

    # Retrieve the tweets from the kafka topic "tweets" as a generator
    test_tweets = retriever.Retriever("test_tweets")
    test_tweets_list = test_tweets.retrieve_tweets(2)

    # Analyse the tweets
    at = analyser.Analyser()
    for tweet in test_tweets_list:
        at.tweet_to_tokens(tweet, "english")
    at.most_common_token_to_img()
