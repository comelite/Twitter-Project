from classes import secret, ingestor, retriever, analyser
import multiprocessing as mp
import time

def tweeter_to_kafka(keys,query, topic, language, nb_tweets):
    feed = ingestor.Ingestor(keys.bearer_token)

    feed.get_data_continuously(query, nb_tweets, topic, language[:2], verbose = True)

class App():
    def __init__(self):
        # Class constructor
        # @param bearer_token : the bearer token to access the twitter API
        self.secrets = secret.Secret()
        self.ctx = mp.get_context('spawn')

    
    def run(self, query, topic, language, nb_tweets):

        process_data_from_tweeter = self.ctx.Process(target=tweeter_to_kafka, args=(self.secrets, query, topic, language, nb_tweets))
        process_data_from_tweeter.start()

        while(True):
            print("Waiting for data from tweeter")
            time.sleep(5)