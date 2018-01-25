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

def handleToTs(toTs, now):
    if toTs is None and not isInt(toTs):
        return now
    elif isInt(toTs) and int(toTs) > now:
        return now
    else:
        return int(toTs)

def calculateLimit(fromTs, toTs, step):
    if isInt(fromTs):
        print('here')
        limit = getStepsBetween(step, int(fromTs), toTs)
    else:
        limit = 30
    return limit


class HistoricalPrices(Resource):
    def get(self):
        now = int(time.time())

        toTs = handleToTs(request.args.get('to'), now)
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

api.add_resource(HistoricalPrices, '/price')

if __name__ == '__main__':
     app.run(port=8060)
