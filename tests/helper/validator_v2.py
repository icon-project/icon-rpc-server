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
        self.assertEqual(len(block['prev_block_hash']), 64)

    int(block['merkle_tree_root_hash'], 16)
    self.assertEqual(len(block['merkle_tree_root_hash']), 64)

    self.assertIsInstance(block['time_stamp'], int)
    self.assertIsInstance(block['height'], int)

    int(block['block_hash'], 16)
    self.assertEqual(len(block['block_hash']), 64)
    if block_hash:
        self.assertEqual(block['block_hash'], block_hash)

    if block_height:
        self.assertEqual(block['height'], block_height)

    self.assertIn('peer_id', block)
    self.assertIn('signature', block)

    self.assertIn('confirmed_transaction_list', block)


def validate_origin(self, result, origin, tx_hash):
    response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHeight', {'height': result['block']['block_height']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['tx_hash'], tx_hash)

    response = jsonrpcclient.request(self.HOST_V2, 'icx_getBlockByHash', {'hash': result['block']['block_hash']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['tx_hash'], tx_hash)

    result.pop('txIndex')
    result.pop('blockHeight')
    result.pop('blockHash')
    self.assertDictEqual(result, origin)
