"""
Provides a Dashboard.

Creates an interactive Dashboard using Dash from Plotly and exposes
it via port 80
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import yaml
from pymongo import MongoClient


def query_mongo(db, collections, query={}, fields={}):
    """Query MongoDB and return a pandas dataframe."""
    df = None
    for collection in collections:
        cursor = db[collection].find()
        df_temp = pd.DataFrame(list(cursor))
        df_temp['collection'] = collection
        if df is None:
            df = df_temp
        else:
            df = df.append(df_temp, ignore_index=True)
    del df['_id']
    return df


def get_timeseries_data(db, collections):
    """Query MongoDB and return a pandas dataframe."""
    df = query_mongo(db, collections, {}, {'timestamp'})
    df['timestamp'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
    df.index = df['timestamp']
    del df['timestamp']

    grouper = df.groupby([pd.TimeGrouper('10T'), 'collection'])
    df_result = grouper['id'].count().unstack('collection').fillna(0)

    return df_result


def init_dash(conf):
    """Load the inital Dataset and show it in initial layout."""
    app = dash.Dash()

    # The following config were neccessary, as the CDN serving the files
    # seems to be unstable.
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True

    # Initially, use all collections
    topics_options = [{'label': i, 'value': i} for i in conf['collections']]
    topics_initial = [i for i in conf['collections']]

    df = get_timeseries_data(db, topics_initial)

    app.layout = html.Div([
        html.Label('Select topics for visualization'),
        dcc.Checklist(
            options=topics_options,
            values=topics_initial
        ),
        dcc.Graph(
            id='life-exp-vs-gdp',
            figure={
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
                    xaxis={'title': 'Count of Tweets'},
                    yaxis={'title': 'Timespan'},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }
        )
    ])

    return app


if __name__ == '__main__':
    # Load the configuration file
    with open('../twitter-listener/config.yaml', 'r') as stream:
        conf = yaml.load(stream)

    # Open Connection to MongoDB
    #conn = MongoClient(conf['mongodb']['host'], conf['mongodb']['port'])
    conn = MongoClient('172.17.0.2', conf['mongodb']['port']) # Use local mongo-container IP for testing
    db = conn[conf['mongodb']['db']]

    app = init_dash(conf)
    app.run_server()
