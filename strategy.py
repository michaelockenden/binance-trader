import numpy
import talib

RSI_PERIOD = 15
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

EMA_SHORT = 30
EMA_LONG = 120

BUY = 'buy'
SELL = 'sell'


def analyse(closes=None):

    if len(closes) <= EMA_LONG:
        return None

    np_closes = numpy.array(closes)
    rsi = talib.RSI(np_closes, RSI_PERIOD)

    latest_rsi = rsi[-1]

    short_ema = talib.EMA(np_closes, EMA_SHORT)
    long_ema = talib.EMA(np_closes, EMA_LONG)

    cross = (short_ema[-1] - long_ema[-1]) / long_ema[-1] + 1

    if latest_rsi / cross > RSI_OVERBOUGHT:
        return SELL

    elif latest_rsi / cross < RSI_OVERSOLD:
        return BUY

    else:
        return None
