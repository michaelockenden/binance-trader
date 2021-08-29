import csv
from datetime import datetime

import matplotlib.pyplot as plt
import numpy

from strategy import BUY, SELL
from strategy import analyse

START = 100
TRADE_FEE = 0.00075
initial_price = None

prices = []
price_movement = []
dates = []

equity = []
in_position = False


with open("data/Bitfinex_BTCUSD_minute.csv", 'r') as file:
    reader = csv.DictReader(file)

    for line in reader:
        price = float(line['close'])
        prices.append(price)

        if initial_price is None:
            initial_price = price

        if equity:
            current_equity = equity[-1]
        else:
            current_equity = START

        if len(prices) > 100:
            del prices[0]

        increase = (price - initial_price) / initial_price + 1
        price_movement.append(START * increase)

        unix = int(line['unix']) / 1000
        dates.append(datetime.fromtimestamp(unix))

        action = analyse(prices)

        if action:

            if action == BUY and not in_position:
                in_position = True
                current_equity -= current_equity * TRADE_FEE
                buy_at = price
                saved_equity = current_equity

            elif action == SELL and in_position:
                in_position = False
                current_equity -= current_equity * TRADE_FEE
                increase = (price - buy_at) / buy_at + 1
                current_equity = saved_equity * increase

        elif in_position:
            increase = (price - buy_at) / buy_at + 1
            current_equity = saved_equity * increase

        equity.append(current_equity)

x = numpy.array(dates)
y1 = numpy.array(equity)
y2 = numpy.array(price_movement)
plt.plot(x, y1, label="Equity")
plt.plot(x, y2, label="Buy and Hold")
plt.legend()
plt.show()
