from classes import secret, ingestor, retriever, analyser
import multiprocessing as mp
import time


class App():
    def __init__(self, query, topic, lang, nb_tweets):
        # Class constructor
        # @param topic : the topic to send the data to
        # @param query : the query to search on tweeter
        # @param lang : the language of the tweets
        # @param nb_tweets : the number of tweets to retrieve
        self.secrets = secret.Secret()
        self.ctx = mp.get_context('spawn')
        self.query = query
        self.topic = topic
        self.lang = lang
        self.nb_tweets = nb_tweets
    
    def analyse_racism_tweet(self, racism_hatred, racism_racist, verbose = False):
        # analyse the tweets to see if they are racist or hateful
        # @param racism_hatred: the model to analyse the tweets for hateful tone
        # @param racism_racist: the model to analyse the tweets for racist tone
        # @param verbose: if True, print the tweets and the results
        time.sleep(10) # Wait for the sentiment analysis to be start
        retriever_module = retriever.Retriever(f"{self.topic}_negative_tweets")
        feed = ingestor.Ingestor(self.secrets.bearer_token)
            
        while True:
            tweets = retriever_module.retrieve_tweets(1)
            for tweet in tweets:
                hateful, proba_hate = racism_hatred.tweet_to_racism(tweet['text'])
                racist, proba_racist = racism_racist.tweet_to_racism(tweet['text'])
                if verbose:
                    print("Tweet: ", tweet['text'])
                    print (f'Hateful tone with a {int(proba_hate*100)}% probability')
                    print (f'Racist tone with a {int(proba_racist*100)}% probability')
                if proba_hate > 0.75:
                    feed.send_to_kafka_from_dict([tweet], f"{self.topic}_hateful_tweets")
                if proba_racist > 0.75:
                    feed.send_to_kafka_from_dict([tweet], f"{self.topic}_racist_tweets")

    def analyse_sentiment_tweet(self, verbose = False):
        # analyse the tweets to see if they are positif or negatif
        # @param verbose : if True, print the tweets and the results

        time.sleep(5) # Wait for the retriever from tweeter to be start

        sentiment = analyser.Sentiment()
        retriever_module = retriever.Retriever(self.topic)
        feed = ingestor.Ingestor(self.secrets.bearer_token)

        while True:
            tweets = retriever_module.retrieve_tweets(1)
            for tweet in tweets:
                if sentiment.tweet_to_sentiment(tweet['text']):
                    if verbose:
                        print("Tweet: ", tweet['text'])
                        print("Sentiment: ", "positive")
                    feed.send_to_kafka_from_dict([tweet], f"{self.topic}_positive_tweets")
                else:
                    if verbose:
                        print("Tweet: ", tweet['text'])
                        print("Sentiment: ", "negative")
                    feed.send_to_kafka_from_dict([tweet], f"{self.topic}_negative_tweets")
                    
    def tweeter_to_kafka(self):
        # Gather tweets from tweeter and send them to kafka
        feed = ingestor.Ingestor(self.secrets.bearer_token)
        feed.get_data_continuously(self.query, self.nb_tweets, self.topic, self.lang[:2], verbose = False)

    def run(self):
            # Start by training the classifier
            racism_hatred = analyser.Racist("./datasets/hatred_init_en.csv")
            racism_racist = analyser.Racist("./datasets/racist_init_en.csv")
            # Get tweets
            process_data_from_tweeter = self.ctx.Process(self.tweeter_to_kafka())
            process_data_from_tweeter.start()
            # Sentiment analysis
            process_analyse_sentiment = self.ctx.Process(self.analyse_sentiment_twee())
            process_analyse_sentiment.start()
            # Racist analysis
            process_analyse_racism = self.ctx.Process(self.analyse_racism_tweet(racism_hatred, racism_racist))
            process_analyse_racism.start()
