import unittest
from RequestHandler import RequestHandler


class TestingForRequestHandler(unittest.TestCase):
    def testing(self):
        request_handler = RequestHandler('Testing.log', 'Testing.db')

        self.assertEqual(request_handler._preheader(5), b'\x00\x05')
        self.assertEqual(request_handler._preheader(55), b'\x00\x37')
        self.assertEqual(request_handler._preheader(5555), b'\x15\xb3')


if __name__ == '__main__':
    unittest.main()
