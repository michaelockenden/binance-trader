from os import listdir

import pandas as pd


def parse():
    files = ["./data/" + f for f in listdir("./data") if f.endswith('.csv')]
    df = pd.concat(map(pd.read_csv, files))

    df.drop(['date', 'symbol'], axis=1, inplace=True)
    df.apply(pd.to_numeric)
    df['date'] = pd.to_datetime(df['unix'], unit='s')
    df = df.set_index(['date'])
    df.drop('unix', axis=1, inplace=True)

    start = '2017'
    end = '2022'

    mask = (df.index > start) & (df.index < end)
    df = df.loc[mask]

    resample_functions = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }

    df = df.resample('180T').agg(resample_functions)
    df.dropna(inplace=True)
    print(df)

    return df


if __name__ == "__main__":
    parse()
