from parse_csv import parse
from graph import plot
from strategy import BUY, SELL
from strategy import analyse

START = 100
TRADE_FEE = 0.00075
initial_price = None

prices = []
price_movement = []
dates = []

equity = []
in_position = 0

trade_buy = []
trade_sell = []

# TODO: create backtesting folder and start separating logic
# TODO: create risk manager/holdings manager, that can be used on backtesting and live trading
# TODO: make it so not all equity is used on every order
# TODO: add another asset (e.g. ETH)

if __name__ == "__main__":
    df = parse()

    count = 0
    for line in df.itertuples():

        # TODO: replace this with DataFrame.resample()
        count += 1
        if count % 15 != 0:
            continue

        price = line.close
        prices.append(price)

        if len(prices) > 200:
            del prices[0]

        if initial_price is None:
            initial_price = price

        if equity:
            current_equity = equity[-1]
        else:
            current_equity = START

        increase = (price - initial_price) / initial_price + 1
        price_movement.append(START * increase)

        date = line.Index
        dates.append(date)

        action = analyse(prices)

        if action:

            if action == BUY and not in_position:
                in_position = 1
                current_equity -= current_equity * TRADE_FEE
                buy_at = price
                saved_equity = current_equity

                trade_buy.append((date, current_equity))

            elif action == SELL and in_position:
                in_position = 0
                current_equity -= current_equity * TRADE_FEE
                increase = (price - buy_at) / buy_at + 1
                current_equity = saved_equity * increase

                trade_sell.append((date, current_equity))

        if in_position:
            increase = in_position * (price - buy_at) / buy_at + 1
            current_equity = saved_equity * increase

        equity.append(current_equity)

    plot(dates, equity, price_movement, trade_buy, trade_sell)
