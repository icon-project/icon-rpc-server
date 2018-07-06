# Copyright 2017 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import binascii
import unittest
import time
import jsonrpcclient
from secp256k1 import PrivateKey

from tests.helper import validator_v2, validator_v3
from rest.server.json_rpc import JsonError, convert_params, ParamType
from tests.helper.wallet import Wallet, ICX_FACTOR


class TestV2(unittest.TestCase):
    process = None  # rest server
    HOST_V2 = 'http://localhost:9000/api/v2'
    HOST_V3 = 'http://localhost:9000/api/v3'
    ICX_TOTAL_SUPPLY = "0x2961ffa20dd47f5c4700000"

    first_block = None

    god_private_key = PrivateKey(binascii.unhexlify('98dc1847168d72e515c9e2a6639ae8af312a1dde5d19f3fb38ded71141a1e6be'))
    god_wallet = Wallet(god_private_key)

    any_wallets = [Wallet(), Wallet()]
    any_icx = [123, 1.23]
    tx_hashes = []
    tx_origin = []

    @classmethod
    def setUpClass(cls):
        response = jsonrpcclient.request(cls.HOST_V2, 'icx_getLastBlock')
        cls.first_block = response['block']

        cls.god_wallet.to_address = cls.any_wallets[0].address
        cls.god_wallet.value = cls.any_icx[0]
        params = cls.god_wallet.create_icx_origin()

        response = jsonrpcclient.request(cls.HOST_V2, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response['tx_hash'])
        cls.tx_origin.append(params)

        time.sleep(1)  # wait for consensus

        cls.any_wallets[0].to_address = cls.any_wallets[1].address
        cls.any_wallets[0].value = cls.any_icx[1]
        params = cls.any_wallets[0].create_icx_origin()

        response = jsonrpcclient.request(cls.HOST_V2, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response['tx_hash'])
        cls.tx_origin.append(params)

        time.sleep(1)  # wait for consensus

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_transaction_result(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': self.tx_hashes[0]})
        self.assertEqual(response['response']['code'], 0)

        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': self.tx_hashes[1]})
        self.assertEqual(response['response']['code'], 0)

    def test_get_balance(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response['response'], hex(int((self.any_icx[0] - self.any_icx[1]) * ICX_FACTOR)))

        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response['response'], hex(int(self.any_icx[1] * ICX_FACTOR)))

    def test_get_total_supply(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTotalSupply')
        self.assertEqual(response['response'], self.ICX_TOTAL_SUPPLY)

    def test_get_last_block(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getLastBlock')
        validator_v2.validate_block(self, response['block'])

        self.assertEqual(response['block']['height'], self.first_block['height'] + len(self.any_icx))

    def test_get_block_by_height(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHeight', {'height': '2'})
        validator_v2.validate_block(self, response['block'])

    def test_get_block_by_hash(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHash', {'hash': self.first_block['block_hash']})
        validator_v2.validate_block(self, response['block'])

        self.assertDictEqual(response['block'], self.first_block)

    def test_get_transaction_by_address(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionByAddress',
                                         {'address': self.god_wallet.address, 'index': 0})
        tx_hashes = response['response']
        for tx_hash in tx_hashes:
            tx_result_response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': tx_hash})
            self.assertEqual(tx_result_response['response']['code'], 0)

    def test_get_balance_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response, hex(int((123 - 1.23) * ICX_FACTOR)))

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response, hex(int(1.23 * ICX_FACTOR)))

    def test_get_total_supply_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTotalSupply')
        self.assertEqual(response, self.ICX_TOTAL_SUPPLY)

    def test_get_last_block_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getLastBlock')
        validator_v3.validate_block(self, response)

        self.assertEqual(response['height'], self.first_block['height'] + len(self.any_icx))

    def test_get_block_by_height_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHeight', {'height': '0x2'})
        validator_v3.validate_block(self, response, block_height='0x2')

    def test_get_block_by_hash_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHash',
                                         {'hash': f"0x{self.first_block['block_hash']}"})
        validator_v3.validate_block(self, response, block_hash=self.first_block['block_hash'])

        self.assertDictEqual(response, convert_params(self.first_block, ParamType.get_block_response))

    def test_get_transaction_result_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': f'0x{self.tx_hashes[0]}'})
        self.assertEqual(response['status'], '0x1')

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': f'0x{self.tx_hashes[1]}'})
        self.assertEqual(response['status'], '0x1')

    def test_get_transaction_by_hash_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionByHash', {'txHash': f'0x{self.tx_hashes[0]}'})
        validator_v2.validate_origin(self, response, self.tx_origin[0], self.tx_hashes[0])

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionByHash', {'txHash': f'0x{self.tx_hashes[1]}'})
        validator_v2.validate_origin(self, response, self.tx_origin[1], self.tx_hashes[1])
