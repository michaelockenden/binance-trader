import logging

from dotenv import dotenv_values
from pprint import pprint

from manager import RealManager

# TODO: Add debug mode
# TODO: Add backtesting suite
# TODO: Add indicators displaying profit
# TODO: Increase or decrease quantity depending on how certain the trade is

debug_flag = True


def set_env():
    """Returns personal API key and Secret key from a .env file."""

    env = dotenv_values(".env")

    if debug_flag:
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

    assets = ["ETH", "BTC"]

    # manager = RealManager(assets, *set_env())
    # pprint(manager.balance)

    # manager = RealManager(assets, *set_env())
    # loop = asyncio.get_event_loop()
    # manager._loop = loop
    # print(loop.run_until_complete(manager.balance))

    manager = RealManager(assets, *set_env())
    manager.run()
