import asyncio
import logging

from binance.client import Client
from dotenv import load_dotenv, dotenv_values
from watcher import Watcher


def set_env():
    load_dotenv()
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

    client = Client(*set_env(), testnet=True)
    watcher = Watcher("ETHUSDT", *set_env())
    asyncio.run(watcher.listen())
