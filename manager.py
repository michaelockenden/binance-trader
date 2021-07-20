import asyncio
import logging

import ccxt.async_support as ccxt

from watcher import Watcher


class Manager:
    """
    Manages account holdings, multiple Watcher classes and performs buy/sell orders.
    """

    def __init__(self, symbols):
        self.usdt = 1000
        self.symbols = symbols
        self.watchers = []

        self.loop = None

        for symbol in symbols:
            watcher = Watcher(symbol)
            self.watchers.append(watcher)

    async def run(self, loop):
        self.loop = loop
        tasks = []
        for watcher in self.watchers:
            tasks.append(self._watch(watcher))

        await asyncio.gather(*tasks)

    async def _watch(self, watcher):
        async for side in watcher.listen(self.loop):
            quantity = self.symbols[watcher.base]
            await self._order(side, watcher.SYMBOL, quantity)

    async def _order(self, side, symbol, quantity):
        exchange = ccxt.binance({'asyncio_loop': self.loop})
        try:
            price = await exchange.fetch_ticker(symbol)
            price = price['close']
            order = f"{side} - {symbol} at {price}"

            if side == "buy":
                self.usdt -= quantity * price

            if side == "sell":
                self.usdt += quantity * price
                running_profit = self.usdt - 100
                order += f"| usdt: {self.usdt} | total profit: {running_profit}%"

            logging.warning(order)
            return True

        except Exception as e:
            logging.warning(e)
            return False

        finally:
            await exchange.close()
