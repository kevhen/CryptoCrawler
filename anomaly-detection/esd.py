"""
Provides a Web Service that does Anomaly Detection.

Parameters are:
- name of mongod-db collection, where the Tweets to be modelled are
- unix-timestamp with start of time range to be included
- unix-timestamp with stop of time range to be included

Example-Call:
http://0.0.0.0:5001/esd?collection=bitcoin&start=1515082825836&end=1515082840114
"""

import pandas as pd
import json
import yaml
from pymongo import MongoClient
from flask import Flask
from webargs import fields
from webargs.flaskparser import use_args
import statsmodels.api as sm
import numpy as np
from PyAstronomy import pyasl
import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def agg_tweets(db, collection, start_time, end_time, hours):
    """Load text from tweets in specified colleciton & time range."""
    agg_range = 1000 * 60 * 60 * hours   # by hour
    cursor = db[collection].aggregate([
        {
            '$project': {
                'timestamp_ms': '$timestamp_ms',
                'div_val': {'$divide': ['$timestamp_ms', agg_range]},
            }
        },
        {
            '$project': {
                'timestamp_ms': '$timestamp_ms',
                'div_val': '$div_val',
                'mod_val': {'$mod': ['$div_val', 1]}
            }
        },
        {
            '$project': {
                'timestamp_ms': '$timestamp_ms',
                'div_val': '$div_val',
                'mod_val': '$mod_val',
                'sub_val': {'$subtract': ['$div_val', '$mod_val']},
            }
        },
        {
            '$group': {
                '_id': '$sub_val',
                'count': {'$sum': 1}
            }
        }])
    df = pd.DataFrame(list(cursor))
    df['collection'] = collection

    # Restore the actual time stamps, which got "compressed"
    # during mongodb aggregation
    df['timestamp_ms'] = df['_id'].astype(int).multiply(agg_range)

    df = df[(df['timestamp_ms'] >= start_time)
            & (df['timestamp_ms'] <= end_time)]

    # Convert to datetime
    df['date'] = pd.to_datetime(df['timestamp_ms'], unit='ms')

    # Set as index
    df = df.set_index(df['date'])
    df = df.sort_index()

    # Remove the mongo-row-id, as it's not needed
    if '_id' in df.columns:
        del df['_id']
    if 'date' in df.columns:
        del df['date']
    return df


def detect_anomalies(df, hours):
    """Use Seasonal Decompose and ESD on residual to detect anomalies."""
    # The frequency of the signal changes. We expect 24h cycles.
    frequency = round(24 / hours)

    # Seasonal decompose
    model = sm.tsa.seasonal_decompose(df['count'], freq=frequency)

    # We only use residue values here
    resid = model.resid.values

    # Set NaNs to 0, as this ESD doesn't handle them
    resid[np.isnan(resid)] = 0

    # Use ESD to detect anomalies
    anomalies = pyasl.generalizedESD(resid, 10, 0.05)

    # Get the timestamps from the corresponding anomalies
    result_df = df['timestamp_ms'].ix[anomalies[1]].tolist()
    return result_df


def open_mongo():
    """Open Connection to MongoDB and return db-object."""
    # Load config yaml
    with open('../config.yaml', 'r') as stream:
        config = yaml.load(stream)

    # Open Connection to MongoDB
    conn = MongoClient(config['mongodb']['host'],
                       config['mongodb']['port'])
    # Use local mongo-container IP for testing
    conn = MongoClient('172.17.0.2', config['mongodb']['port'])
    db = conn[config['mongodb']['db']]
    return db


def init_flask():
    """Initialize Flask Webservice."""
    # Open MongoDB needed for answering request
    db = open_mongo()

    # Define Flask Webservice
    app = Flask(__name__)

    anom_args = {
        'collection': fields.Str(missing='bitcoin'),
        'start': fields.Int(missing=0),
        'end': fields.Int(missing=0),
        'hours': fields.Int(missing=1),
    }

    @app.route('/esd', methods=['GET'])
    @use_args(anom_args)
    def detect_anoms(args):
        """Handle incoming request, send back anomalies."""
        logger.info('Received request.')
        result = {}
        df = agg_tweets(db, args['collection'], args[
                        'start'], args['end'], args['hours'])

        result['agg_hours'] = args['hours']
        result['values_count'] = len(df)
        result['anomalies'] = detect_anomalies(df, args['hours'])
        logger.info('Sending result:', result)
        return json.dumps(result)
    return app


if __name__ == '__main__':
    app = init_flask()
    app.run(host='0.0.0.0', port=5001, debug=True)
