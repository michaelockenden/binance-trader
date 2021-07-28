import numpy
import talib

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

BUY = 'buy'
SELL = 'sell'


def analyse(closes=None):

    if len(closes) <= RSI_PERIOD:
        return None

    np_closes = numpy.array(closes)
    rsi = talib.RSI(np_closes, RSI_PERIOD)
    print(rsi)

    latest_rsi = rsi[-1]

    if latest_rsi > RSI_OVERBOUGHT:
        return BUY

    elif latest_rsi < RSI_OVERSOLD:
        return SELL

    else:
        return None
