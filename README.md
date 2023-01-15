# Racist tweets analyzer & wordcloud generator <!-- omit in toc -->

This project is a group project of the Data Stream Processing subject of 3 students of the M2DS at Ecole Polytechnique.

The goal of the project is to detect hatred and racism in tweets in real time, and to generate a wordcloud of the most used words in the racist tweets.

Moreover, it collects potentially problematic users and their tweets, and stores them in a file if there are more than a certain threshold of problematic tweets in their recent tweets.

## Table of contents <!-- omit in toc -->

- [Authors](#authors)
- [Introduction](#introduction)
  - [Environment requirements](#environment-requirements)
  - [Twitter API requirements](#twitter-api-requirements)
  - [Start Kafka](#start-kafka)
  - [Start the project](#start-the-project)
- [Project structure](#project-structure)
  - [Overview](#overview)
  - [Classes specifications](#classes-specifications)

## Authors

| Last name | First name | Email                             |
| --------- | ---------- | --------------------------------- |
| COTTART   | Kellian    | kellian.cottart@polytechnique.edu |
| LOISON    | Xavier     | xavier.loison@polytechnique.edu   |
| NOIR      | Mathys     | mathys.noir@polytechnique.edu     |

## Introduction

### Environment requirements

You need to create an environment to run the project. The list of dependencies can be found in [`requirements.txt`](requirements.txt). The project works with `Python 3.10`.

You can update all the libraries using the following command:

```bash
pip install -r requirements.txt
```

### Twitter API requirements

With your credentials, you need to create a `secrets.txt` file. In this file, you have to put all your keys.

```txt
API_KEY {your api key}
API_KEY_SECRET {your api key secret}
BEARER_TOKEN {your bearer token}
ACCESS_TOKEN {your access token}
ACCESS_TOKEN_SECRET {your access token secret}
```

To fill in the required fields, you must go and get them from the [twitter official website](https://developer.twitter.com/en/portal/dashboard).

### Start Kafka

You need to launch your zookeeper server and your kafka server in two different terminals:

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

```bash
bin/kafka-server-start.sh config/server.properties
```

### Start the project

Now you can run the app:

```bash
python main.py
```

## Project structure

### Overview

The tree of the project is the following:

```bash
├───classes
├───datasets
└───init
```

- The [`classes`](classes) folder contains all the classes used during the project.
- The [`datasets`](datasets) folder contains all the datasets used during the project.
- The [`init`](init) folder contains all the files used to initialize the classifiers used during the project.

### Classes specifications

The classes are the following:

- [`analyser.py`](classes/analyser.py): This file is used to analyse the tweets. The main idea is to classify racist tweets, heinous tweets and neutral tweets. The classifier used is `LogisticRegression` from `sklearn.linear_model`.  
The classifier is trained on a dataset of tweets labelled as racist or not. The dataset are available in the [`datasets`](datasets) folder.  
Furthermore, a wordcloud is also created to analyse the most used words in the racist tweets. It is updated in real time.

- [`app.py`](classes/app.py): This file is used to launch the app. It uses multi-threading to both get the recent tweets on a specific topic, and to process the tweets, leveraging the different cores of the computer to avoid waiting time.
  
- [`cleaner.py`](classes/cleaner.py): This file is used to clean the tweets. The main idea is to remove all the useless information from the tweets, such as the username, the hashtags, the links, the emojis, etc. The cleaning is done using the `re` library for regex, and it also uses `nltk` to lemmatize and tokenize the words.

- [`ingestor.py`](classes/ingestor.py): This file is used to ingest the tweets. The idea behind it is to get the tweets from the Twitter API, and to send them to the Kafka server. The tweets are sent to a custom named topic depending on the query.

- [`retriever.py`](classes/retriever.py): This file is used to retrieve the tweets from the Kafka topics.

- [`secret.py`](classes/secret.py): This file is used to get the credentials from the `secrets.txt` file, so as to not allow other people to see them from the GitHub repository.

- [`user_information.py`](classes/user_information.py): This file is used to get the user information from the Twitter API. The main idea is to look up the user account if a tweet he posted in the recent feed was detected as racist or heinous.  
If it is, then we retrieve his recent tweets and perform the same analysis on them. If the user has several racist tweets, he is added to the `dangerous_users.txt` file, along with the tweets supposed to be racist, acting as a small database for problematic users.
