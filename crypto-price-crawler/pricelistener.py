"""
Listens to the CryptoCompare API.

- Connects to CryptoCompare API.
- Requests values for the defined currencies
- Stores the prices in a Mongodb, connection params in config.yaml.
"""

from pymongo import MongoClient
from pymongo import errors as pymongo_errors
import requests
import yaml
import json
import sched, time
import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

def checkCurrencies(conf):
    """Checks if the currency from the config.yaml is a valid currency and returns a dictionary with the valid checkCurrencies in the form"""
    response = requests.get(conf['cryptocompare']['coinlist'])
    if response.status_code == 200:
        coinList = json.loads(response.content)
        coins = coinList['Data']
        validCoins = []
        for key, item in conf['collections'].items():
            if 'currencycode' in item:
                if item['currencycode'] in coins:
                    validCoins.append(item['currencycode'])
        logger.info('Valid coins are {}'.format(validCoins))
        return validCoins
    else:
        return False

def buildCoinString(validCoins):
    """Concats the valid coins to use them in the API call"""
    coinString = ','.join(validCoins)
    logger.info('The coin string is {}'.format(coinString))
    return coinString

def getPricesOnce(currencies, conf):
    """Gets the current price for the currencies defined in the config.yaml"""
    payload = { 'fsyms': currencies, 'tsyms': 'USD,EUR' }
    response = requests.get(conf['cryptocompare']['price'], params=payload)
    if response.status_code == 200:
        prices = json.loads(response.content)
        logger.info('Prices are {}'.format(prices))
        return prices
    else:
        logger.warn('Could not get prices. Error code {}'.format(response.status_code))
        return False

def saveToMongo(db, prices):
    timestamp_ms = millis = int(round(time.time() * 1000))
    logger.info('Trying to save the prices for timestamp {} to mongo'.format(timestamp_ms))
    for currencycode, item in prices.items():
        document = item
        document['timestamp_ms'] = timestamp_ms
        # Try saving to mongo, delay on auto reconnect (e.g. container down)
        try:
            # Store in mongo collection(s)
            db[currencycode].insert(document)
        except pymongo_errors.AutoReconnect:
            logger.error('Pymongo auto reconnect. Wait for some seconds...')
            time.sleep(5)

def startListening(conf, db, scheduler):
    logger.info('Starting Currency Listener')
    validCoins = checkCurrencies(conf)
    if validCoins:
        coinString = buildCoinString(validCoins)
        prices = getPricesOnce(coinString, conf)
        if prices:
            saveToMongo(db, prices)
        else:
            logger.warn('Prices could not be retrieved. Skipping this timestamp')
    else:
        logger.warn('Valid coins could not be retrieved. Skipping this step')

    scheduler.enter(10, 1, startListening, (db,scheduler,))

def init():
    with open('../config.yaml', 'r') as stream:
        conf = yaml.load(stream)
    # Open a connection to mongo:
    client = MongoClient(conf['mongodb']['host'], conf['mongodb']['port'])
    db = client[conf['mongodb']['db']]
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.run()
    startListening(conf,db,scheduler)

if __name__ == '__main__':
    init()
