from afinn import Afinn
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import re
import string
from wordcloud import WordCloud
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# for sentiment analysis


class Cloud():

    def __init__(self):
        self.tokens = []
        pass

    def tweet_to_tokens(self, tweet, lang):
        # Convert the tweet to tokens
        # @param tweet : the tweet to convert to tokens
        # @param lang : the language of stopwords to use
        tokenizer = RegexpTokenizer(r'\w+')
        lemmatizer = WordNetLemmatizer()

        tweet_tokens = tokenizer.tokenize(tweet)[1:]
        tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
        tweet_tokens = [word for word in tweet_tokens if word.lower() != 'rt']

        tweet = " ".join(
            [word for word in tweet_tokens if word not in stopwords.words(lang)])

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

        self.tokens.append(tweet)

    def most_common_token_to_img(self):
        # Generate a wordcloud image from the most common tokens
        total_sentences = " ".join(self.tokens)
        twitter_mask = np.array(Image.open("img/twitter.jpg"))
        wordcloud = WordCloud(width=800, height=500, random_state=42, max_font_size=100, mask=twitter_mask,
                              contour_color="steelblue", contour_width=0, background_color="white").generate(total_sentences)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()


class Sentiment():
    # Sentiment analysis class
    def __init__(self):
        pass

    def tweet_to_sentiment(self, tweet):
        # Sentiment analysis of a tweet
        # Returns True if the tweet is positive, False if it is negative
        afinn = Afinn()
        score = afinn.score(tweet)
        return score >= 0
