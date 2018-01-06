"""
Provides a Web Service that does topic Modelling.

Parameters are:
- name of mongod-db collection, where the Tweets to be modelled are
- unix-timestamp with start of time range to be included
- unix-timestamp with stop of time range to be included

Example-Call:
http://0.0.0.0:5000/lda?collection=bitcoin&start=1515082825836&end=1515082840114
"""

import pandas as pd
import json
import yaml
from pymongo import MongoClient
from flask import Flask
from webargs import fields
from webargs.flaskparser import use_args


# Load config yaml
with open('../config.yaml', 'r') as stream:
    config = yaml.load(stream)

# Open Connection to MongoDB
conn = MongoClient(config['mongodb']['host'],
                   config['mongodb']['port'])
# Use local mongo-container IP for testing
conn = MongoClient('172.17.0.2', config['mongodb']['port'])
db = conn[config['mongodb']['db']]


def load_tweets(collection, start_time, end_time):
    """Load text from tweets in specified colleciton & time range."""
    query = {'timestamp_ms': {'$gt': str(start_time), '$lt': str(end_time)}}
    fields = {'text': 1}
    cursor = db[collection].find(query, fields)
    df = pd.DataFrame(list(cursor))
    print(df)
    # Remove the mongo-row-id, as it's not needed
    if '_id' in df.columns:
        del df['_id']
    return df


# Define Flask Webservice

app = Flask(__name__)

topic_args = {
    'collection': fields.Str(missing='bitcoin'),
    'start': fields.Int(missing=0),
    'end': fields.Int(missing=0)
}


@app.route('/lda', methods=['GET'])
@use_args(topic_args)
def model_topics(args):
    """Handle incoming request, send back topics."""
    result = {}
    df = load_tweets(args['collection'], args['start'], args['end'])
    result['tweet_count'] = len(df)
    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
