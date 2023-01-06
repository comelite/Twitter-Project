# import classes from the class folder
from classes import app
from nltk import download

download('wordnet')
download('omw-1.4')
download('stopwords')

if __name__ == "__main__":

    # Set the topic to search
    query = "white OR arab OR black OR asian OR muslim OR jews"
    # Set the topic to send the data to
    topic = "racist_test"
    # Set the language of the tweets
    language = "english"
    # Get a batch of 10 tweets
    nb_tweets = 10
    # Create the application
    application = app.App(query, language[:2] + "_" + topic.lower() + "_tweets", language, nb_tweets)
    # Start the application
    application.run()
