import asyncio
import logging

from dotenv import dotenv_values
from watcher import Watcher


def set_env():
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

    watcher = Watcher("ETHUSDT", *set_env())

    asyncio_loop = asyncio.get_event_loop()
    asyncio_loop.run_until_complete(watcher.listen(asyncio_loop))
