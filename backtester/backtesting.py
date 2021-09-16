import pandas as pd
import numpy as np

prices = pd.read_csv("data/Bitstamp_BTCUSD_2021_minute.csv")
prices['ma cross'] = prices['close'].rolling(5).mean() - prices['close'].rolling(20).mean()
prices['position'] = (prices['ma cross'].apply(np.sign) + 1) / 2
print(prices[['close', 'ma cross', 'position']])
