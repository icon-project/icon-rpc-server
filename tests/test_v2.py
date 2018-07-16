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
from jsonrpcclient.exceptions import ReceivedErrorResponse
from secp256k1 import PrivateKey

from rest.protos.message_code import Response
from rest.server.json_rpc import JsonError, convert_params, ParamType
from tests.helper import validator_v2, validator_v3
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

    def test_get_transaction_result_success(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': self.tx_hashes[0]})
        self.assertEqual(response['response']['code'], 0)

        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': self.tx_hashes[1]})
        self.assertEqual(response['response']['code'], 0)

    def test_get_transaction_result_fail_invalid_tx_hash(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': "INVALID_TXHASH"})
        self.assertEqual(response['response_code'], str(Response.fail_validate_params))

    def test_get_balance_success(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': self.tx_hashes[1]})
        var1 = self.any_icx[0] * ICX_FACTOR
        var2 = self.any_icx[1] * ICX_FACTOR
        fee = int(response['stepPrice'], 16) * int(response['stepUsed'], 16)
        excepted_balance = var1 - var2 - fee

        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response['response'], hex(int(excepted_balance)))
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response['response'], hex(int(self.any_icx[1] * ICX_FACTOR)))

    def test_get_balance_fail_invalid_address(self):
        try:
            response = jsonrpcclient.request(self.HOST_V2, 'icx_getBalance', {"address": "INVALID_ADDRESS"})
        except ReceivedErrorResponse as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)

    def test_get_total_supply(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTotalSupply')
        self.assertEqual(response['response'], self.ICX_TOTAL_SUPPLY)

    def test_get_last_block(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getLastBlock')
        validator_v2.validate_block(self, response['block'])

        self.assertEqual(response['block']['height'], self.first_block['height'] + len(self.tx_origin))

    def test_get_block_by_height_success(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHeight', {'height': str(1)})
        validator_v2.validate_block(self, response['block'])
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHeight', {'height': str(2)})
        validator_v2.validate_block(self, response['block'])

    def test_get_block_by_height_fail_invalid_height(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHeight', {'height': hex(2)})
        self.assertEqual(response['response_code'], Response.fail_validate_params)

    def test_get_block_by_hash_success(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHash', {'hash': self.first_block['block_hash']})
        validator_v2.validate_block(self, response['block'])

        self.assertDictEqual(response['block'], self.first_block)

    def test_get_block_by_hash_fail_invalid_hash(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHash', {'hash': "INVALID_BLOCK_HASH"})
        self.assertEqual(response['response_code'], Response.fail_wrong_block_hash)

    def test_get_transaction_by_address_success(self):
        response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionByAddress',
                                         {'address': self.god_wallet.address, 'index': 0})
        tx_hashes = response['response']
        for tx_hash in tx_hashes:
            tx_result_response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionResult', {'tx_hash': tx_hash})
            self.assertEqual(tx_result_response['response']['code'], 0)

    def test_get_transaction_by_address_fail_invalid_address(self):
        try:
            response = jsonrpcclient.request(self.HOST_V2, 'icx_getTransactionByAddress',
                                             {'address': "INVALID_ADDRESS", 'index': 0})
        except ReceivedErrorResponse as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)

    def test_get_balance_v3_success(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': self.tx_hashes[1]})
        var1 = self.any_icx[0] * ICX_FACTOR
        var2 = self.any_icx[1] * ICX_FACTOR
        fee = int(response['stepPrice'], 16) * int(response['stepUsed'], 16)
        excepted_balance = var1 - var2 - fee

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response, hex(int(excepted_balance)))
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response, hex(int(self.any_icx[1] * ICX_FACTOR)))

    def test_get_balance_v3_fail_invalid_address(self):
        try:
            response = jsonrpcclient.request(self.HOST_V3, 'icx_getBalance', {"address": "INVALID_ADDRESS"})
        except ReceivedErrorResponse as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)

    def test_get_total_supply_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTotalSupply')
        self.assertEqual(response, self.ICX_TOTAL_SUPPLY)

    def test_get_last_block_v3(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getLastBlock')
        validator_v3.validate_block(self, response)

        self.assertEqual(response['height'], self.first_block['height'] + len(self.tx_origin))

    def test_get_block_by_height_v3_success(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHeight', {'height': hex(2)})
        validator_v3.validate_block(self, response, block_height=2)

    def test_get_block_by_height_v3_fail_invalid_height(self):
        try:
            response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHeight', {'height': str(2)})
        except ReceivedErrorResponse as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)

    def test_get_block_by_hash_v3_success(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHash',
                                         {'hash': f"0x{self.first_block['block_hash']}"})
        validator_v3.validate_block(self, response, block_hash=self.first_block['block_hash'])

        self.assertDictEqual(response, convert_params(self.first_block, ParamType.get_block_response))

    def test_get_block_by_hash_v3_fail_invalid_hash(self):
        try:
            response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHash', {'hash': "INVALID_HASH"})
        except ReceivedErrorResponse as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)

    def test_get_transaction_result_v3_success(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': f'0x{self.tx_hashes[0]}'})
        self.assertEqual(response['status'], '0x1')

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': f'0x{self.tx_hashes[1]}'})
        self.assertEqual(response['status'], '0x1')

    def test_get_transaction_result_v3_fail_invalid_hash(self):
        try:
            response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionResult', {'txHash': "INVALID_TX_HASH"})
        except ReceivedErrorResponse as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)

    def test_get_transaction_by_hash_v3_success(self):
        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionByHash', {'txHash': f'0x{self.tx_hashes[0]}'})
        validator_v2.validate_origin(self, response, self.tx_origin[0], self.tx_hashes[0])

        response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionByHash', {'txHash': f'0x{self.tx_hashes[1]}'})
        validator_v2.validate_origin(self, response, self.tx_origin[1], self.tx_hashes[1])

    def test_get_transaction_by_hash_v3_fail_invalid_hash(self):
        try:
            response = jsonrpcclient.request(self.HOST_V3, 'icx_getTransactionByHash', {'txHash': "INVALID_TX_HASH"})
        except ReceivedErrorResponse as e:
            self.assertEqual(e.code, JsonError.INVALID_PARAMS)
