import asyncio
import logging

from pprint import pprint
from dotenv import dotenv_values
from trader import PaperTrader


# TODO: Add minimum quantity/account balance validator
# TODO: Automatically adjust bought/sold indicator based on current holdings
# TODO: Find a way to change RSI thresholds without rerunning the program
# TODO: Add indicators displaying profit
# TODO: Increase or decrease quantity depending on how certain the trade is


def set_env():
    """Returns personal API key and Secret key from a .env file."""

    env = dotenv_values(".env")

    api = env["API_KEY"]
    secret = env["SECRET_KEY"]

    return api, secret


async def start(loop):
    """Creates a watcher for each symbol and runs them at once."""

    symbols = [("ETH", 0.005), ("ADA", 10), ("ALGO", 10), ("BTC", 0.00001)]
    tasks = []
    api, secret = set_env()

    for symbol in symbols:
        trader = PaperTrader(*symbol)
        tasks.append(trader.listen(loop))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    logging.basicConfig(filename="orders.log",
                        filemode='a',
                        format="%(asctime)s | %(levelname)s | %(message)s",
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    asyncio_loop = asyncio.get_event_loop()
    asyncio_loop.run_until_complete(start(asyncio_loop))
