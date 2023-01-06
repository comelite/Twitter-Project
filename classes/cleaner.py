import re
import string
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
import time

class Cleaner():
    
    def __init__(self, tweet, lang, stoplist):
        # Init the cleaner class
        # @param tweet : Tweet to clean
        # @param lang : Language of the tweet
        # @param stoplist : Stopwords list to use
        self.tweet = tweet
        self.lang = lang
        self.stoplist = stoplist
        
    def to_tokens(self):
        
        # Shortcut for the tweet
        tweet = self.tweet
        
        # Init the tokenizer and the lemmatizer
        tokenizer = RegexpTokenizer(r'\w+')
        lemmatizer = WordNetLemmatizer()

        # Remove the new line character
        tweet = tweet.strip('\n')
        
        # Remove the mentions
        tweet = " ".join(filter(lambda x: x[0] != '@', tweet.split()))
        
        # Tokenize the tweet as a list and remove "RT"
        tweet_tokens = tokenizer.tokenize(tweet)[1:]
        
        # Remove any non-alphabetic characters
        tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
        
        # Lowercase all the words
        tweet_tokens = [word for word in tweet_tokens if word.lower() != 'rt']
        
        # Remove the stopwords
        tweet = " ".join([word for word in tweet_tokens if word not in self.stoplist])
        
        # Decode the tweet
        tweet = bytes(tweet, 'utf-8').decode('utf-8', 'ignore')
        
        # Remove any URL
        tweet = re.sub(r"http\S+", "", tweet)
        tweet = re.sub(r"www\S+", "", tweet)
        tweet = re.sub(r"co\S+", "", tweet)
        
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
        return tweet
