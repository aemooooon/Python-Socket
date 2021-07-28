#! /usr/bin/env python3

import datetime


class User:

    def __init__(self, user_log_filename: str):
        self._filename = user_log_filename
        self._user_socket_by_name = {}
        self._username_by_socket = {}

    def add_user(self, sock, username: str):
        self._user_socket_by_name[username] = sock
        self._username_by_socket[sock] = username

    def remove_user(self, username: str):
        sock = self._user_socket_by_name[username]
        self._username_by_socket.pop(sock)
        self._user_socket_by_name.pop(username)

    def remove_user_by_socket(self, sock):
        name = self._username_by_socket[sock]
        self._user_socket_by_name.pop(name)
        self._username_by_socket.pop(sock)

    def get_user_num(self):
        return len(self._username_by_socket)

    def is_logged_by_name(self, username):
        return self._user_socket_by_name.get(username) is not None

    def is_logged_by_socket(self, sock):
        return self._username_by_socket.get(sock) is not None

    def get_name(self, sock):
        if self.is_logged_by_socket(sock):
            return self._username_by_socket[sock]
        else:
            return str(sock)

    def add_log(self, username, request_type, success):
        f = open(self._filename, 'a')
        now = datetime.datetime.utcnow()
        time_str = now.isoformat()
        s = time_str + ':' + username + ':' + request_type + ':'
        if success:
            s += 'OK'
        else:
            s += 'ERROR'
        f.write(s + '\n')
        f.close()
