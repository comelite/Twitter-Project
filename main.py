# import classes from the class folder
from classes import secret, ingestor, retriever, analyser

if __name__ == "__main__":

    # Create a class to decode the secrets
    keys = secret.Secret()

    # Create a class to analyse the tweets
    feed = ingestor.Ingestor(keys.bearer_token)

    # Get 10 recent tweets from the topic "france"
    tweets = feed.get_recent_tweets("football", 10)

    # Send them to the kafka topic "test_tweets"
    feed.send_to_kafka(tweets, "test_football", "fr", False)

    # Retrieve the tweets from the kafka topic "tweets" as a generator
    test_tweets = retriever.Retriever("test_football")
    test_tweets_generator = test_tweets.retrieve_tweets(10)

    # Analyse the tweets
    at = analyser.Cloud()
    sentiment = analyser.Sentiment()
    racism = analyser.Racist()

    best_model, vectorizer, best_threshold = racism.init_racism()
    
    for tweet in test_tweets_generator:
        at.tweet_to_tokens(tweet, "french")
        print(tweet)
        cleaned_tweet = racism.clean_tweet(tweet)
        print(cleaned_tweet)
        print("Sentiment: ", "positive" if sentiment.tweet_to_sentiment(
            cleaned_tweet) else "negative")
        racist, proba = racism.tweet_to_racism(cleaned_tweet, best_model, vectorizer, best_threshold)
        if racist:
            print (f'Racist tone with a {int(proba*100)}% probability')
    at.most_common_token_to_img()
