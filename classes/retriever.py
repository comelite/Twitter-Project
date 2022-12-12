from kafka import KafkaConsumer
from json import loads

class Retriever():
    # Class to retrieve tweets from a kafka topic as a dictionary
    def __init__(self, topics):
        # Class constructor
        # @param topics : the topics to retrieve the tweets from
        self.consumer = KafkaConsumer(
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            value_deserializer=lambda x: loads(x.decode('utf-8')))
        self.topics = topics
        self.consumer.subscribe(self.topics)
        pass

    def retrieve_tweets(self, limit):
        # Retrieve the tweets from the topics
        # @param topics : the topics to retrieve the tweets from
        # @param limit : the number of tweets to retrieve
        for message in self.consumer:
            # return message.value and decrease the counter (generator function)
            yield message.value
            limit -= 1
            if limit == 0:
                break