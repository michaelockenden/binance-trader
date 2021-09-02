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

trade_buy = []
trade_sell = []

count = 0

# TODO: create backtesting folder and start separating logic
# TODO: create risk manager/holdings manager, that can be used on backtesting and live trading
# TODO: make it so not all equity is used on every order
# TODO: add another asset (e.g. ETH)

with open("data/Bitstamp_BTCUSD_2021_minute.csv", 'r') as file:
    reader = csv.DictReader(file)

    for line in reader:

        count += 1
        if count % 60 != 0:
            continue

        price = float(line['close'])
        prices.append(price)

        if initial_price is None:
            initial_price = price

        if equity:
            current_equity = equity[-1]
        else:
            current_equity = START

        if len(prices) > 200:
            del prices[0]

        increase = (price - initial_price) / initial_price + 1
        price_movement.append(START * increase)

        date = datetime.fromtimestamp(int(line['unix']))
        dates.append(date)

        action = analyse(prices)

        if action:

            if action == BUY and not in_position:
                in_position = True
                current_equity -= current_equity * TRADE_FEE
                buy_at = price
                saved_equity = current_equity

                trade_buy.append((date, current_equity))

            elif action == SELL and in_position:
                in_position = False
                current_equity -= current_equity * TRADE_FEE
                increase = (price - buy_at) / buy_at + 1
                current_equity = saved_equity * increase

                trade_sell.append((date, current_equity))

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

plt.scatter(*(zip(*trade_buy)), marker='v', c='red')
plt.scatter(*(zip(*trade_sell)), marker='v', c='green')

plt.show()
