from classes import secret, ingestor, retriever, analyser
import multiprocessing as mp
import time
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image

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
                feed.send_to_kafka_from_dict([tweet], f"{self.topic}_normal_tweets")

    def generate_clouds(self):
        
        time.sleep(5)
        twitter_mask = np.array(Image.open("img/twitter.jpg"))
        
        hate_cloud = analyser.Cloud()
        racist_cloud = analyser.Cloud()
        normal_cloud = analyser.Cloud()
        
        cloud_array = [normal_cloud, hate_cloud, racist_cloud]
        names = ["Normal", "Hate", "Racist"]
        
        hateful_tweets_flow = retriever.Retriever(f"{self.topic}_hateful_tweets")
        racist_tweets_flow = retriever.Retriever(f"{self.topic}_racist_tweets")
        normal_tweets_flow = retriever.Retriever(f"{self.topic}_normal_tweets")
        
        figure = plt.figure()
        printable = True
        while True:
            
            hate_tweets = hateful_tweets_flow.retrieve_tweets(1)
            racist_tweets = racist_tweets_flow.retrieve_tweets(1)
            normal_tweets = normal_tweets_flow.retrieve_tweets(1)
            
            for h, r, n in zip(hate_tweets, racist_tweets, normal_tweets):
                hate_cloud.tweet_to_tokens(h['text'], self.lang)
                racist_cloud.tweet_to_tokens(r['text'], self.lang)
                normal_cloud.tweet_to_tokens(n['text'], self.lang)
                
            for idx, cloud in enumerate(cloud_array):
                plt.subplot(1, len(cloud_array), idx+1).set_title(names[idx])
                wordcloud = WordCloud(random_state=42, max_font_size=100, mask=twitter_mask,
                                contour_color="steelblue", contour_width=0, background_color="white").generate(" ".join(cloud.tokens))
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
            
            if printable:
                figure.show()
                printable = False
            else:
                figure.canvas.draw()
                figure.canvas.flush_events()
                                
    def tweeter_to_kafka(self):
        # Gather tweets from tweeter and send them to kafka
        feed = ingestor.Ingestor(self.secrets.bearer_token)
        feed.get_data_continuously(self.query, self.nb_tweets, self.topic, self.lang[:2], verbose = False)

    def run(self):
        try:
            # Start by training the classifier
            racism_hatred = analyser.Racist("./datasets/hatred_init_en.csv")
            racism_racist = analyser.Racist("./datasets/racist_init_en.csv")
            # Get tweets
            process_data_from_tweeter = self.ctx.Process(target=self.tweeter_to_kafka)
            process_data_from_tweeter.start()
            # Racist analysis
            process_analyse_racism = self.ctx.Process(target = self.analyse_racism_tweet, args = (racism_hatred, racism_racist))
            process_analyse_racism.start()
            # Clouds
            process_clouds = self.ctx.Process(target = self.generate_clouds)
            process_clouds.start()
        except RuntimeError:
            print("Program is shutting down...") 
        finally:
            # Join the threads and close
            process_data_from_tweeter.join()
            process_analyse_racism.join()
            process_clouds.start()
