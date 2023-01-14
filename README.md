# Twitter-Project
This project is a group project of the Data Stream Processing subject of 3 students of the M2DS of the Polytechnic Institute of Paris

# Before we start

You need to create an environment to run Kafka. Use requirements.txt:

```bash
pip install -r requirements.txt
```

You need to create a secrets.txt file. In this file we will find :

```
API_KEY {your api key}
API_KEY_SECRET {your api key secret}
BEARER_TOKEN {your bearer token}
ACCESS_TOKEN {your access token}
ACCESS_TOKEN_SECRET {your access token secret}
```

To fill in your information you have to go and get it from the [tweeter site](https://developer.twitter.com/en/portal/dashboard)

# Run the app !

You need to launch your zookeeper server and your kafka server in two different terminals :

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

```bash
bin/kafka-server-start.sh config/server.properties
```

After that you need to create the "tweets" topic :

```bash
kafka-topics --create --topic tweets --bootstrap-server localhost:9092
```

Now you can run the app :

```bash
python twitter-app.py
```
