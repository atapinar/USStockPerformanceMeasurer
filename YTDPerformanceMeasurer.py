import sys
print("Python executable being used:", sys.executable)

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz

def get_stock_data(symbol, start_date, end_date):
    try:
        stock = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if stock.empty:
            print(f"No data found for symbol: {symbol}\n")
            return None
        stock['Log_Ret'] = np.log(stock['Close'] / stock['Close'].shift(1))
        stock['Volatility'] = stock['Log_Ret'].rolling(window=30).std() * np.sqrt(252)
        return stock
    except Exception as e:
        print(f"An error occurred while fetching data for {symbol}: {e}\n")
        return None

def calculate_1yr_percentage(stock_data, symbol):
    try:
        stock_data = stock_data.sort_index()
        end_date = stock_data.index[-1]
        start_date = end_date - timedelta(days=365)
        if stock_data.index.tz is None:
            y1_start = pd.Timestamp(start_date).tz_localize('UTC')
            y1_end = pd.Timestamp(end_date).tz_localize('UTC')
        else:
            y1_start = pd.Timestamp(start_date).tz_convert('UTC')
            y1_end = pd.Timestamp(end_date).tz_convert('UTC')
        y1_data = stock_data[(stock_data.index >= y1_start) & (stock_data.index <= y1_end)]
        if y1_data.empty:
            print(f"No trading data available for the last 1 year for {symbol}.\n")
            return None
        y1_start_close = y1_data['Close'].iloc[0]
        y1_end_close = y1_data['Close'].iloc[-1]
        if isinstance(y1_start_close, pd.Series):
            y1_start_close = y1_start_close.iloc[0]
        if isinstance(y1_end_close, pd.Series):
            y1_end_close = y1_end_close.iloc[0]
        y1_percentage = ((y1_end_close - y1_start_close) / y1_start_close) * 100
        print(f"1-Year Start Close for {symbol}: {y1_start_close}")
        print(f"1-Year End Close for {symbol}: {y1_end_close}")
        print(f"1-Year Percentage Change for {symbol}: {y1_percentage:.2f}%\n")
        return float(y1_percentage)
    except Exception as e:
        print(f"An error occurred while calculating 1-Year percentage change for {symbol}: {e}\n")
        return None

user_input = input("Enter US stock symbols separated by commas (e.g., AAPL, MSFT, AMZN): ")
stock_symbols = [symbol.strip().upper() for symbol in user_input.split(',')]

end_date = datetime.now()
start_date = end_date - timedelta(days=365)
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

print(f"\nFetching data from {start_date_str} to {end_date_str}...\n")

stock_data = {}
for symbol in stock_symbols:
    print(f"Fetching data for {symbol}...")
    data = get_stock_data(symbol, start_date_str, end_date_str)
    if data is not None:
        print(f"Data fetched for {symbol}.\n")
        stock_data[symbol] = data
    else:
        print(f"Skipping {symbol} due to data retrieval issues.\n")

additional_tickers = {
    'Bitcoin': 'BTC-USD',
    'Gold': 'GC=F'
}

additional_data = {}
for name, ticker in additional_tickers.items():
    print(f"Fetching data for {name} ({ticker})...")
    data = get_stock_data(ticker, start_date_str, end_date_str)
    if data is not None:
        print(f"Data fetched for {name}.\n")
        additional_data[name] = data
    else:
        print(f"Skipping {name} due to data retrieval issues.\n")

y1_percentages = {}
for name, data in additional_data.items():
    y1_percentage = calculate_1yr_percentage(data, name)
    if y1_percentage is not None:
        y1_percentages[name] = y1_percentage

for symbol in stock_data.keys():
    y1_percentage = calculate_1yr_percentage(stock_data[symbol], symbol)
    if y1_percentage is not None:
        y1_percentages[symbol] = y1_percentage

if y1_percentages:
    try:
        plt.figure(figsize=(10, 6))
        names = list(y1_percentages.keys())
        percentages = list(y1_percentages.values())
        
        colors = []
        for name in names:
            if name == 'Bitcoin':
                colors.append('#f7931a')
            elif name == 'Gold':
                colors.append('#d4af37')
            else:
                colors.append('#1f77b4')
        
        bars = plt.bar(names, percentages, color=colors)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, height, f'{height:.2f}%', ha='center', va='bottom')
        
        plt.title('1-Year Percentage Change: Bitcoin, Gold, and Input Stocks')
        plt.xlabel('Asset')
        plt.ylabel('1-Year Percentage Change (%)')
        plt.ylim(min(percentages) - 10, max(percentages) + 10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"An error occurred while plotting 1-Year Percentage Changes: {e}\n")
