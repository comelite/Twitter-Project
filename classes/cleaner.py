import re
import string
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk import download

download('wordnet')
download('omw-1.4')

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
        tweet = self.tweet
        tokenizer = RegexpTokenizer(r'\w+')
        lemmatizer = WordNetLemmatizer()

        tweet_tokens = tokenizer.tokenize(tweet)[1:]
        tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
        tweet_tokens = [word for word in tweet_tokens if word.lower() != 'rt']

        tweet = " ".join(
            [word for word in tweet_tokens if word not in self.stoplist])

        tweet = tweet.strip('\n')
        tweet = " ".join(filter(lambda x: x[0] != '@', tweet.split()))
        tweet = bytes(tweet, 'utf-8').decode('utf-8', 'ignore')

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
        return tweet
