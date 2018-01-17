"""
Provides a Web Service that does Anomaly Detection.

Parameters are:
- List of values of a timeseries
- Frequence of the timeseries
- Desired p value

Example BODY json/application:
{
"ary": [112, 118, 132, 129, 121, 135, 148, 148, 136, 119, 104, 118, 115, 126,
 141, 135, 125, 149, 170, 170, 158, 133, 114, 140, 145, 150, 178, 163, 172,
 178, 199, 199, 184, 162, 146, 166, 171, 180, 193, 181, 183, 218, 230, 242,
 209, 191, 172, 194, 196, 196, 236, 235, 229, 243, 264, 272, 237, 211, 180,
 201, 204, 188, 235, 227, 234, 264, 302, 293, 259, 229, 203, 229, 242, 233,
 267, 269, 270, 315, 364, 347, 312, 274, 237, 278, 284, 277, 317, 313, 318,
 374, 413, 405, 355, 306, 271, 306, 315, 301, 356, 348, 355, 422, 465, 467,
 404, 347, 305, 336, 340, 318, 362, 348, 363, 435, 491, 505, 404, 359, 310,
 337, 360, 342, 406, 396, 420, 472, 548, 559, 463, 407, 362, 405, 417, 391,
 419, 461, 472, 535, 622, 606, 508, 461, 390, 432],
"freq": 12,
"p": 0.95
}
"""

import json
from flask import Flask, abort, request
import statsmodels.api as sm
import numpy as np
from PyAstronomy import pyasl
import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_anomalies(ary, freq, p):
    """Use Seasonal Decompose and ESD on residual to detect anomalies."""
    # Seasonal decompose
    model = sm.tsa.seasonal_decompose(ary, freq=freq)

    # We only use residue values here
    resid = model.resid

    # Count leading Nan, which are going to be dropped for ESD
    # but have to be taken into account for the results
    dropped = 0
    for val in resid:
        if np.isnan(val):
            dropped += 1
        else:
            break

    # Remove NaNs, as ESD doesn't handle them well
    resid_cleaned = [x for x in resid if not np.isnan(x)]

    # Use ESD to detect anomalies
    anomalies = pyasl.generalizedESD(resid_cleaned, 20, p)

    # Get the indexed of the anomalies (index of resid_cleaned + dropped)
    idx_anoms = [x + dropped for x in anomalies[1]]

    # Convert np.int64 to standard int to make it serializable in json
    idx_anoms = [x.item() for x in idx_anoms]

    return idx_anoms, len(resid_cleaned)


def init_flask():
    """Initialize Flask Webservice."""
    # Define Flask Webservice
    app = Flask(__name__)

    @app.route('/esd', methods=['POST'])
    def detect_anoms():
        """Handle incoming request, send back anomalies."""
        logger.info('Received request.')
        print(request)
        if not request.json:
            logger.warn('No valid JSON in Request.')
            abort(400)

        data = request.get_json()

        # Sanitize Request
        if 'ary' not in data:
            abort(400)
            logger.warn('No data sent.')
        if ('freq' not in data):
            data['freq'] = 24
            logger.info('Using default freqency of 24.')
        if ('p' not in data):
            data['p'] = 0.05
            logger.info('Using default freqency of 0.05.')

        # Build Response
        res = {}
        res['p'] = data['p']
        res['freq'] = data['freq']
        res['values_received'] = len(data['ary'])
        res['idx_anoms'], res['values_used'] = detect_anomalies(data['ary'],
                                                                data['freq'],
                                                                data['p'])
        logger.info('Sending result:', res)
        print(res)
        return json.dumps(res)
    return app


if __name__ == '__main__':
    app = init_flask()
    app.run(host='0.0.0.0', port=5001, debug=True)
