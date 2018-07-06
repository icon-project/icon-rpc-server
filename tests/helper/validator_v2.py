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

import jsonrpcclient


def validate_block(self, block, block_hash=None, block_height=None):
    self.assertIn('version', block)

    if block['height'] != 0:
        int(block['prev_block_hash'], 16)
        self.assertEqual(64, len(block['prev_block_hash']))

    int(block['merkle_tree_root_hash'], 16)
    self.assertEqual(64, len(block['merkle_tree_root_hash']))

    int(block['block_hash'], 16)
    self.assertEqual(64, len(block['block_hash']))
    if block_hash:
        self.assertEqual(block['block_hash'], block_hash)

    self.assertIsInstance(block['time_stamp'], int)
    self.assertIsInstance(block['height'], int)

    if block_height:
        self.assertEqual(block['height'], block_height)

    self.assertIn('peer_id', block)
    self.assertIn('signature', block)

    self.assertIn('confirmed_transaction_list', block)


def validate_origin(self, tx_result, origin, tx_hash):
    block_height = int(tx_result['blockHeight'], 16)
    response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHeight', {'height': str(block_height)})
    validate_block(self, response['block'])

    txs = response['block']['confirmed_transaction_list']
    tx_index = int(tx_result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['tx_hash'], tx_hash.replace('0x', ''))

    response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHash',
                                     {'hash': tx_result['blockHash'].replace('0x', '')})
    validate_block(self, response['block'])

    txs = response['block']['confirmed_transaction_list']
    tx_index = int(tx_result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['tx_hash'], tx_hash.replace('0x', ''))

    tx_result.pop('txIndex')
    tx_result.pop('blockHeight')
    tx_result.pop('blockHash')
    tx_result.pop('method')
    self.assertDictEqual(tx_result, origin)
