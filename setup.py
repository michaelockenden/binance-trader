import asyncio
import logging

from dotenv import dotenv_values

from manager import Manager, RealManager

from pprint import pprint


# TODO: Add minimum quantity/account balance validator
# TODO: Automatically adjust bought/sold indicator based on current holdings
# TODO: Find a way to change RSI thresholds without rerunning the program
# TODO: Add indicators displaying profit
# TODO: Increase or decrease quantity depending on how certain the trade is


def set_env(test=True):
    """Returns personal API key and Secret key from a .env file."""

    env = dotenv_values(".env")

    if test:
        api = env["API_KEY_TEST"]
        secret = env["SECRET_KEY_TEST"]
    else:
        api = env["API_KEY"]
        secret = env["SECRET_KEY"]

    return api, secret


if __name__ == "__main__":
    logging.basicConfig(filename="orders.log",
                        filemode='a',
                        format="%(asctime)s | %(levelname)s | %(message)s",
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    assets = {"ETH": 0.005, "ADA": 10, "ALGO": 15, "BTC": 0.00001}

    # manager = RealManager(assets, *set_env())
    # pprint(manager.balance)

    # manager = RealManager(assets, *set_env())
    # loop = asyncio.get_event_loop()
    # manager._loop = loop
    # print(loop.run_until_complete(manager.balance))

    manager = Manager(assets)
    manager.run()
