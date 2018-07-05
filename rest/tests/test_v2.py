import socket
import unittest
import subprocess
import time
import jsonrpcclient
from contextlib import closing


from .wallet import Wallet


class TestV3(unittest.TestCase):
    process = None  # rest server

    god_private_key = '98dc1847168d72e515c9e2a6639ae8af312a1dde5d19f3fb38ded71141a1e6be'
    god_wallet = Wallet(god_private_key)

    any_wallet = Wallet()

    @classmethod
    def setUpClass(cls):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(('localhost', 9000)) != 0:
                cls.process = subprocess.Popen(['python', '-m', 'loopchain_rest'])

        cls.god_wallet.to_address = cls.any_wallet.address
        cls.god_wallet.create_icx_origin()

        time.sleep(3)  # wait for consensus

    @classmethod
    def tearDownClass(cls):
        if cls.process:
            cls.process.terminate()

    def test_get_transaction_result(self):
        pass

    def test_get_balance(self):
        pass

    def test_get_last_block(self):
        pass

    def test_get_block_by_hash(self):
        pass

    def test_get_block_by_height(self):
        pass

    def test_get_transaction_by_address(self):
        pass

    def test_get_total_supply(self):
        pass
