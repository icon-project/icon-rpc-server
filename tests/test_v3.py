import binascii
import unittest
import time
import jsonrpcclient
from secp256k1 import PrivateKey

from tests.helper import validator_v3
from tests.helper.wallet import Wallet, ICX_FACTOR


class TestV3(unittest.TestCase):
    host = 'http://localhost:9000/api/v3'
    first_block = None

    god_private_key = PrivateKey(binascii.unhexlify('98dc1847168d72e515c9e2a6639ae8af312a1dde5d19f3fb38ded71141a1e6be'))
    god_wallet = Wallet(god_private_key)

    any_wallets = [Wallet(), Wallet()]
    any_icx = [123, 1.23]
    tx_hashes = []
    tx_origin = []

    @classmethod
    def setUpClass(cls):
        response = jsonrpcclient.request(cls.host, 'icx_getLastBlock')
        cls.first_block = response

        cls.god_wallet.to_address = cls.any_wallets[0].address
        cls.god_wallet.value = cls.any_icx[0]
        params = cls.god_wallet.create_icx_origin_v3()

        response = jsonrpcclient.request(cls.host, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)
        cls.tx_origin.append(params)

        time.sleep(1)  # wait for consensus

        cls.any_wallets[0].to_address = cls.any_wallets[1].address
        cls.any_wallets[0].value = cls.any_icx[1]
        params = cls.any_wallets[0].create_icx_origin_v3()

        response = jsonrpcclient.request(cls.host, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)
        cls.tx_origin.append(params)

        time.sleep(1)  # wait for consensus

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_balance(self):
        response = jsonrpcclient.request(self.host, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response, hex(int((123 - 1.23) * ICX_FACTOR)))

        response = jsonrpcclient.request(self.host, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response, hex(int(1.23 * ICX_FACTOR)))

    def test_get_total_supply(self):
        response = jsonrpcclient.request(self.host, 'icx_getTotalSupply')
        self.assertEqual(response, '0x296f3bc3cac14e365700000')

    def test_get_last_block(self):
        response = jsonrpcclient.request(self.host, 'icx_getLastBlock')
        validator_v3.validate_block(self, response)

        self.assertEqual(int(response['height'], 16), int(self.first_block['height'], 16) + len(self.any_icx))

    def test_get_block_by_height(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHeight', {'height': '0x2'})
        validator_v3.validate_block(self, response, block_height='0x2')

    def test_get_block_by_hash(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': self.first_block['block_hash']})
        validator_v3.validate_block(self, response, block_hash=self.first_block['block_hash'])

        self.assertDictEqual(response, self.first_block)

    def test_get_transaction_result(self):
        response = jsonrpcclient.request(self.host, 'icx_getTransactionResult', {'txHash': self.tx_hashes[0]})
        validator_v3.validate_receipt(self, response, self.tx_hashes[0])

        response = jsonrpcclient.request(self.host, 'icx_getTransactionResult', {'txHash': self.tx_hashes[1]})
        validator_v3.validate_receipt(self, response, self.tx_hashes[1])

    def test_get_transaction_by_hash(self):
        response = jsonrpcclient.request(self.host, 'icx_getTransactionByHash', {'txHash': self.tx_hashes[0]})
        validator_v3.validate_origin(self, response, self.tx_origin[0], self.tx_hashes[0])

        response = jsonrpcclient.request(self.host, 'icx_getTransactionByHash', {'txHash': self.tx_hashes[1]})
        validator_v3.validate_origin(self, response, self.tx_origin[1], self.tx_hashes[1])
