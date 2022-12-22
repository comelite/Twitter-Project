
import datetime

class Writer():
    def write(self, data):
        with open(f"{data.user_id}.txt", "w") as f:
            f.write(f"User Id: {data.user_id}")
            f.write(f"Time: {datetime.datetime.utcnow()}")
            f.write(f"Number of tweets: {len(data.tweets)}")
            for tweet in data.tweets:
                f.write(f"Time : {tweet.} - Tweet: {tweet.text}")


