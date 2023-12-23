import datetime
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import apimoex
from mt5_funcs import get_symbol_names, TIMEFRAMES, dict_timeframes, INDICATORS
# import ta.trend as ta
import pandas_ta as ta


# creates the Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
server = app.server

symbol_dropdown = html.Div([
    html.P('Symbol:'),
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': symbol, 'value': symbol} for symbol in get_symbol_names()],
        value='SBER',
        searchable=True,
        clearable=True
    )
])


timeframe_dropdown = html.Div([
    html.P('Timeframe:'),
    dbc.Select(
        id='timeframe-dropdown',
        options=[{'label': timeframe, 'value': timeframe} for timeframe in TIMEFRAMES],
        value='D1'
    )
])

indicator_dropdown = html.Div([
    html.P('Indicators:'),
    dbc.Select(
        id='indicator-dropdown',
        options=[{'label': indicator, 'value': indicator} for indicator in INDICATORS],
        value='CLEAR'
    )
])




num_bars_input = html.Div([
    html.P('Number of Candles:'),
    dbc.Input(id='num-bar-input', type='number', value='50')
], className='my-dropdown')

# creates the layout of the App
app.layout = html.Div(children=[
    html.H1('Real Time Charts'),

    dbc.Row([
        dbc.Col(symbol_dropdown),
        dbc.Col(timeframe_dropdown),
        dbc.Col(num_bars_input),
        dbc.Col(indicator_dropdown)
    ]),

    html.Hr(),

    dcc.Interval(id='update', interval=3000),

    html.Div(id='page-content')

], style={'margin-left': '7%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(
    Output('page-content', 'children'),
    Input('update', 'n_intervals'),
    State('symbol-dropdown', 'value'), State('timeframe-dropdown', 'value'), State('num-bar-input', 'value'), State('indicator-dropdown', 'value')
)
def update_ohlc_chart(interval, symbol, timeframe, num_bars, indicator):
    timeframe_str = timeframe
    timeframe = dict_timeframes[timeframe]
    num_bars = int(num_bars)
    print(symbol, timeframe, num_bars, timeframe)
    from_ = (datetime.datetime.now() - datetime.timedelta(weeks=300)).strftime("%Y-%m-%d")
    till = datetime.datetime.now().strftime("%Y-%m-%d")
    query = f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{symbol}/candles.csv?iss.meta=on&iss.reverse=true&from={from_}&till={till}&interval={timeframe}'
    df = pd.read_csv(query, sep=';', header=1)
    if indicator != "CLEAR":
        indicator = indicator.lower()
        df[indicator] = getattr(ta, indicator)(close = df.close, length=10)
    df = df.head(num_bars)
    df['end'] = pd.to_datetime(df['end'])

    fig = go.Figure(data=go.Candlestick(x=df['end'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']))
                    # template = "plotly_dark",
                    # title="Gapminder 2007: '%s' theme" % "plotly_dark"))
    if indicator != "CLEAR":
        fig.add_scatter(x=df['end'], y=df[indicator], mode='lines', line=dict(color='white'), name=indicator.upper())

    fig.update_layout(xaxis_rangeslider_visible=False)

    fig.update_layout(plot_bgcolor = "rgba(0,0,0,0.2)", paper_bgcolor='rgba(0,0,0,0.2)',margin_l = 0, margin_t = 40)
    fig.update_layout(width=1150, height= 700)
    fig.update_xaxes(showgrid=False, gridwidth=0.001, gridcolor='rgba(95,98,171,0)', mirror=True, ticks='outside', showline=True)
    fig.update_yaxes(showgrid=True, gridwidth=0.1, gridcolor='gray', mirror=True, ticks='outside', showline=True)
    fig.update_layout(yaxis={'side': 'right'})


    return [
        html.H2(id='chart-details', children=f'{symbol} - {timeframe_str}'),
        dcc.Graph(figure=fig, config={'displaylogo': False, 'modeBarButtonsToAdd': ['drawline',
                                        'drawopenpath',
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]})
        ]



if __name__ == '__main__':
    app.run_server()
