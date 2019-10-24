# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import unittest
from typing import Union
from copy import deepcopy

from iconrpcserver.utils.icon_service.converter import convert_params
from iconrpcserver.utils.icon_service import RequestParamType, ResponseParamType


class TestConverter(unittest.TestCase):
    BLOCK_v0_1a = {
        "version": "0.1a",
        "prev_block_hash": "5b7985592ee6da8d2a6e202a170cbc5f2afd3915991924b21e5f1e3f66c62760",
        "merkle_tree_root_hash": "4d50c98a43402b8ed8dd6fa9a66f15f009ebf62ce7c3d0d3512bd8223d163629",
        "time_stamp": 1566541016906709,
        "confirmed_transaction_list": [],
        "block_hash": "10d890fe8254ba8d571b796d81d3ad7124251ef519d23e20d7726892594cff41",
        "height": 7,
        "peer_id": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "signature": "bgBn8XwHe5IMsVR8C/cplrEtWeULY7VHNvlA1Ri8vKFf67lxAMVDGHqPN9zxgo8HotGlAF+Wwrc8rKaYqt+ACQA=",
        "next_leader": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe"
    }
    BLOCK_v0_3 = {
        "version": "0.3",
        "prevHash": "0xecafbdc4fb0311995e9f5f4cd01e82deb3d4016c6276c45e77b66eea053a2b22",
        "transactionsHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "stateHash": "0xa7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a",
        "receiptsHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "repsHash": "0xa0fa1058145d96226fbe31d4987ae43b54fe83a6bed7939dc7c38da1d44f06bc",
        "nextRepsHash": "0xa0fa1058145d96226fbe31d4987ae43b54fe83a6bed7939dc7c38da1d44f06bc",
        "leaderVotesHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "prevVotesHash": "0x51e030a24c5967047f8463c138024f857ec6663535df1f4e76e224f95abbe4b1",
        "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "timestamp": "0x5908392532c01",
        "transactions": [],
        "leaderVotes": [],
        "prevVotes": [
            {
                "rep": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
                "timestamp": "0x590839234a5de",
                "blockHeight": "0x3",
                "blockHash": "0xecafbdc4fb0311995e9f5f4cd01e82deb3d4016c6276c45e77b66eea053a2b22",
                "signature": "9MhqZW4n9CtJXTKfDOiVsvZRuGQh9G3X9g3X3+4V2Fp8PcqGvkKHoAI4nJpAxGiJICiT7kgMqwQmvQ8ndGVXrgE="
            },
            {
                "rep": "hx9f049228bade72bc0a3490061b824f16bbb74589",
                "timestamp": "0x590839235367b",
                "blockHeight": "0x3",
                "blockHash": "0xecafbdc4fb0311995e9f5f4cd01e82deb3d4016c6276c45e77b66eea053a2b22",
                "signature": "e2JNWDnNTulhksibVR2AV0/ZLLPwDfeOdq1A5DE/GAIPI56QR+78nV7I/eNHvFDzL6OcpN7D5/VZ5dfFBszB2QE="
            },
            {
                "rep": "hx6435405122df9fe5187d659588beccdf7aee8557",
                "timestamp": "0x590839235419f",
                "blockHeight": "0x3",
                "blockHash": "0xecafbdc4fb0311995e9f5f4cd01e82deb3d4016c6276c45e77b66eea053a2b22",
                "signature": "mjhQSlSZhYuwLSqu+CbNDsiB4WTn8096RQ2EP89YPAVRita+bDuCBhyUkfZWhDqQPVW//sCwQD2GDXxNCC5dCgA="
            },
            {
                "rep": "hx475bfec4178f3abc88c959faa2e6384e6b409c8f",
                "timestamp": "0x59083923541d1",
                "blockHeight": "0x3",
                "blockHash": "0xecafbdc4fb0311995e9f5f4cd01e82deb3d4016c6276c45e77b66eea053a2b22",
                "signature": "o2OnbkaLK1rvGP+pDwrTo/+VV1Ag2/HuDeUV5aoReOhvmS4rOWLGuV00B5KZmE9GO7ZRHl32Ys0oSrj85ve3uAA="
            }
        ],
        "hash": "0x6d4a4dbb950152050684eef5d0e228b8a31cae7afd37d9760b79312305008977",
        "height": "0x4",
        "leader": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "signature": "OPHFV8Zfyr//lP+SmKsr/RK3yawJDtolrfsdqDFKh3wxmyMh243zVp7CTLRu5wG5PdneX7mHzuLA9x41mqzjrAE=",
        "nextLeader": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe"
    }
    TX_V2 = {
        "from": "hx5a05b58a25a1e5ea0f1d5715e1f655dffc1fb30a",
        "to": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "timestamp": "1566541014562476",
        "value": "0xde0b6b3a7640000",
        "signature": "orj3aiUYwoDvj/vEQSYwdOZ2XNUnHxFdEIWUVBG9FEM0zt2KZWwYu2Rg3c+0qosR1ccPFX2M1ckQ6VHZBqec8AE=",
        "tx_hash": "b6153bf19fd010081bec49d1d4eea7c7e27888fc2d89ff3a1f3cd6d79de22efa",
        "fee": "0x2386f26fc10000",
        "method": "icx_sendTransaction"
    }
    TX_V3 = {
        "version": "0x3",
        "from": "hx5a05b58a25a1e5ea0f1d5715e1f655dffc1fb30a",
        "to": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "stepLimit": "0xf4240",
        "timestamp": "0x590c2c0b2f6ac",
        "nid": "0x3",
        "value": "0xde0b6b3a7640000",
        "signature": "orj3aiUYwoDvj/vEQSYwdOZ2XNUnHxFdEIWUVBG9FEM0zt2KZWwYu2Rg3c+0qosR1ccPFX2M1ckQ6VHZBqec8AE=",
        "txHash": "0xb6153bf19fd010081bec49d1d4eea7c7e27888fc2d89ff3a1f3cd6d79de22efa"
    }

    def setUp(self):
        self.converter = convert_params
        self.block_v0_1a_tx_v2, self.block_v0_1a_tx_v3 = deepcopy(self.BLOCK_v0_1a), deepcopy(self.BLOCK_v0_1a)
        self.block_v0_3_tx_v3 = deepcopy(self.BLOCK_v0_3)
        self.block_v0_1a_tx_v2["confirmed_transaction_list"].append(self.TX_V2)
        self.block_v0_1a_tx_v3["confirmed_transaction_list"].append(self.TX_V3)
        self.block_v0_3_tx_v3["transactions"].append(self.TX_V3)

    def _convert(self, origin_data: dict, param_type: Union[RequestParamType, ResponseParamType]):
        try:
            return self.converter(origin_data, param_type)
        except:
            self.fail(f'error with : {origin_data}')

    def _check_block_key(self, converted_data: dict, comparing_data: dict, is_v3: bool=True):
        # block data check
        assert converted_data.keys() == comparing_data.keys()
        # tx data check
        self._check_tx_key(converted_data, comparing_data, is_v3)

    def _check_tx_key(self, converted_data: dict, comparing_data: dict, is_v3: bool):
        converted_tx = self._get_tx_from_block_data(converted_data, is_v3)
        comparing_tx = self._get_tx_from_block_data(comparing_data, is_v3)
        assert converted_tx.keys() == comparing_tx.keys()

    def _get_tx_from_block_data(self, block_data, is_v3=True) -> dict:
        if block_data["version"] == "0.1a" or not is_v3:
            return block_data["confirmed_transaction_list"][0]
        else:
            return block_data["transactions"][0]

    def test_convert_get_block_response_v2(self):
        converted_data = self._convert(self.block_v0_1a_tx_v3, ResponseParamType.get_block_v0_1a_tx_v2)
        for tx in converted_data["confirmed_transaction_list"]:
            tx["fee"] = "0x2386f26fc10000"  # additional parameters from loopchain
        self._check_block_key(converted_data, self.block_v0_1a_tx_v2, is_v3=False)

        block_v0_3_converted = self._convert(self.block_v0_3_tx_v3, ResponseParamType.get_block_v0_1a_tx_v2)
        for tx in block_v0_3_converted["confirmed_transaction_list"]:
            tx["fee"] = "0x2386f26fc10000"
        self._check_block_key(block_v0_3_converted, self.block_v0_1a_tx_v2, is_v3=False)


if __name__ == "__main__":
    unittest.main()
