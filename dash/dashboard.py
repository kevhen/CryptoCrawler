"""
Provides a Dashboard.

Creates an interactive Dashboard using Dash from Plotly and exposes
it via port 80
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as ddp
import plotly.graph_objs as go
import pandas as pd
import yaml
import datetime
import os
from flask import send_from_directory
from pymongo import MongoClient


class dashboard():
    """Control the Dashboard Appearance and functionality."""

    def __init__(self, *args, **kwargs):
        """Prepare class variables on class init."""
        # Load the configuration file
        with open('../twitter-listener/config.yaml', 'r') as stream:
            self.config = yaml.load(stream)

        # Open Connection to MongoDB
        conn = MongoClient(self.config['mongodb']['host'],
                           self.config['mongodb']['port'])
        # Use local mongo-container IP for testing
        #conn = MongoClient('172.17.0.2', self.config['mongodb']['port'])
        self.db = conn[self.config['mongodb']['db']]

        # Helper Variable for timestamp conversion
        self.epoch = datetime.datetime.utcfromtimestamp(0)

        # twitter topics / collections
        self.topics = [i for i in self.config['collections']]

        # Interval for updating live charts
        self.update_interval = 5

        # Draw Dashboard
        self.init_dash()

    # ============================================
    # Helper Methods
    # ============================================

    def unix_time(self, dt):
        return round((dt - self.epoch).total_seconds() * 1000.0)

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
        if '_id' in df.columns:
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
                              "$gt": str(start_ms)}}, {'timestamp_ms': 1})

        # Convert to datetime
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

        # Initially, use all collections
        topics_options = [{'label': i, 'value': i}
                          for i in self.topics]

        # Layout of Dashboard
        app.layout = html.Div([
            html.Link(
                rel='stylesheet',
                href='/static/style.css'
            ),

            # Header
            html.Div([
                html.H1('Crypto Crawler\'s Dashboard'),
                html.Img(
                    src='/static/logo.png'),
            ], className='banner'),

            # Topic Selection
            html.Div([
                html.Div([
                    html.H3("Topic Selection")
                ], className='title'),
                html.Div([
                    dcc.Checklist(
                        id='global-topic-checklist',
                        options=topics_options,
                        # select only crypto currency topics by default
                        values=self.topics.remove('trump').remove('car2go')
                    ),
                ], className='content')
            ], className='box'),

            # Live Tweets
            html.Div([
                html.Div([
                    html.H3(
                        'Tweets - Live Count - {} sec. per Tick'.format(self.update_interval))
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
                            {'label': 'Last 30 min', 'value': 20}
                        ],
                        value=5
                    ),
                    # Chart for Live Tweets
                    dcc.Graph(
                        id='tweets-live-plot',
                        # Initialize figure with all topics and 1
                        # min timerange
                        figure=self.plot_live_tweets(
                            self.topics, 5),
                        config={
                            'displayModeBar': False
                        })
                ], className='content')
            ], className='box'),
            html.Div(
                'Build in January 2018 by kevhen & dynobo with ❤ and Plotly Dash', id='bottom-line'),
            dcc.Interval(id='live-update',
                         interval=1000 * self.update_interval),
        ],  className='container')

        @app.server.route('/static/<path:path>')
        def static_file(path):
            static_folder = os.path.join(os.getcwd(), 'static')
            return send_from_directory(static_folder, path)

        @app.callback(
            ddp.Output('tweets-live-plot', 'figure'),
            [ddp.Input(component_id='global-topic-checklist', component_property='values'),
             ddp.Input(component_id='tweets-live-dropdown', component_property='value')],
            [],
            [ddp.Event('live-update', 'interval')])
        def update_timeseries(topic_values, live_range):
            # Do nothing, if Live Chart is set to "off" (value = 0)
            if (live_range == 0) or (live_range is None):
                return
            return self.plot_live_tweets(topic_values, live_range)

        self.app = app

    def plot_live_tweets(self, topics, live_range):
        df = self.get_live_data(topics, live_range)
        figure = {
            'data': [
                go.Scatter(
                    x=df.index,
                    y=df[i],
                    text=df[i].astype('int').astype('str') + ' Tweets',
                    opacity=0.7,
                    name=i
                ) for i in df.columns.values
            ],
            'layout': go.Layout(
                xaxis={'title': 'Time'},
                yaxis={'title': 'Tweets'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                showlegend=True,
                legend={'x': 1, 'y': 0},
                hovermode='closest'
            )
        }
        return figure


if __name__ == '__main__':
    dashboard = dashboard()
    dashboard.app.run_server(host='0.0.0.0')
