import json
from abc import ABC, abstractmethod

import numpy
import talib
import websockets
import time

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


class Watcher(ABC):
    """
    Responsible for watching symbol candles and deciding when to order.
    """

    def __init__(self, symbol):
        self.base = symbol
        self.quote = "USDT"
        self.SYMBOL = self.base + "/" + self.quote

        self._ws = None
        self._loop = None

        self._closes = []
        self._bought = False

        self.SOCKET = f"wss://stream.binance.com:9443/ws/{symbol.lower()}usdt@kline_1m"

    async def listen(self, loop):
        self._ws = await websockets.connect(self.SOCKET, ping_interval=None)
        self._loop = loop

        async for message in self._ws:
            if await self._receive(message):
                yield True

    async def _receive(self, message):
        kline = json.loads(message)['k']

        if kline['x']:
            # 'x' being True indicates the candle has closed

            print(time.ctime(time.time()), kline)
            self._closes.append(float(kline['c']))

            if len(self._closes) > RSI_PERIOD:
                np_closes = numpy.array(self._closes)
                rsi = talib.RSI(np_closes, RSI_PERIOD)
                print(rsi)
                return await self._check(rsi[-1])

    async def _check(self, rsi):
        # TODO: Use enum or constants for buy and sell sides

        if rsi > RSI_OVERBOUGHT:
            if self._bought:
                print("==SELL==")
                return "sell"

        elif rsi < RSI_OVERSOLD:
            if not self._bought:
                print("==BUY==")
                return "buy"
