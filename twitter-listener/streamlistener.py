"""
Listens to the Twitter stream.

- Connects to Twitter API using creds in credentials.yaml.
- Filters the Stream for words defined in config.yaml.
- Stores the tweet in a Mongodb, connection params in config.yaml.
"""

import tweepy
import json
import yaml
from pymongo import MongoClient

class MyStreamListener(tweepy.StreamListener):
    """Extends tweepy.StreamListener."""

    def __init__(self, *args, **kwargs):
        """Extend tweepys init to allow additional parameters."""
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
        # Looking in whole json for keywords of the different collections
        tweet_json_str = json.dumps(status._json)
        collections = self.identify_collection(tweet_json_str)

        # Store in mongo collection(s)
        for collection_name in collections:
        	self.db[collection_name].insert(status._json)

        # Debug output
        print('-' * 15)
        print(collections, status.text)

    def on_error(self, status_code):
        """Handle API errors. Especially quit in 420 to avoid API penalty."""
        print('[ERROR] API returns status code {}'.format(status_code))
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def identify_collection(self, tweet):
        """Identifies, to which collection(s) the tweet belongs."""
        collections = set()
        for collection_name, data in self.collections.items():
            for keyword in data.keywords:
                if keyword in tweet.lower():
                    collections.add(collection_name)

        # If no words found, something went wrong. Put to 'unknown':
        if len(collections) < 1:
        	collections.add('unknown')
        return collections


def startListening():
    """Start listening to twitter streams."""
    # Load settings, config files expected in current dir
    with open('credentials.yaml', 'r') as stream:
        creds = yaml.load(stream)
    with open('config.yaml', 'r') as stream:
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
    for stream_name, word_list in conf['collections'].items():
        all_words.update(word_list)

    print('Starting Stream Listener...')
    stream_listener = MyStreamListener(conf=conf)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=list(all_words), async=True)


if __name__ == '__main__':
    startListening()
