#! /usr/bin/env python3

import socket
import struct
import json
from datetime import datetime
from User import User
from Message import Message

MAX_HEADER_SIZE = 2**16 - 1
PREHEADER_SIZE = 2
ISOTIMEFORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class RequestHandler:
    def __init__(self, log_file_name, db_file_name):
        self._user = User(log_file_name)
        self._message = Message(db_file_name)

    def _preheader(self, length) -> bytes:
        if length > MAX_HEADER_SIZE:
            raise ValueError('Header size {length} is out of limitation.')
        return struct.pack('>H', length)

    def _read_sock(self, sock: socket.socket, data: dict):
        """
        Append data to the data/s field 'buffer',
        If remote client exit unnormally,
        ConnectResetError is thrown by recv().
        """
        try:
            recv_data = sock.recv(1024)
            data['buffer'] += recv_data
        except BlockingIOError as e:
            pass

    # Read the specified length of data
    def _read(self, sock: socket.socket, data: dict, length: int):
        while len(data['buffer']) < length:
            self._read_sock(sock, data)
        result = data['buffer'][:length]
        data['buffer'] = data['buffer'][length:]
        return result

    # Receive the preheader and return transformed result
    def _read_preheader(self, sock: socket.socket, data: dict) -> int:
        preheader_bytes = self._read(sock, data, PREHEADER_SIZE)
        return struct.unpack('>H', preheader_bytes)[0]

    def _read_header(self, sock: socket.socket, data: dict, length: int) -> dict:
        """
        Receive header data by sock and the specified length
        Return a JSON formated of header data
        """
        header_bytes = self._read(sock, data, length)
        header_str = header_bytes.decode('utf-8')
        return json.loads(header_str)

    def _read_body(self, sock: socket.socket, data: dict, header: dict) -> dict:
        # Receive the body according to inputed 'Content-length' field in the header JSON
        body_len = header.get('Content-length')
        body_bytes = b''
        body_str = ''
        body = None
        if body_len:
            body_bytes = self._read(sock, data, body_len)
        else:
            raise ValueError('Content-length header missing')

        # Transfor the body string to be utf-8
        body_encoding = header.get('Content-encoding')
        if body_encoding == 'utf-8':
            body_str = body_bytes.decode('utf-8')
        else:
            raise ValueError(f'Unsupported Content-encoding: {body_encoding}')

        # Parse the body string to be a JSON
        body_type = header.get('Content-type')
        if body_type == 'application/json':
            body = json.loads(body_str)
        else:
            raise ValueError(f'Unsupported Content-type: {body_type}')
        return body

    def _send(self, sock, body: dict):
        """
        Send a dict-type body and put the preheader and header in
        """
        body_data = json.dumps(body).encode('utf-8')
        body_len = len(body_data)
        header = {
            "Content-type": "application/json",
            "Content-encoding": "utf-8",
            "Content-length": body_len
        }
        header_data = json.dumps(header).encode('utf-8')
        preheader = self._preheader(len(header_data))
        data = preheader + header_data + body_data
        sock.sendall(data)

    def _send_error(self, sock, action, err_info):
        response = {
            'action': action,
            'result': 'error',
            'errors': [err_info]
        }
        self._send(sock, response)

    def on_login(self, sock, body, data, action):
        params = body['params']
        name = params['name']
        if self._user.is_logged_by_name(name):
            print(name + ' has been logged.')
        if len(name) == 0:
            print('username can not be empty.')

        response = {
            'action': action,
            'result': 'ok',
            'errors': []
        }
        self._send(sock, response)

        self._user.add_user(sock, name)
        self._user.add_log(name, action, True)
        print(name + ' is logged in.')
        print('The number of current online users is ' +
              str(self._user.get_user_num()))

    def on_logout(self, sock, body, data, action):
        response = {
            'action': action,
            'result': 'ok',
            'errors': []
        }
        self._send(sock, response)

        name = self._user.get_name(sock)
        if self._user.is_logged_by_socket(sock):
            self._user.remove_user_by_socket(sock)
            self._user.add_log(name, action, True)
        print(name + ' logged out.')
        print('The number of current online users is: ',
              str(self._user.get_user_num()))

    def on_message(self, sock, body, data, action):
        if self._user.is_logged_by_socket(sock) == False:
            print("You have not been logged.")
        sender = self._user.get_name(sock)

        params = body['params']
        messages = params['messages']

        for message in messages:
            self._message.insert(message['to'], sender, message['msg'])
            print(sender + ' send to ' +
                  message['to'] + ': ' + message['msg'])

        response = {
            'action': action,
            'result': 'ok',
            'errors': []
        }
        self._send(sock, response)
        self._user.add_log(sender, action, True)

    def on_get(self, sock, body, data, action):
        if self._user.is_logged_by_socket(sock) == False:
            print("You have not been logged.")
        receiver = self._user.get_name(sock)

        params = body['params']
        last_read_str = params.get('last_read')
        last_read = None
        if last_read_str is not None:
            last_read = datetime.strptime(last_read_str, ISOTIMEFORMAT)

        messages = self._message.get_message(receiver, last_read)
        print('Found ' + str(len(messages))+' messages to ' + receiver + '.')

        response = {
            'action': action,
            'result': 'ok',
            'messages': messages,
            'errors': []
        }
        self._send(sock, response)
        self._user.add_log(receiver, action, True)

    def process(self, sock, data: dict) -> bool:
        action = 'unknown'
        try:
            header_len = self._read_preheader(sock, data)
            header = self._read_header(sock, data, header_len)
            body = self._read_body(sock, data, header)

            action = body['action']

            if action == 'login':
                self.on_login(sock, body, data, action)
                return True

            if action == 'logout':
                self.on_logout(sock, body, data, action)
                return False

            if action == 'send_messages':
                self.on_message(sock, body, data, action)
                return True

            if action == 'get_messages':
                self.on_get(sock, body, data, action)
                return True

            raise ValueError('Unknown action: ', action)

        except ConnectionResetError as e:
            name = self._user.get_name(sock)
            if self._user.is_logged_by_socket(sock):
                self._user.remove_user_by_socket(sock)
            print(name + 'lost connection.')
            print('The number of current online users is ' +
                  str(self._user.get_user_num()))
            return False
        except (json.JSONDecodeError, ValueError) as e:
            print(e.with_traceback)
            data['buffer'] = b''
            self._send_error(sock, action, str(e))
        return True
