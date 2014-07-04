#!/usr/bin/python3.4
"""
TODO:
- connection timeout
"""
import asyncio

import websockets
import logging

PORT = 7778

logging.basicConfig(filename='caster.log',
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    datefmt='%y-%m-%d:%H:%M:%S')


@asyncio.coroutine
def handler(proto, uri):
    logging.info("CONNECTED TO", uri)
    while proto.open:
        message = yield from proto.recv()
        logging.debug("MSG RECEIVED:" + message)

    logging.info("DISCONNECTED", uri)


asyncio.get_event_loop().run_until_complete(websockets.serve(handler, 'localhost', PORT))
asyncio.get_event_loop().run_forever()


