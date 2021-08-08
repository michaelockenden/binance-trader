import asyncio
import logging

import ccxt.async_support as a_ccxt
import ccxt

from watcher import Watcher
from strategy import BUY, SELL


class Manager:
    """
    Manages account holdings, multiple Watcher classes and performs buy/sell orders.
    """

    def __init__(self, bases):
        self.usdt = 100
        self.holdings = dict()

        self.bases = bases
        self.watchers = []

        self._loop = asyncio.get_event_loop()

        for base in bases:
            watcher = Watcher(base)
            self.watchers.append(watcher)

            self.holdings[base] = 0

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

        async for side in watcher.listen():
            quantity = await self._check_position(side, watcher.base)
            if quantity:
                await self._order(side, watcher.symbol, quantity)

    async def _check_position(self, side, base):
        quantity = self.bases[base]
        if side == BUY:
            if self.usdt >= 20:
                return quantity

        elif side == SELL:
            if self.holdings[base] >= quantity:
                return quantity

        return None

    async def _order(self, side, symbol, quantity):
        exchange = a_ccxt.binance({'asyncio_loop': self._loop})
        try:
            price = await exchange.fetch_ticker(symbol)
            price = price['close']
            order = f"{side} - {symbol} at {price}"

            if side == BUY:
                self.usdt -= quantity * price
                self.holdings[symbol.split("/")[0]] += quantity

            if side == SELL:
                self.usdt += quantity * price
                self.holdings[symbol.split("/")[0]] -= quantity
                running_profit = self.usdt - 100
                order += f"| usdt: {self.usdt} | total profit: {running_profit}%"

            logging.warning(order)
            return True

        except Exception as e:
            logging.warning(e)
            return False

        finally:
            await exchange.close()


class RealManager(Manager):

    def __init__(self, bases, api, secret):

        super().__init__(bases)

        self.api_key = api
        self.secret_key = secret

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
            order = await exchange.create_order(symbol, order_type, side, quantity, None, {
                'type': 'spot',
            })
            print(order)
            logging.warning(order)
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

    @property
    def balance(self):
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'apiKey': self.api_key,
            'secret': self.secret_key,
            # 'verbose': True
        })
        exchange.set_sandbox_mode(True)
        balance = exchange.fetch_balance()
        return balance['USDT']['free']
