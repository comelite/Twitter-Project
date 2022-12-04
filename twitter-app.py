from kafka import KafkaProducer
from kafka import KafkaConsumer
import tweepy
import datetime
import json
import time
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
import re
import string
from wordcloud import WordCloud
from PIL import Image
import json
import numpy as np
from PIL import Image
import json
import matplotlib.pyplot as plt

nltk.download('stopwords')
nltk.download('wordnet')

with open("secrets.txt","r") as f:
    secrets =f.read().splitlines()
    
    api_key = secrets[0].split()[1]
    api_secret = secrets[1].split()[1]
    bearer_token = secrets[2].split()[1]
    access_token = secrets[3].split()[1]
    access_token_secret = secrets[4].split()[1]

class tweetsListener():

    def __init__(self,bearer_token):

        self.bearer_token = bearer_token
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        self.client = tweepy.Client(bearer_token=bearer_token)

    def get_recent_tweets(self,query,limit,start_time = None, end_time = None):

        start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=40) if start_time is None else start_time
        end_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10) if end_time is None else end_time
        tweets = self.client.search_recent_tweets(query=query,
                                            tweet_fields=['context_annotations', 'created_at', 'lang'],
                                            start_time=start_time,
                                            end_time=end_time,
                                            max_results=limit)
        return tweets
    
    def send_to_kafka(self,tweets,topic,lang,verbose=False):

        for tweet in tweets.data:
            if tweet.lang == lang:
                tweet_text = json.dumps(tweet.text).encode('utf-8')
                self.producer.send(topic,tweet_text)
                if verbose:
                    print(tweet_text)
        self.producer.flush()

    def get_data_continuously(self,query,limit,topic,lang,timeLimit = 0,verbose=False):

        is_time_true = True if timeLimit == 0 else False
        true_end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timeLimit)
        start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=40)
        end_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=30)

        while is_time_true or not true_end_time < datetime.datetime.utcnow():
            tweets = self.get_recent_tweets(query,limit,start_time,end_time)
            self.send_to_kafka(tweets,topic,lang,verbose)
            start_time = end_time
            end_time = start_time + datetime.timedelta(seconds=10)
            print("Pause ! ", true_end_time < datetime.datetime.utcnow())
            time.sleep(10)

class analyseTweet():
    def __init__(self):
        self.tokens = []
        pass

    def tweet_to_tokens(self,tweet,lang):
        tokenizer = RegexpTokenizer(r'\w+')
        lemmatizer = WordNetLemmatizer()

        tweet_tokens = tokenizer.tokenize(tweet)[1:]
        tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
        tweet_tokens = [word for word in tweet_tokens if word.lower() != 'rt']

        
        tweet = " ".join([word for word in tweet_tokens if word not in stopwords.words(lang)])

        tweet = tweet.strip('\n')
        tweet = " ".join(filter(lambda x: x[0] != '@', tweet.split()))
        tweet = bytes(tweet, 'utf-8').decode('utf-8','ignore')

        # Remove any URL
        tweet = re.sub(r"http\S+", "", tweet)
        tweet = re.sub(r"www\S+", "", tweet)

        # remove colons from the end of the sentences (if any) after removing url
        tweet = tweet.strip()
        tweet_len = len(tweet)
        if tweet_len > 0:
            if tweet[len(tweet) - 1] == ':':
                tweet = tweet[:len(tweet) - 1]
        # Remove any hash-tags symbols
        tweet = tweet.replace('#', '')

        # Convert every word to lowercase
        tweet = tweet.lower()

        # remove punctuations
        tweet = tweet.translate(str.maketrans('', '', string.punctuation))

        # trim extra spaces
        tweet = " ".join(tweet.split())

        # lematize words
        tweet = lemmatizer.lemmatize(tweet)

        self.tokens.append(tweet)

    def most_common_token_to_img(self):
        total_sentences = " ".join(self.tokens)
        twitter_mask = np.array(Image.open("img/twitter.jpg"))
        wordcloud = WordCloud(width=800, height=500, random_state=42, max_font_size=100, mask=twitter_mask, 
        contour_color="steelblue", contour_width=0, background_color="white").generate(total_sentences)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()

    def get_tweet_from_kafka(self,topic,lang,limit=100):
        consumer = KafkaConsumer(topic,bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest')
        for i in range(limit):
            print("Tweet : ",i)
            v = next(iter(consumer)).value
            
            if v is not None:
                tweet = json.loads(v)
                self.tweet_to_tokens(tweet,lang)
                print(tweet)


# tl = tweetsListener(bearer_token)
# tweets = tl.get_recent_tweets("covid",10)
# tl.send_to_kafka(tweets,"tweets","en")

# tl.get_data_continuously("covid",10,"tweets","en",timeLimit=60,verbose=True)

at = analyseTweet()
at.get_tweet_from_kafka("tweets","english",limit=10)
at.most_common_token_to_img()