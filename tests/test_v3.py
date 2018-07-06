import binascii
import unittest
import jsonrpcclient
import jsonrpcclient.exceptions
from time import sleep
from secp256k1 import PrivateKey

from rest.server.json_rpc import GenericJsonRpcServerError, JsonError, convert_params, ParamType
from tests.helper import validator_v3, validator_v2
from tests.helper.wallet import Wallet, ICX_FACTOR


class TestV3(unittest.TestCase):
    HOST_V2 = 'http://localhost:9000/api/v2'
    HOST_V3 = 'http://localhost:9000/api/v3'
    ICX_TOTAL_SUPPLY = "0x296f3bc3cac14e365700000"

    first_block = None

    god_private_key = PrivateKey(binascii.unhexlify('98dc1847168d72e515c9e2a6639ae8af312a1dde5d19f3fb38ded71141a1e6be'))
    score_owner_private_key = PrivateKey(binascii.unhexlify('a0a1c51d2deeba854ca25aab72e465d701e0f47fb97e2110dc5157d752ab154a'))
    god_wallet = Wallet(god_private_key)
    score_owner = Wallet(score_owner_private_key)

    any_wallets = [Wallet(), Wallet()]
    any_icx = [123, 1.23]
    tx_hashes = []
    tx_origin = []

    @classmethod
    def setUpClass(cls):
        response = jsonrpcclient.request(cls.HOST_V3, 'icx_getLastBlock')
        cls.first_block = response

        cls.god_wallet.to_address = cls.any_wallets[0].address
        cls.god_wallet.value = cls.any_icx[0]
        params = cls.god_wallet.create_icx_origin_v3()

        response = jsonrpcclient.request(cls.HOST_V3, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)
        cls.tx_origin.append(params)

        sleep(1)  # wait for consensus

        cls.any_wallets[0].to_address = cls.any_wallets[1].address
        cls.any_wallets[0].value = cls.any_icx[1]
        params = cls.any_wallets[0].create_icx_origin_v3()

        response = jsonrpcclient.request(cls.HOST_V3, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)
        cls.tx_origin.append(params)

        sleep(1)  # wait for consensus

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_balance_success(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response, hex(int((123 - 1.23) * ICX_FACTOR)))

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response, hex(int(1.23 * ICX_FACTOR)))

    def test_get_balance_fail_invalid_address(self):
        try:
            response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": "INVALID_ADDRESS"})
        except GenericJsonRpcServerError as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)

    def test_get_total_supply(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTotalSupply')
        self.assertEqual(response, self.ICX_TOTAL_SUPPLY)

    def test_get_last_block(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getLastBlock')
        validator_v3.validate_block(self, response)

        self.assertEqual(int(response['height'], 16), int(self.first_block['height'], 16) + len(self.any_icx))

    def test_get_block_by_height(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHeight', {'height': '0x2'})
        validator_v3.validate_block(self, response, block_height='0x2')

    def test_get_block_by_hash(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHash', {'hash': self.first_block['block_hash']})
        validator_v3.validate_block(self, response, block_hash=self.first_block['block_hash'])

        self.assertDictEqual(response, self.first_block)

    def test_get_transaction_result(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': self.tx_hashes[0]})
        validator_v3.validate_receipt(self, response, self.tx_hashes[0])

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': self.tx_hashes[1]})
        validator_v3.validate_receipt(self, response, self.tx_hashes[1])

    def test_get_transaction_by_hash(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionByHash', {'txHash': self.tx_hashes[0]})
        validator_v3.validate_origin(self, response, self.tx_origin[0], self.tx_hashes[0])

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionByHash', {'txHash': self.tx_hashes[1]})
        validator_v3.validate_origin(self, response, self.tx_origin[1], self.tx_hashes[1])

    def test_deploy_score(self):
        params = self.score_owner.deploy_score_v3('sample_token')
        response = jsonrpcclient.request(self.HOST_V3, 'icx_sendTransaction', params)
        print(response)

    def test_get_balance_v2(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response, hex(int((123 - 1.23) * ICX_FACTOR)))

        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response, hex(int(1.23 * ICX_FACTOR)))

    def test_get_total_supply_v2(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTotalSupply')
        self.assertEqual(response, self.ICX_TOTAL_SUPPLY)

    def test_get_last_block_v2(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getLastBlock')
        block = response['block']
        validator_v2.validate_block(self, block)

        self.assertEqual(block['height'], int(self.first_block['height'], 16) + len(self.any_icx))

    def test_get_block_by_height_v2(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHeight', {'height': '2'})
        block = response['block']
        validator_v2.validate_block(self, block)

    def test_get_block_by_hash_v2(self):
        block_hash = self.first_block['block_hash'].replace('0x', '')
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHash', {'hash': block_hash})
        block = response['block']
        validator_v2.validate_block(self, block)

        self.assertNotEqual(block['block_hash'], self.first_block['block_hash'])
        self.assertDictEqual(convert_params(block, ParamType.get_block_response), self.first_block)

    def test_get_transaction_result_v2(self):
        tx_hash = self.tx_hashes[0].replace('0x', '')
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': tx_hash})
        self.assertEquals(response['response']['code'], 0)

        tx_hash = self.tx_hashes[1].replace('0x', '')
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': tx_hash})
        self.assertEquals(response['response']['code'], 0)
