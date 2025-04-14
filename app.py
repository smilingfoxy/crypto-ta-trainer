# ===============================
# IMPORTS AND DEPENDENCIES
# ===============================
from dash import Dash, dcc, html, Input, Output, callback_context
import plotly.graph_objs as go
import pandas as pd
from datetime import timedelta
import random
import ccxt

# ===============================
# DATA GENERATION AND FETCHING
# ===============================
def generate_dummy_data(start_date, periods, timeframe):
    time_delta = {
        '5m': timedelta(minutes=5),
        '15m': timedelta(minutes=15),
        '30m': timedelta(minutes=30),
        '1h': timedelta(hours=1),
        '4h': timedelta(hours=4),
        '1d': timedelta(days=1)
    }
    times = [start_date + i * time_delta[timeframe] for i in range(periods)]
    
    base_price = 85000
    prices = []
    current_price = base_price
    for i in range(periods):
        change = (random.random() - 0.5) * 200  # Random change between -100 and +100
        current_price += change
        prices.append(current_price)
    
    df = pd.DataFrame({
        'time': times,
        'open': prices,
        'close': [p + (random.random() - 0.5) * 50 for p in prices],
        'high': [p + abs(random.random() * 100) for p in prices],
        'low': [p - abs(random.random() * 100) for p in prices]
    })
    
    return df

def fetch_binance_data(pair='BTC/USDT', timeframe='1h', limit=200):
    try:
        exchange = ccxt.binance()
        
        # Calculate timestamps for 3 years of data
        now = exchange.milliseconds()
        three_years = 3 * 365 * 24 * 60 * 60 * 1000  # 3 years in milliseconds
        start_timestamp = now - three_years
        
        all_ohlcv = []
        current_timestamp = start_timestamp
        
        # Fetch data in chunks to avoid rate limits
        while current_timestamp < now and len(all_ohlcv) < limit:
            chunk = exchange.fetch_ohlcv(
                pair, 
                timeframe=timeframe,
                since=current_timestamp,
                limit=1000
            )
            if not chunk:
                break
                
            all_ohlcv.extend(chunk)
            current_timestamp = chunk[-1][0] + 1
        
        # Take random subset of the historical data
        if len(all_ohlcv) > limit:
            start_idx = random.randint(0, len(all_ohlcv) - limit)
            all_ohlcv = all_ohlcv[start_idx:start_idx + limit]
        
        df = pd.DataFrame(all_ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return generate_dummy_data(pd.to_datetime('2025-04-05 00:00:00'), limit, timeframe)

# ===============================
# DATA PROCESSING
# ===============================
def add_technical_indicators(df):
    # Keeping the function but removing all indicators
    return df

# ===============================
# APP INITIALIZATION
# ===============================
app = Dash(__name__, 
    external_stylesheets=[{
        'href': 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap',
        'rel': 'stylesheet',
    }]
)

server = app.server  # Ensure this line is present

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .Select-control {
                background-color: rgb(25,25,25) !important;
                border-color: rgb(40,40,40) !important;
            }
            .Select-menu-outer {
                background-color: rgb(25,25,25) !important;
                border: 1px solid rgb(40,40,40) !important;
            }
            .Select-option {
                background-color: rgb(25,25,25) !important;
                color: white !important;
            }
            .Select-option:hover {
                background-color: rgb(40,40,40) !important;
            }
            .Select-value-label {
                color: white !important;
            }
            .Select-arrow {
                border-color: white transparent transparent !important;
            }
            .is-open .Select-arrow {
                border-color: transparent transparent white !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ===============================
# CHART CONFIGURATION
# ===============================
config = {
    'scrollZoom': True,
    'displayModeBar': True,
    'modeBarButtonsToAdd': [
        'drawline',
        'drawrect',
        'eraseshape',
        'zoomIn2d',
        'zoomOut2d',
        'autoScale2d',
        'resetScale2d'
    ],
    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],  # Remove box and lasso select
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'chart_image',
        'height': 800,
        'width': 1200,
        'scale': 2
    }
}

# Function to get random training segment
def get_random_training_segment(df, segment_size=100):
    if len(df) < segment_size:
        return None, None
    
    max_start = len(df) - segment_size
    start_idx = random.randint(0, max_start)
    end_idx = start_idx + segment_size
    
    full_segment = df.iloc[start_idx:end_idx].copy()
    training_data = full_segment.iloc[:50].copy()  # First 50 candles
    future_data = full_segment.iloc[50:].copy()    # Next 50 candles
    return training_data, future_data

# Generate initial data
data = fetch_binance_data(limit=1000)
data = add_technical_indicators(data)
training_data, revealed_data = get_random_training_segment(data)

# App layout - update the buttons section
# Update the app layout styling
# App layout - update the buttons section
app.layout = html.Div([
    html.Div([
        html.H1("Crypto TA Trainer", style={
            'margin': '2px', 
            'fontSize': '24px',
            'color': '#00ff99',
            'fontFamily': 'Arial, sans-serif',
            'fontWeight': 'bold'
        }),
        html.Div([
            dcc.Dropdown(
                id='pair-dropdown',
                options=[
                    {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                    {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                    {'label': 'XRP/USDT', 'value': 'XRP/USDT'},
                    {'label': 'BNB/USDT', 'value': 'BNB/USDT'},
                    {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                    {'label': 'ADA/USDT', 'value': 'ADA/USDT'},
                    {'label': 'DOGE/USDT', 'value': 'DOGE/USDT'},
                    {'label': 'DOT/USDT', 'value': 'DOT/USDT'},
                    {'label': 'MATIC/USDT', 'value': 'MATIC/USDT'}
                ],
                value='BTC/USDT',
                style={
                    'width': '150px',
                    'margin': '2px',
                    'backgroundColor': 'rgb(25,25,25)',
                    'color': 'white'
                }
            ),
            dcc.Dropdown(
                id='timeframe-dropdown',
                options=[
                    {'label': '5 Minutes', 'value': '5m'},
                    {'label': '15 Minutes', 'value': '15m'},
                    {'label': '30 Minutes', 'value': '30m'},
                    {'label': '1 Hour', 'value': '1h'},
                    {'label': '4 Hours', 'value': '4h'},
                    {'label': '1 Day', 'value': '1d'}
                ],
                value='1h',
                style={
                    'width': '150px',
                    'margin': '2px',
                    'backgroundColor': 'rgb(25,25,25)',
                    'color': 'white'
                }
            ),
            html.Button('New Chart', id='reset-button', n_clicks=0, 
                style={
                    'margin': '2px',
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'border': 'none',
                    'padding': '5px 15px',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }
            ),
            html.Button('⬆️ Up', id='up-button', n_clicks=0, 
                style={
                    'margin': '2px',
                    'backgroundColor': '#27ae60',
                    'color': 'white',
                    'border': 'none',
                    'padding': '5px 15px',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }
            ),
            html.Button('⬇️ Down', id='down-button', n_clicks=0, 
                style={
                    'margin': '2px',
                    'backgroundColor': '#c0392b',
                    'color': 'white',
                    'border': 'none',
                    'padding': '5px 15px',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }
            ),
            html.Div(id='mode-text', style={
                'margin': '2px',
                'color': '#3498db',
                'fontWeight': 'bold'
            }),
            html.Div(id='prediction-result', style={
                'margin': '2px',
                'color': 'white',
                'fontWeight': 'bold'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'height': '40px',
            'gap': '15px',
            'backgroundColor': 'rgb(20,20,20)',
            'padding': '0 20px',
            'borderRadius': '10px'
        }),
    ], style={
        'marginBottom': '0px',
        'height': '60px',
        'padding': '10px 20px',
        'backgroundColor': 'rgb(15,15,15)',
        'borderBottom': '1px solid rgb(40,40,40)'
    }),
    dcc.Graph(
        id='candlestick-graph',
        config=config,
        style={'height': 'calc(100vh - 60px)', 'marginTop': '0px'}
    )
], style={
    'width': '100%',
    'height': '100vh',
    'overflow': 'hidden',
    'display': 'flex',
    'flexDirection': 'column',
    'backgroundColor': 'rgb(15,15,15)'
})

# Update the chart layout settings
@app.callback(
    [Output('candlestick-graph', 'figure'),
     Output('mode-text', 'children'),
     Output('prediction-result', 'children')],
    [Input('reset-button', 'n_clicks'),
     Input('up-button', 'n_clicks'),
     Input('down-button', 'n_clicks'),
     Input('pair-dropdown', 'value'),
     Input('timeframe-dropdown', 'value')]
)
def update_graph(reset_clicks, up_clicks, down_clicks, pair, timeframe):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    prediction_result = ""
    mode = "Training Mode"
    
    try:
        global training_data, revealed_data
        fig = go.Figure()

        # Auto-refresh on pair or timeframe change
        if button_id in ['pair-dropdown', 'timeframe-dropdown', 'reset-button']:
            new_data = fetch_binance_data(pair=pair, timeframe=timeframe, limit=1000)
            new_data = add_technical_indicators(new_data)
            training_data, revealed_data = get_random_training_segment(new_data)
            mode = 'Training Mode (First 50 Candles)'
        
        # Add training data
        fig.add_trace(go.Candlestick(
            x=training_data['time'],
            open=training_data['open'],
            high=training_data['high'],
            low=training_data['low'],
            close=training_data['close'],
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350',
            name='Training',
            increasing_fillcolor='rgba(38, 166, 154, 0.8)',
            decreasing_fillcolor='rgba(239, 83, 80, 0.8)',
            line=dict(width=1),
            whiskerwidth=0,
        ))

        # Handle prediction buttons
        if button_id in ['up-button', 'down-button']:
            mode = 'Prediction Revealed'
            prediction = 'UP' if button_id == 'up-button' else 'DOWN'
            
            # Add future data with different color
            fig.add_trace(go.Candlestick(
                x=revealed_data['time'],
                open=revealed_data['open'],
                high=revealed_data['high'],
                low=revealed_data['low'],
                close=revealed_data['close'],
                increasing_line_color='rgba(38, 166, 154, 0.5)',
                decreasing_line_color='rgba(239, 83, 80, 0.5)',
                name='Future',
                increasing_fillcolor='rgba(38, 166, 154, 0.3)',
                decreasing_fillcolor='rgba(239, 83, 80, 0.3)',
                line=dict(width=1),
                whiskerwidth=0,
            ))
            
            # Calculate if prediction was correct
            first_future_close = revealed_data.iloc[0]['close']
            last_future_close = revealed_data.iloc[-1]['close']
            actual_direction = 'UP' if last_future_close > first_future_close else 'DOWN'
            
            if prediction == actual_direction:
                prediction_result = "✅ Correct Prediction!"
            else:
                prediction_result = "❌ Wrong Prediction!"

        # Move fig.update_layout inside the try block with correct indentation
        fig.update_layout(
            title=dict(
                text=f"Crypto Chart ({pair}) - {mode}",
                font=dict(size=20, color='#00ff99'),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            height=None,
            template="plotly_dark",
            dragmode='pan',
            xaxis=dict(
                tickformat="%Y-%m-%d %H:%M",
                rangeslider=dict(visible=False),
                type='date',
                gridcolor='rgba(128,128,128,0.1)',
                fixedrange=False,
                scaleanchor=None,
                constrain=None,
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                showline=True,
                showgrid=True,
                title=dict(font=dict(color='#3498db'))
            ),
            yaxis=dict(
                fixedrange=False,
                scaleanchor=None,
                constrain=None,
                autorange=True,
                type='linear',
                gridcolor='rgba(128,128,128,0.1)',
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                showline=True,
                showgrid=True,
                side='right',
                title=dict(font=dict(color='#3498db'))
            ),
            plot_bgcolor='rgb(15,15,15)',
            paper_bgcolor='rgb(15,15,15)',
            margin=dict(t=30, b=10, r=20, l=20),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1,
                font=dict(color='#ffffff')
            ),
            hovermode='x unified'
        )
        # Add RR tools functionality
        if button_id == 'candlestick-graph' and click_data:
            point = click_data['points'][0]
            x = point['x']
            y = point['y']
            
            if 'Long RR' in ctx.triggered[0]['prop_id']:
                fig.add_shape(type='line', x0=x, x1=x, y0=y*0.99, y1=y*1.01, 
                            line=dict(color='blue', width=2))
                fig.add_shape(type='line', x0=x, x1=x, y0=y*0.98, y1=y, 
                            line=dict(color='red', width=2))
                fig.add_shape(type='line', x0=x, x1=x, y0=y, y1=y*1.02, 
                            line=dict(color='green', width=2))
                fig.add_annotation(text='Long RR', x=x, y=y, showarrow=True)
            elif 'Short RR' in ctx.triggered[0]['prop_id']:
                fig.add_shape(type='line', x0=x, x1=x, y0=y*0.99, y1=y*1.01, 
                            line=dict(color='blue', width=2))
                fig.add_shape(type='line', x0=x, x1=x, y0=y, y1=y*1.02, 
                            line=dict(color='red', width=2))
                fig.add_shape(type='line', x0=x, x1=x, y0=y*0.98, y1=y, 
                            line=dict(color='green', width=2))
                fig.add_annotation(text='Short RR', x=x, y=y, showarrow=True)

        return fig, f"Mode: {mode}", prediction_result
    except Exception as e:
        return go.Figure(), f"Error: {str(e)}", ""

# ===============================
# APP ENTRY POINT
# ===============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)