import logging

import ccxt.async_support as ccxt

from watcher import Watcher


class Trader(Watcher):
    """
    Handles buying and selling logic, using the Binance API to create orders.
    """

    def __init__(
        self,
        symbol,
        quantity,
        api,
        secret
    ):
        super(Trader, self).__init__(symbol)

        self.QUANTITY = quantity
        self.API_KEY = api
        self.SECRET_KEY = secret

    async def _order(self, side):
        exchange = ccxt.binance({
            'asyncio_loop': self._loop,
            'enableRateLimit': True,
            'apiKey': self.API_KEY,
            'secret': self.SECRET_KEY,
            # 'verbose': True
        })
        try:
            order_type = 'market'
            order = await exchange.create_order(self.SYMBOL, order_type, side, self.QUANTITY, None, {
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


class PaperTrader(Watcher):
    """
    Records orders but doesn't execute them.
    """

    def __init__(
        self,
        symbol,
        quantity
    ):
        super(PaperTrader, self).__init__(symbol)

        self.QUANTITY = quantity

    async def _order(self, side):
        exchange = ccxt.binance({'asyncio_loop': self._loop})
        try:
            price = await exchange.fetch_ticker(self.SYMBOL)
            price = price['close']
            order = f"{side} - {self.SYMBOL} at {price}"
            logging.warning(order)
            return True
        except Exception as e:
            logging.warning(e)
            return False
        finally:
            await exchange.close()
