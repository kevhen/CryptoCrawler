"""
Provides a Dashboard.

Creates an interactive Dashboard using Dash from Plotly and exposes
it via port 8050
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as ddp
import plotly.graph_objs as go
import pandas as pd
import yaml
import datetime
import time
import os
import json
from flask import send_from_directory
from pymongo import MongoClient
import requests
import logging
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class dashboard():
    """Control the Dashboard Appearance and functionality."""

    def __init__(self, *args, **kwargs):
        """Prepare class variables on class init."""
        # Load the configuration file
        with open('../config.yaml', 'r') as stream:
            self.config = yaml.load(stream)

        # Open Connection to MongoDB
        self.config['mongodb']['host'] = '172.18.0.2'
        conn = MongoClient(self.config['mongodb']['host'],
                           self.config['mongodb']['port'])
        # Use local mongo-container IP for testing
        # conn = MongoClient('127.0.0.1', 27017)  # Holger
        self.db = conn[self.config['mongodb']['db']]

        # Helper Variable for timestamp conversion
        self.epoch = datetime.datetime.utcfromtimestamp(0)

        # twitter topics / collections
        self.topics = [i for i in self.config['collections']]
        self.topics_default = self.config['dash']['live']['default']

        # Interval for updating live charts
        self.update_interval = int(self.config['dash']['live']['interval'])

        logger.info('Init Dashboard')
        logger.info('Live Update Interval: {} s'.format(self.update_interval))

        # Set colors for collection:
        self.colors = {
            'generalcrypto': '#DB56B2',
            'bitcoin': '#DBC256',
            'BTC': '#DBC256',
            'ethereum': '#56DB7F',
            'ETH': '#56DB7F',
            'iota': '#56D3DB',
            'IOT': '#56D3DB',
            'trump': '#CE0000',
            'car2go': '#A056DB',
            'collection': 'black'
        }

        # Helper Variable to detect new button clicks:
        self.topic_btn_clicks = 0

        # Draw Dashboard
        self.init_dash()

    # ============================================
    # Helper Methods
    # ============================================

    def unix_time(self, dt):
        """Convert DateTime object to Unixtimestamp in ms."""
        return round((dt - self.epoch).total_seconds() * 1000.0)

    def get_x(self, rd):
        """Get xaxis range settings from layout data."""
        set_range = {'autorange': True}
        if (rd is not None) and \
                (('xaxis.autorange' in rd) or
                 ('yaxis.autorange' in rd)):
            return set_range
        if (rd is not None) and \
                ('xaxis.range[0]' in rd) and \
                ('xaxis.range[1]' in rd):
            set_range = {'range': [
                rd['xaxis.range[0]'],
                rd['xaxis.range[1]']
            ]}
        return set_range

    # ============================================
    # Data Querying & prepartion related Methods
    # ============================================

    def query_mongo(self, collections, query={}, fields={}):
        """Query MongoDB and return results as pandas dataframe.

        collections <List> : Mongo Collections to query
        query <Dict> : MongoDB Query Object (to filter observations)
        fields <Dict> : MongoDB Fields Object (to filter fields)

        return <DataFrame> : tweets from mongoDB
        """
        # We can't query multiple colletions with pyMongo, therefore
        # we loop through all needed collections, query one by one and
        # append to a single dataframe with an additional field "collection"
        df = None
        for collection in collections:
            cursor = self.db[collection].find(query, fields)
            df_temp = pd.DataFrame(list(cursor))
            df_temp['collection'] = collection
            if df is None:   # if we do not have a df yet, create it ...
                df = df_temp
            else:            # ... else append to it:
                df = df.append(df_temp, ignore_index=True)

        # Remove the mongo-row-id, as it's not needed
        if (df is not None) and ('_id' in df.columns):
            del df['_id']

        return df

    def get_live_data(self, collections, live_range):
        """Query MongoDB and return a pandas dataframe.

        collections <List> : Mongo Collections to query
        live_range <Int> : amount of past seconds to query

        return <DataFrame> : tweets per collection per update_interval
        """
        # Calculate start time for query in mongodb based on live_range,
        # but has to be one update_interval more, because of grouping issues
        # on left side for timespan:
        start_datetime = datetime.datetime.utcnow() \
            - datetime.timedelta(minutes=live_range,
                                 seconds=self.update_interval)

        # Convert to ms timestamp
        start_ms = self.unix_time(start_datetime)

        # Query the mongo db
        df = self.query_mongo(collections, {'timestamp_ms': {
                              "$gt": start_ms}}, {'timestamp_ms': 1})

        # Convert to datetime
        if (df is None) or (len(df) < 3):
            logger.error('No data for live dashboard!')
            return df

        df['timestamp_ms'] = pd.to_datetime(df['timestamp_ms'], unit='ms')

        # Define Grouper
        agg_time = str(self.update_interval) + 'S'  # group by x seconds
        grouper = pd.Grouper(key='timestamp_ms', freq=agg_time)

        # Group and aggregate
        df_result = df.groupby([grouper, 'collection'])
        df_result = df_result['timestamp_ms'].count(
        ).unstack('collection').fillna(0)

        # Drop first values, because the values for the left side of timespan
        # is missleading:
        df_result = df_result.drop(df_result.index[0])

        return df_result

    def get_agg_data(self, collections, attr):
        """Query MongoDB and return a pandas dataframe.

        collections <List> : Mongo Collections to query

        return <DataFrame> : tweets per collection per 5 minutes
        """
        # Query the mongo db
        df = None
        agg_range = 1000 * 60 * 60  # by hours
        for collection in collections:
            # Mongodb aggregation magic....
            cursor = self.db[collection].aggregate([
                {
                    '$addFields': {
                        'div_val': {'$divide': ['$timestamp_ms', agg_range]},
                    }
                },
                {
                    '$addFields': {
                        'mod_val': {'$mod': ['$div_val', 1]}
                    }
                },
                {
                    '$addFields': {
                        'sub_val': {'$subtract': ['$div_val', '$mod_val']},
                    }
                },
                {
                    '$group': {
                        '_id': '$sub_val',
                        attr: {'$avg': '$' + attr},
                        'count': {'$sum': 1}
                    }
                }])

            df_temp = pd.DataFrame(list(cursor))
            df_temp['collection'] = collection
            if df is None:   # if we do not have a df yet, create it ...
                df = df_temp
            else:            # ... else append to it:
                df = df.append(df_temp, ignore_index=True)

        # Restore the actual time stamps, which got "compressed"
        # during mongodb aggregation
        if df is not None:
            df['timestamp_ms'] = df['_id'].astype(int).multiply(agg_range)

            # Remove the mongo-row-id, as it's not needed
            if '_id' in df.columns:
                del df['_id']

            # Convert to datetime
            df['timestamp_ms'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
        else:
            df = pd.DataFrame()

        return df

    def get_anomalies(self, s):
        """Query anomaly detection service, return anomaly data for charts."""
        url = 'http://crypto-anoms:5001/esd'
        # url = 'http://127.0.0.1:5001/esd'

        data = [float(i) for i in s.values.tolist()]
        payload = {
            "ary": data,
            "freq": 24,  # as data is aggregated by hour
            "p": 0.15  # Treshold for significance
        }
        response = requests.post(url, json=payload)

        result = []
        if response.ok:
            content = json.loads(response.content)
            if 'idx_anoms' in content:
                result = content['idx_anoms']

        s_result = s.iloc[result]
        return s_result

    def get_topics(self, coll, start_ms, end_ms, number):
        """Query anomaly detection service, return anomaly data for charts."""
        url = 'http://crypto-topics:5000/lda'
        # url = 'http://172.18.0.4:5000/lda'  # Local, Holger

        payload = (
            ('collection', coll),
            ('start', start_ms),
            ('end', end_ms),
            ('topics', number)
        )
        response = requests.get(url, params=payload)

        result = None
        if response.ok:
            result = json.loads(response.content)

        return result

    def buildTweet(self, text, timeString):
        timeIso = datetime.datetime.fromtimestamp(
            int(timeString) / 1000).strftime('%A, %d. %B %Y %I:%M%p')
        tweet = html.Div([
            html.Blockquote([
                html.Div([
                    html.Div([
                        html.Img(
                            src='/static/Twitter_Social_Icon_Circle_Color.svg', className='Icon')
                    ], className='Tweet-brand')
                ], className='Tweet-header'),
                html.Div([
                    html.P([
                        text
                    ], className='Tweet-text'),
                    html.Div([
                        timeIso
                    ], className='Tweet-metadata')
                ], className='Tweet-body')
            ])
        ], className='EmbeddedTweet')
        return tweet

    # ============================================
    # Dash/Charting related methods
    # ============================================

    def init_dash(self):
        """Load the inital Dataset and show it in initial layout."""
        app = dash.Dash()

        # The following config were neccessary, as the CDN serving the files
        # seems to be unstable.
        app.css.config.serve_locally = True
        app.scripts.config.serve_locally = True

        # Values for Checkboxes
        topics_options = [{'label': i, 'value': i}
                          for i in self.topics]

        # Layout of Dashboard
        app.layout = html.Div([
            html.Link(
                rel='stylesheet',
                href='/static/style.css'
            ),
            html.Link(
                rel='stylesheet',
                href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
            ),

            # Header
            html.Div([
                html.H1('Crypto Crawler\'s Dashboard'),
                html.Img(
                    src='/static/logo.png'),
            ], className='banner'),

            # Live Tweets
            html.Div([
                html.Div([
                    html.H3(
                        'Tweets per {} sec.' \
                        .format(self.update_interval))
                ], className='title'),
                html.Div([
                    # Dropdown to select time range for Live Tweet Chart
                    dcc.Dropdown(
                        id='tweets-live-dropdown',
                        options=[
                            {'label': 'Stop', 'value': 0},
                            {'label': 'Last minute', 'value': 1},
                            {'label': 'Last 5 min', 'value': 5},
                            {'label': 'Last 15 min', 'value': 15},
                            {'label': 'Last 30 min', 'value': 30}
                        ],
                        value=5
                    ),
                    # Chart for Live Tweets
                    dcc.Graph(
                        id='tweets-live-plot',
                        style={'width': '878px', 'height': '200px'},
                        figure=self.plot_live_tweets(
                            self.topics_default, 5),
                        config={
                            'displayModeBar': False
                        })
                ], className='content')
            ], className='live-box'),

            # Hidden element to store data
            # See: https://plot.ly/dash/sharing-data-between-callbacks
            html.Div(id='hidden-tweet-data', style={'display': 'none'}),
            html.Div(id='hidden-stock-data', style={'display': 'none'}),
            html.Div(id='hidden-layout-data', style={'display': 'none'}),

            # Topic Selection
            html.Div([
                html.Div([
                    html.H3("Topic Selection")
                ], className='title'),
                html.Div([
                    dcc.Checklist(
                        id='global-topic-checklist',
                        options=topics_options,
                        values=self.topics_default
                    ),
                ], className='content')
            ], className='box'),

            # Overall Tweets per Hour
            html.Div([
                html.Div([
                    html.H3([
                        html.Span('∑', className='icon'),
                         'Tweets per Hour'])
                ], className='title'),
                html.Div([
                    dcc.Checklist(
                        id='tweet-anoms-toggle',
                        options=[
                            {'label': 'Show Anomalies',
                             'value': 'anoms'}
                        ],
                        className='anoms-toggle',
                        values=[]
                    ),
                ], className='content'),
                html.Div([
                    # Chart for All Tweets
                    dcc.Graph(
                        style={'width': '878px', 'height': '250px'},
                        id='tweets-plot')
                ], className='content')
            ], className='box'),

            # Sentiment per Hour
            html.Div([
                html.Div([
                    html.H3([
                        html.Span('☺', className='icon'),
                         'Avg. Sentiment per Hour'])
                ], className='title'),
                html.Div([
                    dcc.Checklist(
                        id='senti-anoms-toggle',
                        options=[
                            {'label': 'Show Anomalies',
                             'value': 'anoms'}
                        ],
                        className='anoms-toggle',
                        values=[]
                    ),
                ], className='content'),
                html.Div([
                    dcc.Graph(
                        style={'width': '878px', 'height': '250px'},
                        id='senti-plot')
                ], className='content')
            ], className='box'),

            # Prices per Hour
            html.Div([
                html.Div([
                    html.H3([
                        html.Span('€', className='icon'),
                         'Avg. Stock Prices per Hour'])
                ], className='title'),
                html.Div([
                    dcc.Checklist(
                        id='stock-anoms-toggle',
                        options=[
                            {'label': 'Show Anomalies',
                             'value': 'anoms'}
                        ],
                        values=[],
                        className='anoms-toggle'
                    ),
                ], className='content'),
                html.Div([
                    dcc.Graph(
                        style={'width': '878px', 'height': '250px'},
                        id='stock-plot')
                ], className='content')
            ], className='box'),

            # Random Tweets
            html.Div([
                html.Div([
                    html.H3([
                        html.Span(className='fa fa-twitter icon'),
                         'Random tweets for the selected topic']),
                    html.Button(className='fa fa-refresh refresh',
                                id='refresh-tweets-button')
                ], className='title'),
                html.Div([
                ], id='tweetbox', className='content')
            ], className='box'),

            # Topic Models
            html.Div([
                html.Div([
                    html.H3([
                        html.Span(className='fa fa-newspaper-o icon'),
                         'Identify Topics'])
                ], className='title'),
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            options=[{'label': i, 'value': i}
                                     for i in self.topics],
                            value='bitcoin',
                            id='topic-collection-dropdown'
                        ),
                        dcc.DatePickerRange(
                            id='topic-date-picker',
                            start_date=datetime.datetime(2018, 1, 1, 0, 0, 0),
                            end_date=datetime.datetime(2018, 2, 1, 0, 0, 0),
                            end_date_placeholder_text='Select a date!'
                        ),
                        dcc.Input(
                            placeholder='No. of Topics...',
                            type='number',
                            value=5,
                            min=2,
                            max=10,
                            inputmode='numeric',
                            id='topic-number-input'
                        ),
                        html.Button(className='fa fa-search',
                                    id='topic-button')
                    ], className='settings-bar'),
                    html.Div([
                        html.Div([html.Span(className='fa fa-arrow-circle-o-up'),
                                  'Make your selection and wait some Minutes!'],
                                 className='topic-placeholder')
                    ], id='topic-results')
                ], id='topicbox', className='content')
            ], className='box'),

            # Footer
            html.Div(
                'Build in 01/2018 by kevhen & dynobo with ❤ and Plotly Dash',
                id='bottom-line'),
            dcc.Interval(id='live-update',
                         interval=1000 * self.update_interval),
        ],  className='container')

        @app.server.route('/static/<path:path>')
        def static_file(path):
            static_folder = os.path.join(os.getcwd(), 'static')
            return send_from_directory(static_folder, path)

        @app.callback(
            dash.dependencies.Output('tweetbox', 'children'),
            [ddp.Input(component_id='global-topic-checklist',
                       component_property='values'),
             ddp.Input(component_id='refresh-tweets-button',
                       component_property='n_clicks'),
             ddp.Input('tweets-plot', 'relayoutData'),
             ddp.Input('senti-plot', 'relayoutData'),
             ddp.Input('stock-plot', 'relayoutData')],
            [],
            [])
        def returnUpdatedTweetbox(topic_values, n_clicks, rd_tweets, rd_senti, rd_stock):
            timeframe = {}
            if rd_tweets is not None:
                timeframe = rd_tweets
            if rd_senti is not None:
                timeframe = rd_senti
            if rd_stock is not None:
                timeframe = rd_stock
            if 'xaxis.range[0]' in timeframe:
                fromTs = convertDate(timeframe['xaxis.range[0]'])
            else:
                fromTs = 0
            if 'xaxis.range[1]' in timeframe:
                toTs = convertDate(timeframe['xaxis.range[1]'])
            else:
                toTs = 999999999999
            payload = {
                "topics": ','.join(topic_values),
                "amount": 5,
                "from": fromTs,
                "to": toTs
            }
            tweets = []

            response = requests.get('http://crypto-api-wrapper:8060/tweets', params=payload)
            # response = requests.get('http://127.0.0.1:8060/tweets', params=payload)  # Kevin
            # response = requests.get('http://172.18.0.2:8060/tweets', params=payload)  # Holger

            if response.ok:
                content = json.loads(response.content)
                for tweet in content['tweets']:
                    singleTweet = self.buildTweet(
                        tweet['text'], tweet['timestamp_ms'])
                    tweets.append(singleTweet)

            return html.Div(tweets)

        def convertDate(dateString):
            utc_dt = datetime.datetime.strptime(
                dateString, '%Y-%m-%d %H:%M:%S.%f')
            timestamp = (utc_dt - datetime.datetime(1970, 1, 1)
                         ).total_seconds() + 3600
            return int(timestamp)

        @app.callback(
            ddp.Output('tweets-live-plot', 'figure'),
            [ddp.Input(component_id='global-topic-checklist',
                       component_property='values'),
             ddp.Input(component_id='tweets-live-dropdown',
                       component_property='value')],
            [],
            [ddp.Event('live-update', 'interval')])
        def update_live_timeseries(topic_values, live_range):
            # Do nothing, if Live Chart is set to "off" (value = 0)
            if (live_range == 0) or (live_range is None):
                return
            return self.plot_live_tweets(topic_values, live_range)

        @app.callback(ddp.Output('hidden-tweet-data', 'children'),
                      [ddp.Input(component_id='global-topic-checklist',
                                 component_property='values')])
        def clean_tweet_data(topic_values):
            # Query for Data
            df = self.get_agg_data(topic_values, 'score')

            if (df is None) or (len(df) < 1 or ('timestamp_ms' not in df.columns.values)):
                df_empty = pd.DataFrame()
                data = (df_empty.to_json(
                    date_format='iso', orient='split') + "\n") * 3
                return data

            # Group and aggregate
            df = df.groupby(['timestamp_ms', 'collection'])
            df_score = df['score'].mean().unstack('collection').fillna(0)
            df_count = df['count'].sum().unstack('collection').fillna(0)

            # Get Anomalies for count
            df_anoms_count = pd.DataFrame()
            for col in df_count.columns.values:
                df_temp = self.get_anomalies(df_count[col])
                df_anoms_count = pd.concat([df_anoms_count, df_temp], axis=1)

            # Get Anomalies for score
            df_anoms_score = pd.DataFrame()
            for col in df_score.columns.values:
                df_temp = self.get_anomalies(df_score[col])
                df_anoms_score = pd.concat([df_anoms_score, df_temp], axis=1)

            # Jsonfy & concat DFs, then store string in hidden element
            data = df_count.to_json(date_format='iso', orient='split') \
                + "\n" + \
                df_score.to_json(date_format='iso', orient='split') \
                + "\n" + \
                df_anoms_count.to_json(date_format='iso', orient='split') \
                + "\n" + \
                df_anoms_score.to_json(date_format='iso', orient='split') \

            return data

        @app.callback(ddp.Output('hidden-stock-data', 'children'),
                      [ddp.Input(component_id='global-topic-checklist',
                                 component_property='values')])
        def clean_stock_data(topic_values):
            # Get Data
            currencies = {
                'BTC': 'bitcoin',
                'IOT': 'iota',
                'ETH': 'ethereum',
            }
            currency_codes = []
            for key, val in currencies.items():
                if val in topic_values:
                    currency_codes.append(key)

            if len(currency_codes) > 0:
                df = self.get_agg_data(currency_codes, 'EUR')

                # Replace codes with names
                df['collection'] = df['collection'].replace(currencies)

                # Group and aggregate
                df = df.groupby(['timestamp_ms', 'collection'])
                df = df['EUR'].mean().unstack('collection').fillna(0)
            else:
                df = pd.DataFrame()

            # Get Anomalies for score
            df_anoms = pd.DataFrame()
            for col in df.columns.values:
                df_anoms[col] = self.get_anomalies(df[col])

            # Jsonfy & concat DFs, then store string in hidden element
            data = df.to_json(date_format='iso', orient='split') \
                + "\n" + \
                df_anoms.to_json(date_format='iso', orient='split')

            return data

        axises = ['', '', '']  # Used to store axis scales of the three charts

        @app.callback(ddp.Output('hidden-layout-data', 'children'),
                      [ddp.Input('tweets-plot', 'relayoutData'),
                       ddp.Input('senti-plot', 'relayoutData'),
                       ddp.Input('stock-plot', 'relayoutData')])
        def set_layout_data(rd_tweet, rd_senti, rd_stock):
            new_axises = [rd_tweet, rd_senti, rd_stock]
            for idx, val in enumerate(new_axises):
                if val != axises[idx]:
                    axises[idx] = val
                    return json.dumps(val)
            return json.dumps({})

        @app.callback(
            ddp.Output('tweets-plot', 'figure'),
            [ddp.Input('hidden-tweet-data', 'children'),
             ddp.Input('hidden-layout-data', 'children'),
             ddp.Input('tweet-anoms-toggle', 'values')])
        def update_timeseries(jsonified_data, rd_data, toggle):
            data = jsonified_data.split('\n')[0]
            df = pd.read_json(data, orient='split')
            if 'anoms' in toggle:
                anoms = jsonified_data.split('\n')[2]
                df_anoms = pd.read_json(anoms, orient='split')
            else:
                df_anoms = None
            x_axis = self.get_x(json.loads(rd_data))
            return self.plot_timeseries('Tweets', df, df_anoms, x_axis)

        @app.callback(
            ddp.Output('senti-plot', 'figure'),
            [ddp.Input('hidden-tweet-data', 'children'),
             ddp.Input('hidden-layout-data', 'children'),
             ddp.Input('senti-anoms-toggle', 'values')])
        def update_senti(jsonified_data, rd_data, toggle):
            data = jsonified_data.split('\n')[1]
            df = pd.read_json(data, orient='split')
            if 'anoms' in toggle:
                anoms = jsonified_data.split('\n')[3]
                df_anoms = pd.read_json(anoms, orient='split')
            else:
                df_anoms = None
            x_axis = self.get_x(json.loads(rd_data))
            return self.plot_timeseries('Sentiment Score', df, df_anoms, x_axis)

        @app.callback(
            ddp.Output('stock-plot', 'figure'),
            [ddp.Input('hidden-stock-data', 'children'),
             ddp.Input('hidden-layout-data', 'children'),
             ddp.Input('stock-anoms-toggle', 'values')])
        def update_plot(jsonified_data, rd_data, toggle):
            data = jsonified_data.split('\n')[0]
            df = pd.read_json(data, orient='split')
            if 'anoms' in toggle:
                anoms = jsonified_data.split('\n')[1]
                df_anoms = pd.read_json(anoms, orient='split')
            else:
                df_anoms = None
            x_axis = self.get_x(json.loads(rd_data))
            return self.plot_timeseries('€ Stock Price', df, df_anoms, x_axis)

        self.app = app

        @app.callback(
            ddp.Output('topic-results', 'children'),
            [ddp.Input('topic-button', 'n_clicks')],
            [ddp.State('topic-collection-dropdown', 'value'),
             ddp.State('topic-date-picker', 'start_date'),
             ddp.State('topic-date-picker', 'end_date'),
             ddp.State('topic-number-input', 'value'),
             ])
        def update_topics(btn, coll, start_date, end_date, number):
            print(btn)
            placeholder = html.Div([
                html.Span(className='fa fa-arrow-circle-o-up'),
                'Make your selection and wait some Minutes!'],
                className='topic-placeholder')

            if not start_date or not end_date \
                    or not number or not coll or not btn:
                logger.warn('Parameter is missing.')
                return placeholder

            if self.topic_btn_clicks == btn:
                return placeholder
            else:
                self.topic_btn_clicks = btn

            start_ms = int(time.mktime(
                time.strptime(start_date[:10], '%Y-%m-%d'))) * 1000
            end_ms = int(time.mktime(
                time.strptime(end_date[:10], '%Y-%m-%d'))) * 1000

            data = self.get_topics(coll, start_ms, end_ms, number)

            if (not data) or ('topics' not in data):
                logger.warn('No data received.')
                return placeholder

            all_topics = [
                html.Div('Topics from {} Tweets'.format(data['tweet_count']),
                         className='topic-header')
            ]
            for topic in data['topics']:
                topic_html = html.Div([
                    html.Div([
                        t, html.Span('{:.3f}'.format(c)[1:],
                                     className='topic-value')
                    ], className='topic-token') for t, c in topic[:15]
                ],
                    className='topic-row')
                all_topics.append(topic_html)

            return html.Div(all_topics)

        self.app = app

    def plot_live_tweets(self, topics, live_range):
        """Plot the live tweet chart."""
        df = self.get_live_data(topics, live_range)
        # Don't try drawing, if we have no data
        if (df is None) or (len(df) < 1):
            return {'data': [],
                    'layout': go.Layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )}
        figure = {
            'data': [
                go.Scatter(
                    x=df.index,
                    y=df[i],
                    text=df[i].astype('int').astype('str') + ' Tweets',
                    opacity=0.7,
                    name=i,
                    line={'color': self.colors[i]}
                ) for i in df.columns.values
            ],
            'layout': go.Layout(
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                showlegend=True,
                legend={'x': 1.02, 'y': 0.5},
                hovermode='closest',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#7f7f7f'),
                xaxis={'gridcolor': '#5E5E5E',
                       'zerolinecolor': '#5E5E5E', 'linecolor': '#7f7f7f'},
                yaxis={'gridcolor': '#5E5E5E',
                       'zerolinecolor': '#5E5E5E', 'linecolor': '#7f7f7f'},
            )
        }
        return figure

    def plot_timeseries(self, label, df, df_anoms, x_axis):
        """Plot the overall twitter chart."""
        # Don't try drawing, if we have no data
        if (df is None) or (len(df) < 1):
            return {'data': []}

        # Create annotations
        annos = []
        if df_anoms is not None:
            for col in df_anoms.columns.values:
                for idx, item in df_anoms[col].iteritems():
                    if pd.isnull(item):
                        continue
                    annos.append(dict(
                        x=idx,
                        y=item,
                        xref='x',
                        yref='y',
                        arrowcolor=self.colors[col],
                        showarrow=True,
                        arrowhead=6,
                        arrowsize=2,
                        clicktoshow=True,
                        opacity=0.4,
                        ax=-10,
                        ay=-10
                    ))

        # Create chart figure
        figure = {
            'data': [
                go.Scatter(
                    x=df.index,
                    y=df[i],
                    text=df[i].astype('int').astype('str') + ' ' + label,
                    opacity=0.7,
                    name=i,
                    line={'color': self.colors[i]}
                ) for i in df.columns.values
            ],
            'layout': go.Layout(
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                showlegend=True,
                legend={'x': 1.02, 'y': 0.5},
                hovermode='closest',
                xaxis=x_axis,
                annotations=annos
            )
        }

        return figure


if __name__ == '__main__':
    dashboard = dashboard()
    dashboard.app.run_server(host='0.0.0.0', port=8050)
