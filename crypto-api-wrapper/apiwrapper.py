"""
Wraps the CryptoCompare API.

- Connects to CryptoCompare API.
- Requests values for the defined currencies
- Aggregate multiple requests if necessary
- Makes own API available to be called from the dashboard
"""

from flask import Flask, request, abort
from flask_restful import Resource, Api
import time
from datetime import date
from flask_jsonpify import jsonify
import math
import requests
import yaml
import random
import json
import logging
from pymongo import MongoClient
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

with open('../config.yaml', 'r') as stream:
    config = yaml.load(stream)

# conn = MongoClient(self.config['mongodb']['host'],
                   #self.config['mongodb']['port'])
# Use local mongo-container IP for testing
conn = MongoClient('127.0.0.1', 27017)
db = conn[config['mongodb']['db']]

def isInt(s):
    if s is None:
        return False
    try:
        int(s)
        return True
    except ValueError:
        return False

def getStepsBetween(step, firstTs, secondTs):
    if step == 'day':
        oneUnit = 86400
    elif step == 'hour':
        oneUnit = 3600
    elif step == 'minute':
        oneUnit = 60
    return math.ceil((secondTs - firstTs)/float(oneUnit))

def parseCoin(coin):
    with open('../config.yaml', 'r') as stream:
        conf = yaml.load(stream)
    allowedCoins = []
    for collection in conf['collections']:
        if 'currencycode' in collection:
            allowedCoins.append(collection['currencycode'])
    if coin in allowedCoins:
        return coin
    else:
        return 'BTC'

def buildParams(currency, coin, limit, to):
    params = { 'fsym': coin, 'tsym': currency, 'limit': limit, 'toTs': to }
    return params

def callExternalApi(step, params):
    with open('../config.yaml', 'r') as stream:
        conf = yaml.load(stream)
    url = '{}{}'.format(conf['cryptocompare']['histo'], step)
    response = requests.get(url, params=params)
    parsedResponse = json.loads(response.content)
    return parsedResponse

def parseStep(step):
    allowedSteps = ['day', 'hour', 'minute']
    if step in allowedSteps:
        return step
    else:
        return 'day'

def parseCurrency(currency):
    allowedCurrencies = ['EUR', 'USD']
    if currency in allowedCurrencies:
        return currency
    else:
        return 'EUR'

def handleTs(ts, now):
    if ts is None and not isInt(ts):
        return now
    elif isInt(ts) and int(ts) > now:
        return now
    else:
        return int(ts)

def calculateLimit(fromTs, toTs, step):
    if isInt(fromTs):
        limit = getStepsBetween(step, int(fromTs), toTs)
    else:
        limit = 30
    return limit

def parseTopics(topicstring):
    if topicstring is None:
        return ['bitcoin']
    else:
        topicList = topicstring.split(',')
        return topicList

def parseAmount(amount):
    if amount is None and not isInt(amount):
        return 20
    else:
        return int(amount)

def getTweetsForTopics(topicstring, amount, fromTs, toTs):
    topicList = parseTopics(topicstring)
    randomTweets = []
    for topic in topicList:
        cursor = db[topic].aggregate([
                { '$match': { 'timestamp_ms': {'$gt': fromTs , '$lt': toTs }}},
                { '$sample': { 'size': amount } },
                { '$project' : { '_id': 0 } }
            ])
        tweetListForTopic = list(cursor)
        randomTweets = randomTweets + tweetListForTopic
    if len(randomTweets) >= amount:
        randomListFinal = random.sample(randomTweets, amount)
    else:
        randomListFinal = randomTweets
    resultDict = {'tweets': randomListFinal }
    return resultDict



class HistoricalPrices(Resource):
    def get(self):
        now = int(time.time())

        toTs = handleTs(request.args.get('to'), now)
        fromTs = request.args.get('from')
        currency = parseCurrency(request.args.get('currency'))
        coin = parseCoin(request.args.get('coin'))
        step = parseStep(request.args.get('step'))

        limit = calculateLimit(fromTs, toTs, step)

        params = buildParams(currency, coin, limit, toTs)

        result = callExternalApi(step, params)

        #     result = {'from': getDaysBetween(fromTs, now), 'to': toTs}
        # else:
        #     result = abort(400, 'Missing `from` and/or `to` timestamp')
        return jsonify(result)

class RandomTweets(Resource):
    def get(self):
        now = int(time.time())

        toTs = handleTs(request.args.get('to'), now) * 1000
        fromTs = handleTs(request.args.get('from'), now) * 1000

        topicstring = request.args.get('topics')
        amount = parseAmount(request.args.get('amount'))

        result = getTweetsForTopics(topicstring, amount, fromTs, toTs)
        return jsonify(result)

api.add_resource(HistoricalPrices, '/price')
api.add_resource(RandomTweets, '/tweets')

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8060)
