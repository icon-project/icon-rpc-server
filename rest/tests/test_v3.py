import binascii
import socket
import unittest
import subprocess
import time
import jsonrpcclient
from contextlib import closing
from secp256k1 import PrivateKey

from .wallet import Wallet, ICX_FACTOR


class TestV3(unittest.TestCase):
    process = None  # rest server
    host = 'http://localhost:9000/api/v3'
    first_block = None

    god_private_key = PrivateKey(binascii.unhexlify('98dc1847168d72e515c9e2a6639ae8af312a1dde5d19f3fb38ded71141a1e6be'))
    god_wallet = Wallet(god_private_key)

    any_wallets = [Wallet(), Wallet()]
    any_icx = [123, 1.23]
    tx_hashes = []

    @classmethod
    def setUpClass(cls):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(('localhost', 9000)) != 0:
                cls.process = subprocess.Popen(['python', '-m', 'loopchain_rest', '-o', 'conf/rest_conf.json'])
                time.sleep(3)

        response = jsonrpcclient.request(cls.host, 'icx_getLastBlock')
        cls.first_block = response

        cls.god_wallet.to_address = cls.any_wallets[0].address
        cls.god_wallet.value = cls.any_icx[0]
        params = cls.god_wallet.create_icx_origin_v3()

        response = jsonrpcclient.request(cls.host, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)

        time.sleep(1)  # wait for consensus

        cls.any_wallets[0].to_address = cls.any_wallets[1].address
        cls.any_wallets[0].value = cls.any_icx[1]
        params = cls.any_wallets[0].create_icx_origin_v3()

        response = jsonrpcclient.request(cls.host, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)

        time.sleep(1)  # wait for consensus

    @classmethod
    def tearDownClass(cls):
        if cls.process:
            cls.process.kill()

    def test_get_balance(self):
        response = jsonrpcclient.request(self.host, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response, hex(int((123 - 1.23) * ICX_FACTOR)))

        response = jsonrpcclient.request(self.host, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response, hex(int(1.23 * ICX_FACTOR)))

    def test_get_total_supply(self):
        response = jsonrpcclient.request(self.host, 'icx_getTotalSupply')
        self.assertEqual(response, '0x2961ffa20dd47f5c4700000')

    def test_get_last_block(self):
        response = jsonrpcclient.request(self.host, 'icx_getLastBlock')
        self.validate_block(response)

        self.assertEqual(int(response['height'], 16), int(self.first_block['height'], 16) + len(self.any_icx))

    def test_get_block_by_height(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHeight', {'height': '0x02'})
        self.validate_block(response)

    def test_get_block_by_hash(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': self.first_block['block_hash']})
        self.validate_block(response)

        self.assertDictEqual(response, self.first_block)

    def validate_block(self, block):
        self.assertIn('version', block)

        int(block['prev_block_hash'], 16)
        self.assertEqual(len(block['prev_block_hash']), 66)

        int(block['merkle_tree_root_hash'], 16)
        self.assertEqual(len(block['merkle_tree_root_hash']), 66)

        int(block['block_hash'], 16)
        self.assertEqual(len(block['block_hash']), 66)

        int(block['height'], 16)

        self.assertIn('peer_id', block)
        self.assertIn('signature', block)

        int(block['time_stamp'], 16)



