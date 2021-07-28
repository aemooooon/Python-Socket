#! /usr/bin/env python3

import sqlite3
from datetime import datetime


class Message:
    def __init__(self, db_name):
        self.open(db_name)

        self._create_table()

    def open(self, db_name):
        self._conn = sqlite3.connect(db_name)
        self._cursor = self._conn.cursor()

    def _create_table(self):
        self._cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    receiver CHAR(64) NOT NULL,
                                    sender CHAR(64) NOT NULL,
                                    content TEXT NOT NULL,
                                    time TIMESTAMP NOT NULL);''')

    def insert(self, receiver, sender, content, t: datetime = None):
        if t is None:
            t = datetime.utcnow()
        self._cursor.execute('''INSERT INTO messages (receiver, sender, content, time) VALUES('{}', '{}', '{}', '{}')'''.format(
            receiver, sender, content, t.isoformat()))
        self._conn.commit()

    def get_message(self, receiver, last_read: datetime = None) -> list:
        result = None
        last = []

        if last_read is None:
            result = self._cursor.execute(
                "SELECT * FROM messages WHERE receiver=='{}'".format(receiver))
        else:
            result = self._cursor.execute(
                "SELECT * FROM messages WHERE receiver=='{}' AND time>'{}'".format(receiver, last_read.isoformat()))

        for row in result:
            item = {'to': row[1], 'from': row[2],
                    'msg': row[3], 'sent': row[4]}
            last.append(item)

        return last

    def get_messages(self):
        result = self._cursor.execute("SELECT * FROM messages")
        for row in result:
            print(row)

    def close(self):
        self._conn.commit()
        self._conn.close()
