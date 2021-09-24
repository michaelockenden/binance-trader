import matplotlib.pyplot as plt


def plot(x, y1, y2, trade_buy, trade_sell):
    plt.plot(x, y1, label="Equity")
    plt.plot(x, y2, label="Buy and Hold")
    plt.legend()

    try:
        plt.scatter(*(zip(*trade_buy)), marker='v', c='red')
        plt.scatter(*(zip(*trade_sell)), marker='v', c='green')
    except TypeError:
        pass

    plt.show()
