"""
Provides a Service, that adds sentiment to tweets stored in MongoDB.

Inspired by
http://francescopochetti.com/financial-blogs-sentiment-analysis-part-crawling-web/
"""

import pandas as pd
import yaml
import time
from pymongo import MongoClient
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Load wordlist, if not already available
nltk.download('stopwords')


def load_tweets(db, collection, update_all):
    """Load text from tweets in specified colleciton & time range."""
    if update_all is True:
        query = {}
    else:
        query = {'sentiment': {'$exists': False}}
    fields = {'text': 1}
    cursor = db[collection].find(query, fields)
    df = pd.DataFrame(list(cursor))
    return df


def write_sentiments(db, collection, df):
    """Load text from tweets in specified colleciton & time range."""
    for index, row in df.iterrows():
        # Set sentiment value
        if row['score'] == 0:
            sentiment = 'neu'
        elif row['score'] > 0:
            sentiment = 'pos'
        else:
            sentiment = 'neg'

        query = {'_id': row['_id']}
        update = {'$set': {
            'score': row['score'],
            'sentiment': sentiment
        }}

        db[collection].update_one(query, update)
    return


def clean(text):
    """Clean Documents."""
    text = text.lower()
    bow = tokenizer.tokenize(text)

    # Remove URLS
    clean = [word for word in bow if not word.startswith('http')]

    # Remove Stopwords
    clean = [word for word in clean if word not in stop]

    # Remove short words
    clean = [word for word in clean if len(word) >= 3]

    clean_text = ' '.join(clean)
    return clean_text


def load_positive():
    """Load positive dictionary."""
    with open('./pos.txt', 'r') as f:
        positives = f.readlines()
    positive = [pos.strip().lower() for pos in positives]
    return set(positive)


def load_negative():
    """Load negative dictionary."""
    with open('./neg.txt', 'r') as f:
        negatives = f.readlines()
    negatives = [pos.strip().lower() for pos in negatives]
    return set(negatives)


def sentiment(text):
    """Use keywords to get sentiment."""
    pos = 0
    neg = 0
    for word in text.split():
        if word in positives:
            pos += 1
        if word in negatives:
            neg += 1
    senti = pos - neg
    return senti


def update_sentiment(db, collections, update_all=False):
    """Update sentiment score.

    Recursivly called, to run forever. Update_all can be
    set to True, if you want to re-analyse all tweets. Otherwise
    only new tweets get sentimented.
    """
    for collection in collections:
        logger.info('-' * 50)
        logger.info('Updating sentiment for: {}'.format(collection))
        logger.info('Loading tweets...')
        df = load_tweets(db, collection, update_all)
        if len(df) > 0:
            logger.info('{} Tweets to process...'.format(len(df)))
            logger.info('Clean text...')
            df['text'] = df['text'].apply(clean)
            logger.info('Get sentiment score...')
            df['score'] = df['text'].apply(sentiment)
            logger.info('Write to db...')
            write_sentiments(db, collection, df)
            logger.info('Done.')
        else:
            logger.info('No new tweets.')

    logger.info('Waiting 30 sec...')
    time.sleep(30)
    update_sentiment(db, collections, update_all)
    return


if __name__ == '__main__':
    with open('../config.yaml', 'r') as stream:
        config = yaml.load(stream)

    # List of twitter collections
    collections = list(config['collections'])

    # Open Connection to MongoDB
    conn = MongoClient(config['mongodb']['host'],
                       config['mongodb']['port'])
    # Use local mongo-container IP for testing
    # conn = MongoClient('172.17.0.2', config['mongodb']['port'])
    db = conn[config['mongodb']['db']]

    stop = set(stopwords.words('english') + ['rt'])
    tokenizer = RegexpTokenizer(r'\w+')

    negatives = load_negative()
    positives = load_positive()

    update_sentiment(db, collections, True)
