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

from tests.wallet import Wallet, ICX_FACTOR


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
        self.validate_block(response)

        self.assertEqual(int(response['height'], 16), int(self.first_block['height'], 16) + len(self.any_icx))

    def test_get_block_by_height(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHeight', {'height': '0x2'})
        self.validate_block(response, block_height='0x2')

    def test_get_block_by_hash(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': self.first_block['block_hash']})
        self.validate_block(response, block_hash=self.first_block['block_hash'])

        self.assertDictEqual(response, self.first_block)

    def test_get_transaction_result(self):
        response = jsonrpcclient.request(self.host, 'icx_getTransactionResult', {'txHash': self.tx_hashes[0]})
        self.validate_receipt(response, self.tx_hashes[0])

        response = jsonrpcclient.request(self.host, 'icx_getTransactionResult', {'txHash': self.tx_hashes[1]})
        self.validate_receipt(response, self.tx_hashes[1])

    def test_get_transaction_by_hash(self):
        response = jsonrpcclient.request(self.host, 'icx_getTransactionByHash', {'txHash': self.tx_hashes[0]})
        self.validate_origin(response, self.tx_origin[0], self.tx_hashes[0])

        response = jsonrpcclient.request(self.host, 'icx_getTransactionByHash', {'txHash': self.tx_hashes[1]})
        self.validate_origin(response, self.tx_origin[1], self.tx_hashes[1])

    def validate_block(self, block, block_hash=None, block_height=None):
        self.assertIn('version', block)

        int(block['prev_block_hash'], 16)
        self.assertEqual(len(block['prev_block_hash']), 66)

        int(block['merkle_tree_root_hash'], 16)
        self.assertEqual(len(block['merkle_tree_root_hash']), 66)

        int(block['block_hash'], 16)
        self.assertEqual(len(block['block_hash']), 66)
        if block_hash:
            self.assertEqual(block['block_hash'], block_hash)

        int(block['height'], 16)
        if block_height:
            self.assertEqual(block['height'], block_height)

        self.assertIn('peer_id', block)
        self.assertIn('signature', block)

        int(block['time_stamp'], 16)

        self.assertIn('confirmed_transaction_list', block)

    def validate_receipt(self, receipt, tx_hash):
        int(receipt['txHash'], 16)
        self.assertEqual(receipt['txHash'], tx_hash)
        self.assertEqual(len(receipt['txHash']), 66)

        int(receipt['txIndex'], 16)
        int(receipt['blockHeight'], 16)
        # TODO
        # int(receipt['blockHash'], 16)
        # self.assertEqual(len(receipt['blockHash']), 66)

        # TODO
        # int(receipt['cumulativeStepUsed'], 16)
        int(receipt['stepUsed'], 16)

        # TODO
        # if receipt['status'] == '0x1':  # success
        #     int(receipt['scoreAddress'], 16)
        # elif receipt['status'] == '0x0':  # fail
        #     self.assertIsNone(receipt['scoreAddress'])
        # else:
        #     raise RuntimeError('Unknown status in receipt')

        response = jsonrpcclient.request(self.host, 'icx_getBlockByHeight', {'height': receipt['blockHeight']})
        self.validate_block(response)

        txs = response['confirmed_transaction_list']

        self.assertEqual(txs[int(receipt['txIndex'], 16)]['txHash'], tx_hash)

        # TODO
        # response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': receipt['blockHash']})
        # self.validate_block(response)

        txs = response['confirmed_transaction_list']
        self.assertEqual(txs[int(receipt['txIndex'], 16)]['txHash'], tx_hash)

    def validate_origin(self, result, origin, tx_hash):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHeight', {'height': result['blockHeight']})
        self.validate_block(response)

        txs = response['confirmed_transaction_list']
        tx_index = int(result['txIndex'], 16)
        self.assertEqual(txs[tx_index]['txHash'], tx_hash)

        response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': result['blockHash']})
        self.validate_block(response)

        txs = response['confirmed_transaction_list']
        tx_index = int(result['txIndex'], 16)
        self.assertEqual(txs[tx_index]['txHash'], tx_hash)

        result.pop('txIndex')
        result.pop('blockHeight')
        result.pop('blockHash')
        # TODO
        # self.assertDictEqual(result, origin)
