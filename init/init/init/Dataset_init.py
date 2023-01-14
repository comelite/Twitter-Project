import pandas as pd
import re
from nltk.corpus import stopwords


#  Clean the tweet so that there are just meaning words left
def clean_tweet(tweet, lang='en'):
    stoplist_fr = list(set(stopwords.words('french')))
    stoplist_en = list(set(stopwords.words('english')))
    # Lowercase the tweet
    temp = tweet.lower()
    #  Remove contractions in english
    if lang == 'en':
        temp = re.sub("'", "", temp)
    #  Remove # and @
    list_regex_1 = [r'@[A-Za-z0-9_]+', r'#[A-Za-z0-9_]+']
    for regex in list_regex_1:
        temp = re.sub(regex, '', temp)
    #  Remorve urls
    list_regex_2 = [r'http\S+', r'www.\S+']
    for regex in list_regex_2:
        temp = re.sub('r'+regex, '', temp)
    #  Remove special characters. If french, keep specific characters
    if lang == 'en':
        list_regex_3 = [r'[()!?]', r'\[.*?\]', r'[^a-z0-9]']
    else:
        list_regex_3 = [r'[()!?]', r'\[.*?\]', r'[^a-zàâçéèêëîïôûùæœ0-9]']
    for regex in list_regex_3:
        temp = re.sub(regex, ' ', temp)
    #  Rebuild the sentence
    temp = temp.split()
    if lang == 'en':
        temp = [w for w in temp if w not in stoplist_en]
    else:
        temp = [w for w in temp if w not in stoplist_fr]
    temp = " ".join(word for word in temp)
    return temp


# Extract hashtags, ref to users and urls
def separate_infos(data_set):

    hashtags = data_set['tweet'].str.extractall(
        '#(?P<hashtag>[a-zA-Z0-9_]+)').reset_index().groupby(
            'level_0').agg(lambda x: ' '.join(x.values))
    data_set.loc[:, 'hashtags'] = hashtags['hashtag']

    ref_user = data_set['tweet'].str.extractall(
        '@(?P<ref_user>[a-zA-Z0-9_]+)').reset_index().groupby(
            'level_0').agg(lambda x: ' '.join(x.values))
    data_set.loc[:, 'ref_user'] = ref_user['ref_user']

    urls = data_set['tweet'].str.extractall(
        'http(?P<urls>[a-zA-Z0-9_]+)').reset_index().groupby(
            'level_0').agg(lambda x: ' '.join(x.values))
    data_set.loc[:, 'urls'] = urls['urls']

    data_set.fillna("", inplace=True)
    return data_set


# Use the MLMA data_set to identify racist tweets amongst hatred tweets
def label_racist(data_set):

    list_raciste = ['arabs',
                    'african_descent',
                    'asians',
                    'hispanics',
                    'muslims',
                    'christian',
                    'immigrants',
                    'jews',
                    'indian/hindu',
                    'refugees',
                    'other',
                    'individual']
    df_raciste = data_set[['tweet',
                           'target',
                           'group',
                           'hashtags',
                           'ref_user',
                           'urls']].copy()

    for condition in list_raciste:
        if condition == 'other' or condition == 'individual':
            df_raciste.loc[(df_raciste['target'] == 'religion'),
                           'label'] = 1
            df_raciste.loc[(df_raciste['target'] == 'origin'),
                           'label'] = 1
        else:
            df_raciste.loc[(data_set['group'] == condition),
                           'label'] = 1

    df_raciste.fillna(0, inplace=True)

    df_init = df_raciste.drop(['target',
                               'group'],
                              axis=1)
    return df_init


"""MAIN"""
# Prepare the MLMA data_set and then add labels
# (label_not_racist = 0 and label_racist = 1)

# For French dataset
data_set_fr = pd.read_csv("init/MLMA_fr.csv")
data_temp_fr = data_set_fr.copy()
data_temp_fr = separate_infos(data_temp_fr)
data_temp_fr['tweet'] = data_temp_fr['tweet'].apply(clean_tweet,
                                                    lang='fr')
racist_init_fr = label_racist(data_temp_fr)
racist_init_fr.to_csv('datasets/racist_init_fr.csv')

# For English dataset
data_set_en = pd.read_csv("init/MLMA_en.csv")
data_temp_en = data_set_en.copy()
data_temp_en = separate_infos(data_temp_en)
data_temp_en['tweet'] = data_temp_en['tweet'].apply(clean_tweet)
racist_init_en = label_racist(data_temp_en)
racist_init_en.to_csv('datasets/racist_init_en.csv')


# Prepare the Sentiment140 data_set and then add labels
# (label_not_racist = 0 and label_racist = 1)

# French data_set
# Load and format the data_set
data_frame = pd.read_csv("init/tweets_fr.csv",
                         delimiter=',',
                         on_bad_lines='skip')

data_frame.fillna("", inplace=True)
data_frame['label'] = data_frame.index
data_frame['tweet'] = data_frame['polarity'] + data_frame['statutnull']
data_frame = data_frame.drop(['polarity', 'statutnull'],
                             axis=1)

# Reduce the data_set and clean the tweets
temp_df1 = data_frame.loc[(data_frame['label'] == '4')]['tweet']
temp_df1 = temp_df1.to_frame()
temp_df1 = temp_df1[0:100_000]
temp_df1['label'] = 0

temp_df2 = data_frame.loc[(data_frame['label'] == '0')]['tweet']
temp_df2 = temp_df2.to_frame()
temp_df2 = temp_df2[0:100_000]
temp_df2['label'] = 1

temp_df = pd.concat([temp_df1, temp_df2],
                    ignore_index=True).sample(frac=1).reset_index(drop=True)

data_temp_fr = temp_df.copy()
data_temp_fr = separate_infos(data_temp_fr)
data_temp_fr['tweet'] = data_temp_fr['tweet'].apply(clean_tweet,
                                                    lang='fr')
hatred_init_fr = data_temp_fr.copy()
hatred_init_fr.to_csv('datasets/hatred_init_fr.csv')

# English data_set
# Load and format the english data_set
data_frame = pd.read_csv("init/tweets_en.csv",
                         delimiter=',',
                         on_bad_lines='skip',
                         encoding='latin-1',
                         header=None,
                         names=['id',
                                'date',
                                '',
                                'user',
                                'tweet'])
data_frame['label'] = data_frame.index

# Reduce the data_set and clean the tweets
temp_df1 = data_frame.loc[(data_frame['label'] == 4)]['tweet']
temp_df1 = temp_df1.to_frame()
temp_df1 = temp_df1[0:100_000]
temp_df1['label'] = 0

temp_df2 = data_frame.loc[(data_frame['label'] == 0)]['tweet']
temp_df2 = temp_df2.to_frame()
temp_df2 = temp_df2[0:100_000]
temp_df2['label'] = 1

temp_df = pd.concat([temp_df1, temp_df2],
                    ignore_index=True).sample(frac=1).reset_index(drop=True)

data_temp_en = temp_df.copy()
data_temp_en = separate_infos(data_temp_en)
data_temp_en['tweet'] = data_temp_en['tweet'].apply(clean_tweet)
hatred_init_en = data_temp_en.copy()
hatred_init_en.to_csv('datasets/hatred_init_en.csv')
