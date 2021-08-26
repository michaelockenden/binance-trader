import asyncio
import logging

import ccxt
import ccxt.async_support as a_ccxt

from strategy import BUY, SELL
from watcher import Watcher

QUOTE_PRICE = 15


class Manager:
    """
    Manages account holdings, multiple Watcher classes and performs buy/sell orders.
    """

    def __init__(self, bases):
        self.bases = bases
        self.watchers = []

        self._loop = asyncio.get_event_loop()

        for base in bases:
            watcher = Watcher(base)
            self.watchers.append(watcher)

    def run(self):
        self._loop.run_until_complete(self._gather())

    async def _gather(self):
        """Gathers multiple watchers to run together"""

        tasks = []
        for watcher in self.watchers:
            tasks.append(self._watch(watcher))

        await asyncio.gather(*tasks)

    async def _watch(self, watcher):
        """Uses a generator to continuously return values from a watcher"""
        # TODO: separate the quantity logic from the generator
        async for side in watcher.listen():
            quantity = QUOTE_PRICE / watcher.price
            quantity = await self._check_position(side, watcher.base, quantity)
            if quantity:
                await self._order(side, watcher.symbol, quantity)


class RealManager(Manager):

    def __init__(self, bases, api, secret):

        super().__init__(bases)

        self.api_key = api
        self.secret_key = secret

    def run(self):
        if self.validate_balance():
            self._loop.run_until_complete(self._gather())

    def validate_balance(self):
        if self.balance >= QUOTE_PRICE * len(self.bases):
            return True
        else:
            print("Insufficient balance")
            return False

    async def _check_position(self, side, base, quantity):

        if side == BUY:
            if self.balance >= QUOTE_PRICE:
                return quantity

        elif side == SELL:
            if self.holding(base) >= quantity:
                if self.holding(base) < 2*quantity:
                    return self.holding(base)
                else:
                    return quantity

        else:
            return None

    async def _order(self, side, symbol, quantity):
        exchange = a_ccxt.binance({
            'asyncio_loop': self._loop,
            'enableRateLimit': True,
            'apiKey': self.api_key,
            'secret': self.secret_key,
            # 'verbose': True
        })
        exchange.set_sandbox_mode(True)
        try:
            order_type = 'market'
            order = await exchange.create_order(
                symbol, order_type, side, quantity, price=None, params={'type': 'spot'}
            )
            logging.debug(order)
            summary = f"{side}: {order['amount']} {symbol} at {order['price']}"
            logging.warning(summary)
            return True
        except ccxt.InsufficientFunds as e:
            print('create_order() failed – not enough funds')
            logging.warning(e)
            return False
        except Exception as e:
            print('create_order() failed')
            logging.warning(e)
            return False
        finally:
            await exchange.close()

    def holding(self, asset):
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'apiKey': self.api_key,
            'secret': self.secret_key,
            # 'verbose': True
        })
        exchange.set_sandbox_mode(True)
        balance = exchange.fetch_balance()
        return balance[asset]['free']

    @property
    def balance(self):
        return self.holding('USDT')
