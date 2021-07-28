#! /usr/bin/env python3

import socket
import selectors
import RequestHandler
import sys

HOST = '127.0.0.1'
PORT = 65432
LOG_FILE_NAME = 'user.log'
DB__FILE_NAME = 'message.db'


class Server:
    def __init__(self, ip, port):
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.bind((ip, port))
        self._listener.listen(10)
        self._listener.settimeout(5)
        self._listener.setblocking(False)
        self._requestHandler = RequestHandler.RequestHandler(
            LOG_FILE_NAME, DB__FILE_NAME)

        self._clients = selectors.DefaultSelector()
        self._clients.register(self._listener, selectors.EVENT_READ, data=None)

        print('Kia ora, Chat Server start listening on ', (HOST, PORT))

        while True:
            try:
                events = self._clients.select(timeout=None)
                for event, mask in events:
                    # new client, accept it
                    if event.data is None:
                        self.on_connect()
                    # old client, receive and process its message
                    else:
                        self.on_message(event, mask)
            except socket.timeout as e:
                print(e.with_traceback())
                break
            except BlockingIOError as e:
                print(e.with_traceback())
            except Exception as e:
                print(e.with_traceback())
                break

    def on_connect(self):
        """
        Accept a new client and register it.
        """
        conn, addr = self._listener.accept()
        conn.setblocking(False)
        data = {'addr': addr, 'buffer': b'', 'send': b''}
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._clients.register(conn, events, data=data)

        print('Connected by ', addr)

    def on_message(self, event, mask):
        """
        When an event occurred, classify it and process.
        if it's read, call the request handler to receive and send the response.
        if it's write, indicatd that this socket can be received, so send buffer to it.
        """
        sock = event.fileobj
        data = event.data
        keep_alive = True

        if mask & selectors.EVENT_READ:
            keep_alive = self._requestHandler.process(sock, data)

        if mask & selectors.EVENT_WRITE:
            if data['send']:
                sent = sock.sendall(data['send'])
            data['send'] = b''

        if not keep_alive:
            self._clients.unregister(sock)
            sock.close()


if __name__ == "__main__":
    try:
        server = Server(HOST, PORT)
    except KeyboardInterrupt:
        sys.exit()
