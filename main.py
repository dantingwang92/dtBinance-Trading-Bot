# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 00:15:21 2024

@author: Administrator
chatgpt4o

"""

import pandas as pd
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os

# 設置API密鑰
api_key = 'MmBtw1lNtsxgpwO59JLyOxSwm3TdvKa0vhwJZbuc5ogPfgLeUbgkXyTzZgKz5Oq9'
secret_key = 'NWEhtYcoWs8PlGg99qDHM4vmKJA1jAnM97lxKoD1reEsSPwzjR6l3aNmrnVnKXp8'

# 從環境變數中讀取 API 密鑰
api_key = os.environ.get('API_KEY')
secret_key = os.environ.get('SECRET_KEY')

# 確保 API_KEY 和 API_SECRET_KEY 都存在，否則提醒錯誤
if not api_key or not secret_key:
    raise ValueError("API_KEY and SECRET_KEY must be set as environment variables.")




# 創建Binance客戶端
client = Client(api_key, secret_key)

symbol = 'BTCUSDT'  # 交易對，Binance格式無斜槓
timeframe = Client.KLINE_INTERVAL_5MINUTE  # 5分鐘K線
short_window = 7     # 短期均線窗口
long_window = 25     # 長期均線窗口
position = None      # 當前持倉（'long', 'short', 或者 None）

def fetch_data(symbol, timeframe):
    # 從Binance獲取歷史K線數據
    try:
        klines = client.get_klines(symbol=symbol, interval=timeframe, limit=100)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                           'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                           'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = pd.to_numeric(df['close'])
        return df
    except BinanceAPIException as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_sma(df, window):
    return df['close'].rolling(window=window).mean()

def check_for_signal(df):
    short_sma = calculate_sma(df, short_window)
    long_sma = calculate_sma(df, long_window)

    if short_sma.iloc[-1] > long_sma.iloc[-1] and short_sma.iloc[-2] <= long_sma.iloc[-2]:
        return 'buy'
    elif short_sma.iloc[-1] < long_sma.iloc[-1] and short_sma.iloc[-2] >= long_sma.iloc[-2]:
        return 'sell'
    return None

def place_order(symbol, side, amount):
    try:
        if side == 'buy':
            order = client.order_market_buy(symbol=symbol, quantity=amount)
        elif side == 'sell':
            order = client.order_market_sell(symbol=symbol, quantity=amount)
        print(f"Order placed: {side} {amount} {symbol}")
    except BinanceAPIException as e:
        print(f"An error occurred: {e}")

def main():
    global position
    while True:
        df = fetch_data(symbol, timeframe)
        if df is not None:
            signal = check_for_signal(df)

            if signal == 'buy' and position != 'long':
                print("Buy signal detected")
                place_order(symbol, 'buy', 0.001)  # 假設購買0.001 BTC
                position = 'long'
            elif signal == 'sell' and position != 'short':
                print("Sell signal detected")
                place_order(symbol, 'sell', 0.001)  # 假設賣出0.001 BTC
                position = 'short'

        time.sleep(60)  # 每分鐘檢查一次

if __name__ == "__main__":
    main()




# 查詢交易記錄的範例代碼：
# from binance.client import Client
# import os

# # 設置API密鑰
# api_key = 'MmBtw1lNtsxgpwO59JLyOxSwm3TdvKa0vhwJZbuc5ogPfgLeUbgkXyTzZgKz5Oq9'
# api_secret = 'NWEhtYcoWs8PlGg99qDHM4vmKJA1jAnM97lxKoD1reEsSPwzjR6l3aNmrnVnKXp8'

# # 設置測試網客戶端
# client = Client(api_key, api_secret, testnet=True)

# # 查詢賬戶的交易記錄
# symbol = 'BTCUSDT'

# # 查詢歷史訂單
# orders = client.get_all_orders(symbol=symbol)

# # 打印訂單信息
# for order in orders:
#     print(order)

# # 查詢資金變動（可以查看買賣後的資金情況）
# account_info = client.get_account()
# balances = account_info['balances']
# for balance in balances:
#     print(balance)






