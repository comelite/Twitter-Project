from afinn import Afinn
from nltk import download
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import string
from wordcloud import WordCloud

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import f1_score

download('stopwords')
download('wordnet')
download('omw-1.4')

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
    
class Racist():
    # Sentiment analysis class
    def __init__(self):
        pass
            
    def init_racism(self):    
        data_init = pd.read_csv("data_init.csv")
        data_init.fillna("", inplace=True)
        stoplist = set(stopwords.words('french'))
        vectorizer = TfidfVectorizer(stop_words = list(stoplist), ngram_range=(1, 3), min_df=10)
        features = vectorizer.fit_transform(data_init.tweet)
        X_train, X_test, y_train, y_test = train_test_split(features, data_init.label)
        params = {'penalty': ['l1', 'l2'], 'C': [3, 10, 30, 100, 300]}
        lrmodel = GridSearchCV(LogisticRegression(solver='liblinear', max_iter=250), param_grid=params, scoring='f1', cv=5, n_jobs=-1)
        lrmodel.fit(X_train, y_train)
        best_model = LogisticRegression(solver = 'liblinear', max_iter=250, C = lrmodel.best_params_['C'], penalty = lrmodel.best_params_['penalty'])
        best_model.fit(X_train, y_train)

        probas = best_model.predict_proba(X_test)
        thresholds = np.arange(0.1, 0.9, 0.01)
        scores = [f1_score(y_test, (probas[:, 1] >= x).astype(int)) for x in thresholds]
        best_threshold = thresholds[np.argmax(scores)]
        return best_model, vectorizer, best_threshold
    
    def clean_tweet(self, tweet):
        temp = tweet.lower()
        temp = re.sub("@[A-Za-z0-9_]+","", temp)
        temp = re.sub("#[A-Za-z0-9_]+","", temp)
        temp = re.sub(r'http\S+', '', temp)
        temp = re.sub('[()!?]', ' ', temp)
        temp = re.sub('\[.*?\]',' ', temp)
        temp = re.sub("[^a-zàâçéèêëîïôûùæœ0-9]"," ", temp)
        temp = temp.split()
        stoplist = list(set(stopwords.words('french')))
        temp = [w for w in temp if not w in stoplist]
        temp = " ".join(word for word in temp)
        return temp
    
    def tweet_to_racism(self, tweet, best_model, vectorizer, best_threshold):
        # Racist tone analysis of a tweet
        # Returns True if the tweet has a racist tone, and the probability
        new_features = vectorizer.transform([tweet])
        proba = best_model.predict_proba(new_features)[0][1]
        racist = False
        if proba > best_threshold + 0.3 :
            racist = True
        return racist, proba #print (f'Racist tone with a {np.round(proba*100,1)}% probability')
