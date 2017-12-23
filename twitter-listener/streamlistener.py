"""Listens to the Twitter stream.

- Connects to Twitter API using creds in credentials.yaml.
- Filters the Stream for words defined in config.yaml.
- Stores the tweet in a Mongodb.
"""

import tweepy
import json
import yaml
import sys


class MyStreamListener(tweepy.StreamListener):
    """Extends tweepy.StreamListener."""

    def __init__(self, *args, **kwargs):
        """Extend the init to allow additional parameters."""
        # Used for partitioning the tweets
        self.collections = kwargs['conf']['collections']
        del kwargs['conf']
        # Invoke tweepys' class init
        super(MyStreamListener, self).__init__(*args, **kwargs)

    def on_status(self, status):
        """Handle incoming tweets."""
        # Looking in whole json string for keywords of the different collections
        tweet_json_str = json.dumps(status._json)
        coll = self.identify_collection(tweet_json_str)
        print('-' * 15)
        print(coll)
        print(status.text)

    def on_error(self, status_code):
        """Handle API errors. Especially quit in 420 to avoid API penalty."""
        print('[ERROR] API returns status code {}'.format(status_code))
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def identify_collection(self, tweet):
        """Identifies, to which collection the tweet belongs."""
        collections = set()
        for coll, words in self.collections.items():
            for word in words:
                if word in tweet.lower():
                    collections.add(coll)
        return collections


def startListening():
    """Start listening to x streams."""
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
    all_words = []
    for stream_name, word_list in conf['collections'].items():
        all_words.extend(word_list)

    print('Starting Stream Listener...')
    stream_listener = MyStreamListener(conf=conf)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=all_words, async=True)


if __name__ == '__main__':
    startListening()
