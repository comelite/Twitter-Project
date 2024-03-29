import re
import string

from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer


class Cleaner():

    def __init__(self, tweet, lang, stoplist=[]):
        """Init the cleaner class

        @param tweet: Tweet to clean
        @param lang: Language of the tweet
        @param stoplist: Stopwords list to use
        """
        self.tweet = tweet
        self.lang = lang
        self.stoplist = stoplist

    def to_tokens(self):
        """Clean the tweet and return a list of tokens

        @return tweet: the cleaned tweet
        """
        # Shortcut for the tweet
        tweet = self.tweet
        # Remove the new line character (if any)
        tweet = tweet.strip('\n')
        # Init the tokenizer and the lemmatizer
        tokenizer = RegexpTokenizer(r'[\w\@\#]+')
        lemmatizer = WordNetLemmatizer()
        # Tokenize the tweet as a list and remove "RT"
        tweet_tokens = tokenizer.tokenize(tweet)[1:]
        # Remove the mentions using regex @\w+, then URLs and co
        tweet_tokens = ([word for word in tweet_tokens
                         if not re.match(r'@\w+', word)
                         and not re.match(r'http\S+', word)
                         and not re.match(r"www\S+", word)
                         and not re.match(r"\bco\b", word)])
        # Remove any non-alphabetic characters
        tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
        # Lowercase all the words
        tweet_tokens = [word for word in tweet_tokens if word.lower() != 'rt']
        # Remove the stopwords
        tweet = " ".join([word for word in tweet_tokens
                          if word not in self.stoplist])
        # Decode the tweet
        tweet = bytes(tweet, 'utf-8').decode('utf-8', 'ignore')
        # remove colons from end of sentences (if any) after removing url
        tweet = tweet.strip()
        if len(tweet) > 0:
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

    def to_clean(self):
        """Clean the tweet and return a string of bytes

        @return tweet: the cleaned tweet (as bytes)
        """
        tweet = self.tweet
        tweet = tweet.replace("\n", " ")
        tweet = re.sub(r"http\S+", "", tweet)
        tokenizer = RegexpTokenizer(r'[\w\@\#]+')
        tweet_tokens = tokenizer.tokenize(tweet)[1:]
        tweet = " ".join([word for word in tweet_tokens])
        emojis = re.compile(
            u"([\U00002600-\U000027BF])|"
            "([\U0001f300-\U0001f64F])|"
            "([\U0001f680-\U0001f6FF])")
        tweet = emojis.sub(r'', tweet)
        return bytes(tweet, 'utf-8').decode('utf-8', 'ignore')
