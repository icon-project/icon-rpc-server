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
import re


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

    if block_height is not None:
        self.assertEqual(block['height'], block_height)

    self.assertIn('peer_id', block)
    self.assertIn('signature', block)

    self.assertIn('confirmed_transaction_list', block)


def validate_receipt(self, receipt, tx_hash):
    int(receipt['txHash'], 16)
    self.assertEqual(receipt['txHash'], tx_hash)
    self.assertEqual(66, len(receipt['txHash']))

    int(receipt['txIndex'], 16)
    int(receipt['blockHeight'], 16)
    int(receipt['blockHash'], 16)
    self.assertEqual(66, len(receipt['blockHash']))

    int(receipt['cumulativeStepUsed'], 16)
    int(receipt['stepUsed'], 16)

    response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHeight', {'height': receipt['blockHeight']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    self.assertEqual(txs[int(receipt['txIndex'], 16)]['txHash'], tx_hash)

    response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHash', {'hash': receipt['blockHash']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    self.assertEqual(txs[int(receipt['txIndex'], 16)]['txHash'], tx_hash)


def validate_origin(self, result, origin, tx_hash):
    response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHeight', {'height': result['blockHeight']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['txHash'], tx_hash)

    response = jsonrpcclient.request(self.HOST_V3, 'icx_getBlockByHash', {'hash': result['blockHash']})
    validate_block(self, response)

    txs = response['confirmed_transaction_list']
    tx_index = int(result['txIndex'], 16)
    self.assertEqual(txs[tx_index]['txHash'], tx_hash)

    result.pop('txIndex')
    result.pop('blockHeight')
    result.pop('blockHash')
    self.assertDictEqual(result, origin)


def validate_score_address(address: str) -> bool:
    """Check whether address is in icon address format or not

    :param address: (str) address string including prefix
    :return: (bool)
    """
    try:
        if isinstance(address, str) and len(address) == 42:
            prefix, body = _split_icon_address(address)
            if prefix == 'hx' or prefix == 'cx':
                return _is_lowercase_hex_string(body)
    finally:
        pass

    return False


def _split_icon_address(address: str) -> (str, str):
    """Split icon address into 2-char prefix and 40-char address body

    :param address: 42-char address string
    :return: prefix, body
    """
    return address[:2], address[2:]


def _is_lowercase_hex_string(value: str) -> bool:
    """Check whether value is hexadecimal format or not

    :param value: text
    :return: True(lowercase hexadecimal) otherwise False
    """

    try:
        result = re.match('[0-9a-f]+', value)
        return len(result.group(0)) == len(value)
    except:
        pass

    return False