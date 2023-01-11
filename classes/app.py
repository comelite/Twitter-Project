import time
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp

from classes import secret, ingestor, retriever
from classes import analyser, user_information, cleaner

from PIL import Image
from wordcloud import WordCloud


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

    def analyse_racism_tweet(self,
                             racism_hatred,
                             racism_racist,
                             verbose=False):
        # analyse the tweets to see if they are racist or polarized
        # @param racism_hatred: model to analyse tweets for polarized tone
        # @param racism_racist: model to analyse tweets for racist tone
        # @param verbose: if True, print the tweets and the results
        time.sleep(10)  # Wait for the sentiment analysis to be start
        retriever_module = retriever.Retriever(self.topic)
        feed = ingestor.Ingestor(self.secrets.bearer_token)

        while True:
            tweets = retriever_module.retrieve_tweets(1)
            for tweet in tweets:
                hateful, proba_hate = racism_hatred.tweet_to_racism(
                    tweet['text'])
                racist, proba_racist = racism_racist.tweet_to_racism(
                    tweet['text'])
                if verbose:
                    print("Tweet: ", tweet['text'])
                    print(f'Polarized tone with {int(proba_hate*100)}% proba')
                    print(f'Racist tone with {int(proba_racist*100)}% proba')
                if hateful:
                    feed.send_to_kafka_from_dict(
                        [tweet],
                        f"{self.topic}_hateful_tweets")
                    self.analyse_user_tweets(tweet, racism_racist, 50)
                if racist:
                    feed.send_to_kafka_from_dict(
                        [tweet],
                        f"{self.topic}_racist_tweets")
                feed.send_to_kafka_from_dict(
                    [tweet],
                    f"{self.topic}_normal_tweets")

    def analyse_user_tweets(self, tweet, racism_racist, limit):
        # If the tweet was considered as racist, look at the user's tweets
        # If more than 10% racist tweets of his 50 last tweets, add him to list
        # @param tweet : the tweet to analyse and retrieve the user from
        # @param racism_racist : the model to analyse tweets for racist tone
        # @param limit : the number of tweets to retrieve from the user

        # Create user_information instance
        user = user_information.User_Information(self.secrets.bearer_token)
        # Get the user's tweets (last 50) and put it in a topic
        user_topic = user.get_user_tweets(tweet['author_id'], limit)
        # Get the topic and retrieve the tweets
        feed = retriever.Retriever(user_topic)
        user_tweets = feed.retrieve_tweets(limit)
        # List of tweets that are racist
        racist_dict = (
            {"author": user.get_user_information_from_id(
                tweet['author_id'])['username'],
             "racist_tweets": []})

        # Count the number of racist tweets
        for current_tweet in user_tweets:
            racist, _ = racism_racist.tweet_to_racism(current_tweet['text'])
            if racist:
                clean = cleaner.Cleaner(current_tweet['text'], self.lang)
                new_tweet = clean.to_clean()
                racist_dict["racist_tweets"].append(new_tweet)

        # If more than 10% of tweets are racist, add user to dangerous list
        if len(racist_dict["racist_tweets"]) >= int(0.1 * limit):
            self.append_dangerous_file(racist_dict)

    def append_dangerous_file(self, racist_dict):
        # Generate a file with the dangerous users and their tweets
        # @param racist_dict : the dictionary containing user and its tweets
        with open("./dangerous_users.txt", "a+") as file:
            file.write(f"Pseudo to check: {racist_dict['author']}\n")
            file.write("Suspected tweets: \n")
            for tweet in racist_dict['racist_tweets']:
                file.write(f"- \t{tweet}\n")
            file.write("-------------------\n")

    def generate_clouds(self):

        time.sleep(5)
        twitter_mask = np.array(Image.open("img/twitter.jpg"))

        hate_cloud = analyser.Cloud()
        racist_cloud = analyser.Cloud()
        normal_cloud = analyser.Cloud()

        cloud_array = [normal_cloud, hate_cloud, racist_cloud]
        names = ["Normal", "Hate", "Racist"]

        hateful_tweets_flow = retriever.Retriever(
            f"{self.topic}_hateful_tweets")
        racist_tweets_flow = retriever.Retriever(
            f"{self.topic}_racist_tweets")
        normal_tweets_flow = retriever.Retriever(
            f"{self.topic}_normal_tweets")

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
                wordcloud = WordCloud(random_state=42,
                                      max_font_size=100,
                                      mask=twitter_mask,
                                      contour_color="steelblue",
                                      contour_width=0,
                                      background_color="white").generate(
                                          " ".join(cloud.tokens))
                plt.imshow(wordcloud,
                           interpolation='bilinear')
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
        feed.get_data_continuously(self.query,
                                   self.nb_tweets,
                                   self.topic,
                                   self.lang[:2],
                                   verbose=False)

    def run(self):
        try:
            # Start by training the classifier
            racism_hatred = analyser.Racist("./datasets/hatred_init_en.csv")
            racism_racist = analyser.Racist("./datasets/racist_init_en.csv")
            # Get tweets
            process_data_from_tweeter = self.ctx.Process(
                target=self.tweeter_to_kafka)
            process_data_from_tweeter.start()
            # Racist analysis
            process_analyse_racism = self.ctx.Process(
                target=self.analyse_racism_tweet,
                args=(racism_hatred, racism_racist))
            process_analyse_racism.start()
            # Clouds
            process_clouds = self.ctx.Process(
                target=self.generate_clouds)
            process_clouds.start()
        except RuntimeError:
            print("Program is shutting down...")
        finally:
            # Join the threads and close
            process_data_from_tweeter.join()
            process_analyse_racism.join()
            process_clouds.start()
