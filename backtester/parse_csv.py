from datetime import datetime

import pandas as pd


def parse():
    df = pd.read_csv("backtester/data/Bitstamp_BTCUSD_2021_minute.csv")
    df.drop(['date', 'symbol'], axis=1, inplace=True)
    df.apply(pd.to_numeric)
    df['date'] = df['unix'].apply(datetime.fromtimestamp)
    df.drop('unix', axis=1, inplace=True)

    return df
