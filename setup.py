import asyncio
import logging

from dotenv import dotenv_values

from manager import Manager


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


if __name__ == "__main__":
    logging.basicConfig(filename="orders.log",
                        filemode='a',
                        format="%(asctime)s | %(levelname)s | %(message)s",
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    symbols = {"ETH": 0.005, "ADA": 10, "ALGO": 15, "BTC": 0.00001}
    manager = Manager(symbols)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(manager.run(loop))
