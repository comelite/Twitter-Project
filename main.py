# import classes from the class folder
from classes import app
from nltk import download

download('wordnet')
download('omw-1.4')
download('stopwords')

if __name__ == "__main__":

    # Set the topic to search
    query = "white OR arab OR black OR asian OR muslim OR jews"
    topic = "racist_test"
    language = "english"
    nb_tweets = 10
    application = app.App(query, language[:2] + "_" + topic.lower() + "_tweets", language, nb_tweets)

    application.run()

    # # Analyse the tweets
    # normal_cloud = analyser.Cloud()
    # hate_cloud = analyser.Cloud()
    # racist_cloud = analyser.Cloud()
    # sentiment = analyser.Sentiment()

    # racism_hatred = analyser.Racist("./datasets/hatred_init_en.csv")
    # racism_racist = analyser.Racist("./datasets/racist_init_en.csv")

    # for idx, tweet in enumerate(test_tweets_generator):
    #     print("------------------------")
    #     print("Tweet ", idx+1, ": " , tweet)
    #     print("Sentiment: ", "positive" if sentiment.tweet_to_sentiment(tweet) else "negative")
        
    #     hateful, proba_hate = racism_hatred.tweet_to_racism(tweet)
    #     racist, proba_racist = racism_racist.tweet_to_racism(tweet)
        
    #     print (f'Hateful tone with a {int(proba_hate*100)}% probability')
    #     print (f'Racist tone with a {int(proba_racist*100)}% probability')
        
    #     normal_cloud.tweet_to_tokens(tweet, language)
    #     if proba_hate > 0.75:
    #         hate_cloud.tweet_to_tokens(tweet, language)
    #     if proba_racist > 0.75:
    #         racist_cloud.tweet_to_tokens(tweet, language)

    # cloud_array = [normal_cloud, hate_cloud, racist_cloud]
    # twitter_mask = np.array(Image.open("img/twitter.jpg"))
    # fig = plt.figure(figsize=(15, 15))
    # names = ["Normal", "Hate", "Racist"]
    # for idx, cloud in enumerate(cloud_array):
    #     plt.subplot(1, len(cloud_array), idx+1).set_title(names[idx])
    #     if cloud.tokens == []: 
    #         plt.text(0.5, 0.5, "No words to display")
    #     else:
    #         wordcloud = WordCloud(random_state=42, max_font_size=100, mask=twitter_mask,
    #                             contour_color="steelblue", contour_width=0, background_color="white").generate(" ".join(cloud.tokens))
    #         plt.imshow(wordcloud, interpolation='bilinear')
    #     plt.axis('off')
    # fig.suptitle("Normal - Hate - Racist")
    # plt.show()
    # user_informations = user_information.User_Information(keys.bearer_token)

    # ui = user_informations.get_user_information_from_username("elonmusk")

    # user_tweets = user_informations.get_user_tweets(ui.data.id, 10)
    # print(user_tweets)
