"""
Wraps the CryptoCompare API.

- Connects to CryptoCompare API.
- Requests values for the defined currencies
- Aggregate multiple requests if necessary
- Makes own API available to be called from the dashboard
"""

from flask import Flask, request, abort
from flask_restful import Resource, Api
from flask.ext.jsonpify import jsonify
from flask.ext.aiohttp import AioHTTP
import time
from datetime import date
import math
import requests
import yaml
import json
import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

def isInt(s):
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
    allowedCoins = ['ETH', 'BTC', 'IOT']
    if coin in allowedCoins:
        return coin
    else:
        return 'BTC'

def buildParams(currency, coin, limit, to):
    params = { 'fsym': coin, 'tsym': currency, 'limit': limit, 'toTs': to }

def callExternalApi(step, params):
    url = '{}{}'.format(requests.get(conf['cryptocompare']['histo'], step)
    

    return data

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

def handleToTs(toTs, now):
    if toTs is None or toTs > now or not isInt(toTs):
        return now
    else:
        return toTs

def calculateLimit(fromTs, toTs, step):
    if fromTs is not None and isInt(fromTs):
        limit = getStepsBetween(step, fromTs, toTs)
    else:
        limit = 30
    return limit


class HistoricalPrices(Resource):
    def get(self):
        now = int(time.time())

        toTs = handleToTs(request.args.get('to'))
        fromTs = request.args.get('from')
        currency = parseCurrency(request.args.get('currency'))
        coin = parseCoin(request.args.get('coin'))
        step = parseStep(request.args.get('step'))

        limit = calculateLimit(fromTs, toTs)

        params = buildParams(currency, coin, limit, toTs)

        result = callExternalApi(step, params)

        return jsonify(result)

api.add_resource(HistoricalPrices, '/price')

if __name__ == '__main__':
     app.run(port=8060)
