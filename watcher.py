import json
import logging

import numpy
import talib
import websockets
import ccxt.async_support as ccxt

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_QUANTITY = 0.005


class Watcher:

    def __init__(self, symbol, api, secret):
        self.SYMBOL = symbol
        self.API_KEY = api
        self.SECRET_KEY = secret
        self._ws = None
        self._loop = None
        self._closes = []
        self._bought = False

        self.SOCKET = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@kline_1m"

    async def listen(self, loop):
        self._ws = await websockets.connect(self.SOCKET, ping_interval=None)
        self._loop = loop

        async for message in self._ws:
            await self._receive(message)

    async def _receive(self, message):
        kline = json.loads(message)['k']
        if kline['x'] or True:
            print(kline)
            self._closes.append(float(kline['c']))

            if len(self._closes) > RSI_PERIOD:
                np_closes = numpy.array(self._closes)
                rsi = talib.RSI(np_closes, RSI_PERIOD)
                print(rsi)
                return await self._check(rsi[-1])

    async def _check(self, rsi):
        if rsi > RSI_OVERBOUGHT:
            if self._bought:
                print("==SELL==")
                if await self._order("sell"):
                    self._bought = False
                    return True
                else:
                    return False

        elif rsi < RSI_OVERSOLD or True:
            if not self._bought:
                print("==BUY==")
                if await self._order("buy"):
                    self._bought = True
                    return True
                else:
                    return False

    async def _order(self, side):
        exchange = ccxt.binance({
            'asyncio_loop': self._loop,
            'enableRateLimit': True,
            'apiKey': self.API_KEY,
            'secret': self.SECRET_KEY,
            # 'verbose': True
        })
        try:
            type = 'limit'  # or market
            side = 'buy'
            order = await exchange.create_order(self.SYMBOL, type, side, TRADE_QUANTITY, {
                'type': 'spot',
            })
            print(order)
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
