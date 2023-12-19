import datetime
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import apimoex
from mt5_funcs import get_symbol_names, TIMEFRAMES, dict_timeframes

# creates the Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

symbol_dropdown = html.Div([
    html.P('Symbol:'),
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': symbol, 'value': symbol} for symbol in get_symbol_names()],
        value='SBER'
    )
])

timeframe_dropdown = html.Div([
    html.P('Timeframe:'),
    dcc.Dropdown(
        id='timeframe-dropdown',
        options=[{'label': timeframe, 'value': timeframe} for timeframe in TIMEFRAMES],
        value='D1'
    )
])

num_bars_input = html.Div([
    html.P('Number of Candles'),
    dbc.Input(id='num-bar-input', type='number', value='20')
])

# creates the layout of the App
app.layout = html.Div([
    html.H1('Real Time Charts'),

    dbc.Row([
        dbc.Col(symbol_dropdown),
        dbc.Col(timeframe_dropdown),
        dbc.Col(num_bars_input)
    ]),

    html.Hr(),

    dcc.Interval(id='update', interval=3000),

    html.Div(id='page-content')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(
    Output('page-content', 'children'),
    Input('update', 'n_intervals'),
    State('symbol-dropdown', 'value'), State('timeframe-dropdown', 'value'), State('num-bar-input', 'value')
)
def update_ohlc_chart(interval, symbol, timeframe, num_bars):
    timeframe_str = timeframe
    timeframe = dict_timeframes[timeframe]
    num_bars = int(num_bars)
    print(symbol, timeframe, num_bars, timeframe)
    from_ = (datetime.datetime.now() - datetime.timedelta(weeks=100)).strftime("%Y-%m-%d")
    till = datetime.datetime.now().strftime("%Y-%m-%d")
    query = f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{symbol}/candles.csv?iss.meta=on&iss.reverse=true&from={from_}&till={till}&interval={timeframe}'
    df = pd.read_csv(query, sep=';', header=1)
    df = df.head(num_bars)
    df['end'] = pd.to_datetime(df['end'])
    # df['open'] = df['open'].astype(float)
    # df['high'] = df['high'].astype(float)
    # df['low'] = df['low'].astype(float)
    # df['close'] = df['close'].astype(float)
    fig = go.Figure(data=go.Candlestick(x=df['end'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']))

    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(yaxis={'side': 'right'})
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    return [
        html.H2(id='chart-details', children=f'{symbol} - {timeframe_str}'),
        dcc.Graph(figure=fig, config={'displayModeBar': False})
        ]


if __name__ == '__main__':
    app.run_server()
