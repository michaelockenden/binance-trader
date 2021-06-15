import json
import logging
from pprint import pprint

import numpy
import talib
import websockets
from binance import Client
from binance.enums import *

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
        self._closes = []
        self._bought = False

        self.SOCKET = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@kline_1m"
        self._client = Client(api_key=self.API_KEY, api_secret=self.SECRET_KEY)

    async def listen(self):
        self._ws = await websockets.connect(self.SOCKET, ping_interval=None)

        async for message in self._ws:
            await self._receive(message)

    async def _receive(self, message):
        kline = json.loads(message)['k']
        if kline['x']:
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
                if await self._order(SIDE_SELL):
                    self._bought = False
                    return True
                else:
                    return False

        elif rsi < RSI_OVERSOLD:
            if not self._bought:
                print("==BUY==")
                if await self._order(SIDE_BUY):
                    self._bought = True
                    return True
                else:
                    return False

    async def _order(self, side):
        try:
            order = self._client.create_order(
                symbol=self.SYMBOL,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=TRADE_QUANTITY
            )
            logging.warning(order)
        except Exception as e:
            logging.error(e)
            return False

        return True
