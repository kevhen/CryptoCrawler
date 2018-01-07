"""
Listens to the Twitter stream.

- Connects to Twitter API using creds in credentials.yaml.
- Filters the Stream for words defined in config.yaml.
- Stores the tweet in a Mongodb, connection params in config.yaml.
"""

import tweepy
import json
import yaml
import time
from pymongo import MongoClient
from pymongo import errors as pymongo_errors


class MyStreamListener(tweepy.StreamListener):
    """Extends tweepy.StreamListener."""

    def __init__(self, *args, **kwargs):
        """Extend tweepys init to allow additional parameters."""
        self.mute = False  # Helper for debug output in on_status()
        self.count = 0  # Amount of Tweets recveived for debug output
        # Used for partitioning the tweets
        self.collections = kwargs['conf']['collections']
        self.mongodb = kwargs['conf']['mongodb']
        del kwargs['conf']
        # Open a connection to mongo:
        client = MongoClient(self.mongodb['host'], self.mongodb['port'])
        self.db = client[self.mongodb['db']]
        # Invoke tweepys' class init
        super(MyStreamListener, self).__init__(*args, **kwargs)

    def on_status(self, status):
        """Handle incoming tweets."""
        # Just info, that tweets are received correctly
        if self.mute is not True:
            print('[INFO] Receiving tweets...')
            self.mute = True

        # Info output amout of tweets
        self.count += 1
        if (self.count % 1000) == 0:  # Log every 5000 tweets
            print('{} Tweets received. Still listening...'.format(self.count))

        # Looking in whole json for keywords of the different collections
        tweet_json_str = json.dumps(status._json)
        collections = self.identify_collection(tweet_json_str)

        # Store tweets, but only those with english language
        if status.lang == 'en':
            self.store_tweet(status, collections)

    def on_error(self, status_code):
        """Handle API errors. Especially quit in 420 to avoid API penalty."""
        print('[ERROR] API returns status code {}'.format(status_code))
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_connect(self):
        """Called once connected to streaming server."""
        print('[INFO] Connected to Twitter Stream.')
        return

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice."""
        print('[WARNING] Disconnect from Stream. Notice: ', notice)
        return

    def identify_collection(self, tweet_json):
        """Identifies, to which collection(s) the tweet belongs."""
        collections = set()
        for collection_name, data in self.collections.items():
            for keyword in data['keywords']:
                if keyword in tweet_json.lower():
                    collections.add(collection_name)

        # If no words found, something went wrong. Put to 'unknown':
        if len(collections) < 1:
            collections.add('unknown')
        return collections

    def store_tweet(self, tweet, collections):
        """Store a subset of field from tweet to mongodb."""
        # Select attributes to strore
        tweet_mini = {}
        tweet_mini['timestamp_ms'] = int(tweet.timestamp_ms)
        tweet_mini['id'] = tweet.id_str
        tweet_mini['author_id'] = tweet.author.id_str
        # Text of extended tweets (> 140 chars) is in a different field
        if (tweet.truncated is True) and ('full_text' in tweet.extended_tweet):
            tweet_mini['text'] = tweet.extended_tweet['full_text']
        else:
            tweet_mini['text'] = tweet.text
        # Store geo info, but only if available
        if (tweet.geo is not None):
            tweet_mini['geo'] = tweet.geo
        if (tweet.coordinates is not None):
            tweet_mini['coordinates'] = tweet.coordinates
        if (tweet.place is not None):
            plc = tweet.place
            tweet_mini['place'] = {}
            tweet_mini['place']['name'] = plc.name
            tweet_mini['place']['country'] = plc.country
            tweet_mini['place']['coordinates'] = plc.bounding_box.coordinates
            tweet_mini['place']['type'] = plc.bounding_box.type

        # Try saving to mongo, delay on auto reconnect (e.g. container down)
        try:
            # Store in mongo collection(s)
            for collection_name in collections:
                self.db[collection_name].insert(tweet_mini)
        except pymongo_errors.AutoReconnect:
            print('[ERROR] pymongo auto reconnect. Wait for some seconds...')
            time.sleep(5)


def startListening():
    """Start listening to twitter streams."""
    # Load settings, config files expected in current dir
    with open('credentials.yaml', 'r') as stream:
        creds = yaml.load(stream)
    with open('../config.yaml', 'r') as stream:
        conf = yaml.load(stream)

    # Set OAuth
    auth = tweepy.OAuthHandler(creds['twitter']['api_key'],
                               creds['twitter']['api_secret'])
    auth.set_access_token(creds['twitter']['access_token'],
                          creds['twitter']['access_secret'])

    # Create API object
    api = tweepy.API(auth)

    # Concat all words from configuration file
    all_words = set()  # We want only unique words here
    for collection_name, data in conf['collections'].items():
        if 'keywords' in data:
            all_words.update(data['keywords'])

    print('[INFO] Starting Stream Listener.')
    stream_listener = MyStreamListener(conf=conf)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=list(all_words), async=True)


if __name__ == '__main__':
    startListening()
