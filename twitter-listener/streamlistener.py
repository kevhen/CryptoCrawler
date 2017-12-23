import tweepy
import json
import yaml


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        print('[ERROR] API returns status code {}'.format(status_code))
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


def startListening():
    # Load settings, config files expected in current dir
    with open('credentials.yaml', 'r') as stream:
        creds = yaml.load(stream)

    # Set OAuth
    auth = tweepy.OAuthHandler(creds['twitter']['api_key'],
                               creds['twitter']['api_secret'])
    auth.set_access_token(creds['twitter']['access_token'],
                          creds['twitter']['access_secret'])

    # Create API object
    api = tweepy.API(auth)

    # Create a Stream
    print('Starting Stream Listener...')
    stream_listener = MyStreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=['python'], async=True)


if __name__ == '__main__':
    startListening()
