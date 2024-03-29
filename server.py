import asyncio
import logging
import names
from random import randint

from websockets import (
    WebSocketServerProtocol, 
    serve, 
    WebSocketProtocolError
    )
from exchange import fetch_currency_rates


class ChatServer:
    
    clients = set()
    
    async def register(self, ws: WebSocketServerProtocol):
        # ws.name = randint(1, 100)
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')
    
    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')
    
    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]
        
    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except WebSocketProtocolError as err:
            logging.error(err)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if str(message).startswith("exchange"):
                _, days, *currency = str(message).split()
                # print(days, currency)
                rates = await fetch_currency_rates(int(days), currency)
                # print(rates)
                await self.send_to_clients(f"exchange: {rates}")
            else: 
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    chat_server = ChatServer()
    async with serve(chat_server.ws_handler, 'localhost', 7070):
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
