import unittest
import os
from datetime import datetime
from datetime import timedelta
from Message import Message

class TestingForMessage(unittest.TestCase):
    def testing(self):
        os.remove('Testing.db')
        message = Message('Testing.db')
        t1 = datetime.utcnow()
        t2 = t1 - timedelta(hours=1)
        timeless = t1 + timedelta(days=365)
        msg1={'to': 'alice', 'from': 'bob', 'msg': 'hello', 'sent': t1.isoformat()}
        msg2={'to': 'bob', 'from': 'alice', 'msg': 'bye bye', 'sent': t2.isoformat()}

        # Insert 1st item
        message.insert('alice', 'bob','hello', t1)
        messages = message.get_message('alice')
        self.assertEqual(messages,[msg1])

        # Insert 2rd item
        message.insert('bob', 'alice','bye bye', t2)
        messages = message.get_message('bob')
        self.assertEqual(messages, [msg2])

        # None messages
        messages = message.get_message('alice', timeless)
        self.assertEqual(messages, [])

if __name__ == '__main__':
    unittest.main()