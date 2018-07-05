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
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(receipt['txIndex'], 16)
    self.assertEqual(txs[tx_index]['txHash'], tx_hash)

    # TODO
    # response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': receipt['blockHash']})
    # validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(receipt['txIndex'], 16)
    self.assertEqual(txs[tx_index]['txHash'], tx_hash)


def validate_origin(self, result, origin, tx_hash):
    response = jsonrpcclient.request(self.host, 'icx_getBlockByHeight', {'height': result['blockHeight']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['txHash'], tx_hash)

    response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': result['blockHash']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['txHash'], tx_hash)

    result.pop('txIndex')
    result.pop('blockHeight')
    result.pop('blockHash')
    result.pop('txHash')
    self.assertDictEqual(result, origin)
