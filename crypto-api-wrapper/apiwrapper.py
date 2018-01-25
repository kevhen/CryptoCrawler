"""
Wraps the CryptoCompare API.

- Connects to CryptoCompare API.
- Requests values for the defined currencies
- Aggregate multiple requests if necessary
- Makes own API available to be called from the dashboard
"""

from flask import Flask, request
from flask_restful import Resource, Api
from flask.ext.jsonpify import jsonify
import requests
import yaml
import json
import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

class HistoricalPrices(Resource):
    def get(self):
        param = request.args.get('testparam')
        result = {'data': param}
        return jsonify(result)

api.add_resource(HistoricalPrices, '/price')

if __name__ == '__main__':
     app.run(port=8060)
