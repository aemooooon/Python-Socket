import unittest
import socket
from User import User

class TestingForUser(unittest.TestCase):
    def testing(self):
        user = User('Testing.log')
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # test after adding 1 user
        user.add_user(sock1, 'user1')
        self.assertEqual(user.get_user_num(), 1)
        self.assertEqual(user.get_name(sock1), 'user1')
        self.assertEqual(user.is_logged_by_socket(sock1), True)
        self.assertEqual(user.is_logged_by_socket(sock2), False)
        self.assertEqual(user.is_logged_by_name('user1'), True)
        self.assertEqual(user.is_logged_by_name('user2'), False)

        # test after adding an another user
        user.add_user(sock2, 'user2')
        self.assertEqual(user.get_user_num(), 2)
        self.assertEqual(user.get_name(sock2), 'user2')
        self.assertEqual(user.is_logged_by_socket(sock1), True)
        self.assertEqual(user.is_logged_by_socket(sock2), True)
        self.assertEqual(user.is_logged_by_name('user1'), True)
        self.assertEqual(user.is_logged_by_name('user2'), True)

        # test after removing users
        user.remove_user('user1')
        self.assertEqual(user.get_user_num(), 1)
        self.assertEqual(user.get_name(sock1), str(sock1))
        self.assertEqual(user.is_logged_by_socket(sock1), False)
        self.assertEqual(user.is_logged_by_socket(sock2), True)
        self.assertEqual(user.is_logged_by_name('user1'), False)
        self.assertEqual(user.is_logged_by_name('user2'), True)

        # removed an another user
        user.remove_user_by_socket(sock2)
        self.assertEqual(user.get_user_num(), 0)
        self.assertEqual(user.get_name(sock2), str(sock2))
        self.assertEqual(user.is_logged_by_socket(sock1), False)
        self.assertEqual(user.is_logged_by_socket(sock2), False)
        self.assertEqual(user.is_logged_by_name('user1'), False)
        self.assertEqual(user.is_logged_by_name('user2'), False)

        sock1.close()
        sock2.close()


if __name__ == '__main__':
    unittest.main()
