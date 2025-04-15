import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Pairs and timeframes to download
pairs = [
    'BTC-USD', 'ETH-USD', 'XRP-USD', 'BNB-USD', 
    'SOL-USD', 'ADA-USD', 'DOGE-USD', 'DOT-USD', 'MATIC-USD'
]

# We'll only use 5m timeframe
timeframe = '5m'
period = '60d'  # Maximum allowed for 5m intervals

# Create data directory if it doesn't exist
import os
os.makedirs('d:/your_project/data', exist_ok=True)

for symbol in pairs:
    print(f"Downloading {symbol} data...")
    
    # Download data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=timeframe)
    
    # Format data
    df = df[['Open', 'High', 'Low', 'Close']]
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close'
    })
    
    # Reset index to make datetime a column
    df = df.reset_index()
    df = df.rename(columns={'Datetime': 'time', 'Date': 'time'})
    
    # Save to CSV
    filename = f"d:/your_project/data/{symbol.replace('-', '_')}_5m.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {filename}")

print("Download complete!")