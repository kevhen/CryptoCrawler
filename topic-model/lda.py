"""
Provides a Web Service that does topic Modelling.

Parameters are:
- name of mongod-db collection, where the Tweets to be modelled are
- unix-timestamp with start of time range to be included
- unix-timestamp with stop of time range to be included

Example-Call:
http://0.0.0.0:5000/lda?collection=bitcoin&start=1515082825836&end=1515082840114

Inspired by
https://www.analyticsvidhya.com/blog/2016/08/beginners-guide-to-topic-modeling-in-python/
and
https://rstudio-pubs-static.s3.amazonaws.com/79360_850b2a69980c4488b1db95987a24867a.html
"""

import pandas as pd
import json
import yaml
from pymongo import MongoClient
from flask import Flask
from webargs import fields
from webargs.flaskparser import use_args
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
from gensim import corpora
import random
import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Load wordlist, if not already available
nltk.download('stopwords')
nltk.download('wordnet')


def load_tweets(db, collection, start_time, end_time):
    """Load text from tweets in specified colleciton & time range."""
    query = {'timestamp_ms': {'$gt': start_time, '$lt': end_time}}
    fields = {'text': 1}
    cursor = db[collection].find(query, fields)
    df = pd.DataFrame(list(cursor))
    # Remove the mongo-row-id, as it's not needed
    if '_id' in df.columns:
        del df['_id']

    logger.info('Loaded {} Tweets..'.format(len(df)))
    return df


def clean(docs):
    """Clean Documents."""
    # Prepare parameters
    stop_custom = ['rt', 'bitcoin', 'bitcoins', 'iota', 'ethereum', 'btc',
                   'eth', 'iot', 'ltc', 'litecoin', 'litecoins', 'iotas',
                   'ltc', 'cryptocurrency', 'crypto', 'cryptocurrencies',
                   'coin']
    stop = set(stopwords.words('english') + stop_custom)
    min_length = 4
    exclude_custom = '“”…‘’x'
    exclude = set(string.punctuation + exclude_custom)
    lemma = WordNetLemmatizer()
    do_lemmatization = False

    # As processing takes a lot of time, we limit to 10.000 tweets:
    if len(docs) > 10000:
        random.shuffle(docs)
        docs = docs[:10000]

    # Do actual cleansing
    docs_clean = []
    for doc in docs:
        clean_doc = doc

        # Remove punctuation
        clean_doc = ''.join(ch for ch in clean_doc if ch not in exclude)

        # Remove URLS
        clean_doc = ' '.join([i for i in clean_doc.lower().split()
                              if not i.startswith('http')])

        # Remove anything containing numbers
        clean_doc = ' '.join([i for i in clean_doc.lower().split()
                              if not any(char.isdigit() for char in i)])

        # Remove short words
        clean_doc = ' '.join([i for i in clean_doc.lower().split()
                              if len(i) >= min_length])
        # Lemmatize
        if do_lemmatization:
            clean_doc = ' '.join(lemma.lemmatize(word)
                                 for word in clean_doc.split())

        # Remove Stopwords
        clean_doc = ' '.join([i for i in clean_doc.lower().split()
                              if i not in stop])

        # Add to result list
        docs_clean.append(clean_doc.split())

    i = 0
    for doc in docs_clean:
        i += len(doc)
    logger.info('Words in corpus: {}'.format(i))

    return docs_clean


def model_lda(docs, num_topics):
    """Use LDA to model topics."""
    # Load documents into corpora dictionary
    dictionary = corpora.Dictionary(docs)
    # Prepare Document Term Matrix
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in docs]
    # Training LDA model on the DTM.
    Lda = gensim.models.ldamodel.LdaModel
    ldamodel = Lda(doc_term_matrix, num_topics=num_topics,
                   id2word=dictionary, passes=10)

    # Converts LDA model int nice list
    topic_list = []
    for i in range(num_topics):
        terms = ldamodel.get_topic_terms(i, 20)
        topic_terms = []
        for pair in terms:
            # Workaround to convert float32 into float with 5 decimals
            probability = float("{0:.5f}".format(pair[1]))
            term = dictionary[pair[0]]
            topic_terms.append([term, probability])
        topic_list.append(topic_terms)

    return topic_list


def indentify_topics(df, num_topics):
    """Run DataFrame through preprocessing & modelling pipeline."""
    # Return empty, if no results
    if (len(df) < 1) or ('text' not in df.columns.values):
        return []

    # Convert DataFrame Column to list
    docs = df['text'].values.tolist()
    docs = clean(docs)
    topics = model_lda(docs, num_topics)
    return topics


def open_mongo():
    """Open Connection to MongoDB and return db-object."""
    # Load config yaml
    with open('../config.yaml', 'r') as stream:
        config = yaml.load(stream)

    # Open Connection to MongoDB
    conn = MongoClient(config['mongodb']['host'],
                       config['mongodb']['port'])
    # Use local mongo-container IP for testing
    # conn = MongoClient('172.17.0.2', config['mongodb']['port'])
    db = conn[config['mongodb']['db']]
    return db


def init_flask():
    """Initialize Flask Webservice."""
    # Open MongoDB needed for answering request
    db = open_mongo()

    # Define Flask Webservice
    app = Flask(__name__)

    topic_args = {
        'collection': fields.Str(missing='bitcoin'),
        'start': fields.Int(missing=0),
        'end': fields.Int(missing=0),
        'topics': fields.Int(missing=5),
    }

    @app.route('/lda', methods=['GET'])
    @use_args(topic_args)
    def model_topics(args):
        """Handle incoming request, send back topics."""
        result = {}
        df = load_tweets(db, args['collection'], args['start'], args['end'])
        result['tweet_count'] = len(df)
        result['topics'] = indentify_topics(df, args['topics'])
        result['num_topics'] = args['topics']
        logger.info('Results:')
        logger.info(result)
        return json.dumps(result)
    return app


if __name__ == '__main__':
    app = init_flask()
    app.run(host='0.0.0.0', port=5000, debug=True)
