from afinn import Afinn
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import f1_score

from nltk import download
from nltk.corpus import stopwords
download('stopwords')

from classes.cleaner import Cleaner
        
class Cloud():

    def __init__(self):
        self.tokens = []
        pass

    def tweet_to_tokens(self, tweet, lang):
        # Convert the tweet to tokens
        # @param tweet : the tweet to convert to tokens
        # @param lang : the language of stopwords to use
        cleaner = Cleaner(tweet, lang, stopwords.words(lang))
        self.tokens.append(cleaner.to_tokens())

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
        self.afinn = Afinn()

    def tweet_to_sentiment(self, tweet):
        # Sentiment analysis of a tweet
        # Returns True if the tweet is positive, False if it is negative
        score = self.afinn.score(tweet)
        return score >= 0
    
class Racist():
    # Sentiment analysis class
    def __init__(self, path, params = {'penalty': ['l1', 'l2'], 'C': [3, 10, 30, 100, 300]}):
        # Init the racist classifier
        # @param path : Full path to the dataset
        # @param params : Parameters to use for the GridSearch
        
        # Load the dataset & fill the empty values
        self.dataset = pd.read_csv(path).fillna('')
                
        # if path does not contain fr then it is english
        self.lang = 'french' if 'fr' in path else 'english'
        
        # Set the stopwords to the language of the dataset
        self.stoplist = stopwords.words(self.lang)
        
        # Set the vectorizer
        self.vectorizer = TfidfVectorizer(stop_words = self.stoplist, ngram_range=(1, 3), min_df=10)       
        
        features = self.vectorizer.fit_transform(self.dataset.tweet)
        X_train, X_test, y_train, y_test = train_test_split(features, self.dataset.label)
        
        # GridSearch to find the best parameters for the model
        optimal_params = GridSearchCV(LogisticRegression(solver='liblinear', max_iter=250), param_grid=params, scoring='f1', cv=5, n_jobs=-1)
        optimal_params.fit(X_train, y_train)
        
        # Train the model with the best parameters
        best_model = LogisticRegression(solver = 'liblinear', max_iter=250, C = optimal_params.best_params_['C'], penalty = optimal_params.best_params_['penalty'])
        best_model.fit(X_train, y_train)
        
        # Find the best threshold
        probas = best_model.predict_proba(X_test)
        thresholds = np.arange(0.1, 0.9, 0.01)
        
        # Calculate f1 score for each threshold
        scores = [f1_score(y_test, (probas[:, 1] >= x).astype(int)) for x in thresholds]
        best_threshold = thresholds[np.argmax(scores)]
        
        # Set the model and the threshold
        self.model = best_model
        self.threshold = best_threshold
    
    def tweet_to_racism(self, tweet):
        # Racist tone analysis of a tweet
        # Returns True if the tweet has a racist tone, and the probability
        
        cleaner = Cleaner(tweet, self.lang, self.stoplist)
        tweet = cleaner.to_tokens()
        
        new_features = self.vectorizer.transform([tweet])
        proba = self.model.predict_proba(new_features)[0][1]
        racist = False
        if proba > self.threshold + 0.3 :
            racist = True
        return racist, proba
