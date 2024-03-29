import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import f1_score
from nltk.corpus import stopwords
from classes.cleaner import Cleaner
import afinn as af


class Cloud():

    def __init__(self, word_window=300):
        self.tokens = []
        self.word_window = word_window

    def word_windowing(self):
        """Word windowing
        if list of words longer than word window, we cut it
        """
        self.tokens = (self.tokens
                       if len(self.tokens) <= self.word_window
                       else self.tokens[-self.word_window:])

    def tweet_to_tokens(self, tweet, lang):
        """Convert the tweet to tokens

        @param tweet: the tweet to convert to tokens
        @param lang: the language of stopwords to use
        """
        cleaner = Cleaner(tweet, lang, stopwords.words(lang))
        self.tokens.append(cleaner.to_tokens())
        self.word_windowing()

    def most_common_token_to_img(self):
        """Generate a wordcloud image from the most common tokens"""
        total_sentences = " ".join(self.tokens)
        twitter_mask = np.array(Image.open("img/twitter.jpg"))
        wordcloud = WordCloud(width=800,
                              height=500,
                              random_state=42,
                              max_font_size=100,
                              mask=twitter_mask,
                              contour_color="steelblue",
                              contour_width=0,
                              background_color="white").generate(
                                  total_sentences)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()


class Racist():
    def __init__(self,
                 path,
                 params={'penalty': ['l1', 'l2'],
                         'C': [0.25, 0.5, 0.75, 1, 3],
                         'max_iter': [25, 30, 35, 40]},
                 verbose=False):
        """Init the racist classifier

        @param path: Full path to the dataset
        @param params: Parameters to use for the GridSearch
        @param verbose: Boolean to print the training results
        """
        # Load the dataset & fill the empty values
        self.dataset = pd.read_csv(path).fillna('')
        # if path does not contain fr then it is english
        self.lang = 'french' if 'fr' in path else 'english'
        # Set the stopwords to the language of the dataset
        self.stoplist = stopwords.words(self.lang)
        # Set the vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words=self.stoplist,
            ngram_range=(1, 3), min_df=10)
        features = self.vectorizer.fit_transform(self.dataset.tweet)
        X_train, X_test, y_train, y_test = train_test_split(
            features,
            self.dataset.label)
        # GridSearch to find the best parameters for the model
        optimal_params = GridSearchCV(
            LogisticRegression(solver='liblinear', random_state=2506),
            param_grid=params,
            scoring='f1',
            cv=5,
            n_jobs=-1)
        optimal_params.fit(X_train, y_train)
        if verbose:
            print(
                f'Model trained with F1 score = {optimal_params.best_score_}')
            print(f'Best parameters: {optimal_params.best_params_}')
        # Train the model with the best parameters
        best_model = (
            LogisticRegression(
                solver='liblinear',
                max_iter=optimal_params.best_params_['max_iter'],
                C=optimal_params.best_params_['C'],
                penalty=optimal_params.best_params_['penalty']))
        best_model.fit(X_train, y_train)
        # Find the best threshold
        probas = best_model.predict_proba(X_test)
        thresholds = np.arange(0.1, 0.9, 0.01)
        # Calculate f1 score for each threshold
        scores = ([f1_score(y_test,
                            (probas[:, 1] >= x).astype(int))
                   for x in thresholds])
        best_threshold = thresholds[np.argmax(scores)]
        # Set the model and the threshold
        self.model = best_model
        self.threshold = best_threshold

    def negative_tweets(self, tweet):
        """Negative tone analysis of a tweet

        @param tweet: the tweet to analyze
        @return negative: Boolean of whether the tweet has a negative tone
        @return score: The associated score
        """
        afinn = af.Afinn(language=self.lang[:2])
        score = afinn.score(tweet)
        return score < 0, score

    def tweet_to_racism(self, tweet, verbose=False):
        """Racist tone analysis of a tweet

        @param tweet: the tweet to analyze
        @param verbose: Boolean to print the results
        @return racist: Boolean of whether the tweet has a racist tone
        @return probability: The associated probability
        """
        cleaner = Cleaner(tweet, self.lang, self.stoplist)
        tweet = cleaner.to_tokens()
        new_features = self.vectorizer.transform([tweet])
        probability = self.model.predict_proba(new_features)[0][1]
        negative, score = self.negative_tweets(tweet)
        racist = negative and probability > self.threshold
        if verbose:
            print("----------------------------------")
            print(f'Tweet: {tweet}')
            print(f'Probability: {probability * 100:.2f}%')
            print(f'Is problematic?: {racist}')
            print(f'Negative tone: {negative}')
            print(f'Negative score: {score}')
        return racist, probability
