from classes import secret, ingestor, retriever, analyser
import multiprocessing as mp
import time

def tweeter_to_kafka(keys,query, topic, language, nb_tweets):
    # Run the app
    # @param query : the query to search on tweeter
    # @param topic : the topic to send the data to
    # @param language : the language of the tweets
    # @param nb_tweets : the number of tweets to retrieve
    feed = ingestor.Ingestor(keys.bearer_token)
    feed.get_data_continuously(query, nb_tweets, topic, language[:2], verbose = False)

def analyse_sentiment_tweet(topic,keys,verbose = False, cloud = False):
    # analyse the tweets to see if they are positif or negatif
    # @param topic: the topic to analyse
    # @param keys: the keys to access the tweeter API
    # @param verbose: if True, print the tweets and the results
    # @param cloud: if True, will show the cloud image.

    time.sleep(5) # Wait for the retriever from tweeter to be start

    sentiment = analyser.Sentiment()
    retriever_module = retriever.Retriever(topic)
    feed = ingestor.Ingestor(keys.bearer_token)

    while True:
        tweets = retriever_module.retrieve_tweets(1)
        for tweet in tweets:
            if sentiment.tweet_to_sentiment(tweet['text']):
                if verbose:
                    print("Tweet: ", tweet['text'])
                    print("Sentiment: ", "positive")
                feed.send_to_kafka_from_dict([tweet], f"{topic}_positive_tweets")
            else:
                if verbose:
                    print("Tweet: ", tweet['text'])
                    print("Sentiment: ", "negative")
                feed.send_to_kafka_from_dict([tweet], f"{topic}_negative_tweets")

def analyse_racism_tweet(topic,keys,racism_hatred,racism_racist,verbose = False, cloud = False):
    # analyse the tweets to see if they are racist or hateful
    # @param topic: the topic to analyse
    # @param keys: the keys to access the tweeter API
    # @param racism_hatred: the model to analyse the tweets for hateful tone
    # @param racism_racist: the model to analyse the tweets for racist tone
    # @param verbose: if True, print the tweets and the results
    # @param cloud: if True, will show the cloud image.
    time.sleep(10) # Wait for the sentiment analysis to be start
    retriever_module = retriever.Retriever(f"{topic}_negative_tweets")
    feed = ingestor.Ingestor(keys.bearer_token)
    while True:
        tweets = retriever_module.retrieve_tweets(1)
        for tweet in tweets:
            hateful, proba_hate = racism_hatred.tweet_to_racism(tweet['text'])
            racist, proba_racist = racism_racist.tweet_to_racism(tweet['text'])
            if proba_hate > 0.75:
                if verbose:
                    print("Tweet: ", tweet['text'])
                    print (f'Hateful tone with a {int(proba_hate*100)}% probability')
                feed.send_to_kafka_from_dict([tweet], f"{topic}_hateful_tweets")
            if proba_racist > 0.75:
                if verbose:
                    print("Tweet: ", tweet['text'])
                    print (f'Racist tone with a {int(proba_racist*100)}% probability')
                feed.send_to_kafka_from_dict([tweet], f"{topic}_racist_tweets")

class App():
    def __init__(self):
        # Class constructor

        self.secrets = secret.Secret()
        self.ctx = mp.get_context('spawn')

    
    def run(self, query, topic, language, nb_tweets):
        # Run the app
        # @param query : the query to search on tweeter
        # @param topic : the topic to send the data to
        # @param language : the language of the tweets
        # @param nb_tweets : the number of tweets to retrieve

        racism_hatred = analyser.Racist("./datasets/hatred_init_en.csv")
        racism_racist = analyser.Racist("./datasets/racist_init_en.csv")

        process_data_from_tweeter = self.ctx.Process(target=tweeter_to_kafka, args=(self.secrets, query, topic, language, nb_tweets))
        process_data_from_tweeter.start()

        process_analyse_sentiment = self.ctx.Process(target=analyse_sentiment_tweet, args=(topic, self.secrets))
        process_analyse_sentiment.start()

        process_analyse_racism = self.ctx.Process(target=analyse_racism_tweet, args=(topic, self.secrets, racism_hatred, racism_racist))
        process_analyse_racism.start()

