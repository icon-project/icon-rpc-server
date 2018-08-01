# -*- coding: utf-8 -*-

# Copyright 2017-2018 theloop Inc.
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

import unittest
from typing import Union

from iconrpcserver.server.json_rpc.exception import GenericJsonRpcServerError
from iconrpcserver.server.json_rpc.validator import validate_jsonschema_v2, validate_jsonschema_v3
from tests import create_address, create_tx_hash


class TestJsonschemaValidator(unittest.TestCase):
    def setUp(self):
        self.validator = None

    def check_valid(self, full_data: dict):
        try:
            self.validator(full_data)
        except:
            self.fail(f'error with : {full_data}')

    def check_invalid(self, full_data: dict):
        self.assertRaises(GenericJsonRpcServerError, self.validator, full_data)

    def check_more(self, full_data: dict, data: Union[dict, str, None], required_keys: list,
                   invalid_value: object = list()):
        # check required key validation
        for key in required_keys:
            self._check_required(full_data, data, key, invalid_value)

        # check required key validation
        if isinstance(data, dict):
            self._check_invalid_key(full_data, data)

    def _check_required(self, full_data: dict, data: dict, key: str, invalid_value: object = list()):
        # remove required key and test
        original_value = data.pop(key)
        self.check_invalid(full_data=full_data)

        # add value with invalid type. we do not support int type value
        data[key] = invalid_value
        self.check_invalid(full_data=full_data)

        # recover original value
        data[key] = original_value

    def _check_invalid_key(self, full_data: dict, data: dict):
        # add invalid key to params
        data['invalid_key'] = "invalid_value"
        self.check_invalid(full_data=full_data)
        data.pop('invalid_key')


class TestJsonschemValidatorV2(TestJsonschemaValidator):
    def setUp(self):
        self.validator = validate_jsonschema_v2

        self.sendTransaction = {
            "jsonrpc": "2.0",
            "id": 1234,
            'method': 'icx_sendTransaction',
            'params': {
                "from": create_address(data=b'from'),
                "to": create_address(data=b'to'),
                "value": "0xde0b6b3a7640000",
                "fee": "0x12345",
                "timestamp": "1516942975500598",
                "nonce": "1234",
                'tx_hash': create_tx_hash(b'tx', is_v3=False),
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA=",
            }
        }
        self.getTransactionResult = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getTransactionResult",
            "params": {
                'tx_hash': create_tx_hash(b'tx', is_v3=False),
            }
        }
        self.getBalance = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getBalance",
            "params": {
                "address": create_address(data=b'from'),
            }
        }
        self.getBlockByHeight = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getBlockByHeight",
            "params": {
                "height": "412"
            }
        }
        self.getBlockByHash = {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHash",
            "id": 1234,
            "params": {
                "hash": create_tx_hash(b'tx', is_v3=False),
            }
        }
        self.getLastBlock = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getLastBlock"
        }
        self.getTotalSupply = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getTotalSupply",
        }
        self.icx_getTransactionByAddress = {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionByAddress",
            "id": 1234,
            "params": {
                "address": create_address(data=b'address'),
                "index": 0
            }
        }

    def check_address(self, full_data: dict, data: dict, keys: list):
        for key in keys:
            org_addr = data.get(key)
            data[key] = create_address(data=b'addr', is_eoa=False)
            self.check_invalid(full_data=full_data)
            data[key] = org_addr

    def test_sendTransaction(self):
        full_data = self.sendTransaction

        # check default function
        self.check_valid(full_data=full_data)

        # check with invalid address
        params = full_data['params']
        addr_keys = ['from', 'to']
        self.check_address(full_data=full_data, data=params, keys=addr_keys)

        # remove non-required key and test
        params.pop('nonce')
        self.check_valid(full_data=full_data)

        # check full_data['params']
        required_keys = ['from', 'to', 'value', 'fee', 'timestamp', 'tx_hash', 'signature']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getTransactionResult(self):
        full_data = self.getTransactionResult

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['tx_hash']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getBalance(self):
        full_data = self.getBalance

        # check default function
        self.check_valid(full_data=full_data)

        # check with invalid address
        params = full_data['params']
        addr_keys = ['address']
        self.check_address(full_data=full_data, data=params, keys=addr_keys)

        # check required key validation
        required_keys = ['address']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getBlockByHeight(self):
        full_data = self.getBlockByHeight

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['height']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getBlockByHash(self):
        full_data = self.getBlockByHash

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['hash']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getLastBlock(self):
        full_data = self.getLastBlock

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        required_keys = ['jsonrpc', 'id']
        self.check_more(full_data=full_data, data=full_data, required_keys=required_keys)

    def test_getTotalSupply(self):
        full_data = self.getTotalSupply

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        required_keys = ['jsonrpc', 'id', 'method']
        self.check_more(full_data=full_data, data=full_data, required_keys=required_keys)

    def test_getTransactionByAddress(self):
        full_data = self.icx_getTransactionByAddress

        # check default function
        self.check_valid(full_data=full_data)

        # check with invalid address
        params = full_data['params']
        addr_keys = ['address']
        self.check_address(full_data=full_data, data=params, keys=addr_keys)

        # check required key validation
        required_keys = ['address', 'index']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_batch_request(self):
        batch_request = [self.getBlockByHash, self.sendTransaction, self.getBalance]
        try:
            validate_jsonschema_v2(batch_request)
        except:
            self.fail('raise exception!')


class TestJsonschemValidatorV3(TestJsonschemaValidator):
    def setUp(self):
        self.validator = validate_jsonschema_v3

        self.getLastBlock = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getLastBlock"
        }
        self.getBlockByHeight = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getBlockByHeight",
            "params": {
                "height": "0x4d2"
            }
        }
        self.getBlockByHash = {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHash",
            "id": 1234,
            "params": {
                "hash": "0x1fcf7c34dc875681761bdaa5d75d770e78e8166b5c4f06c226c53300cbe85f57"
            }
        }
        self.call = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_call",
            "params": {
                "from": create_address(data=b'from'),
                "to": create_address(data=b'to', is_eoa=False),
                "dataType": "call",
                "data": {
                    "method": "get_balance",
                    "params": {
                        "address": "hx1f9a3310f60a03934b917509c86442db703cbd52"
                    }
                }
            }
        }
        self.getBalance = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getBalance",
            "params": {
                "address": create_address(data=b'from'),
            }
        }
        self.getScoreApi = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getScoreApi",
            "params": {
                "address": create_address(data=b'from', is_eoa=False),
            }
        }
        self.getTotalSupply = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getTotalSupply",
        }
        self.getTransactionResult = {
            "jsonrpc": "2.0",
            "id": 1234,
            "method": "icx_getTransactionResult",
            "params": {
                'txHash': create_tx_hash(b'tx')
            }
        }
        self.getTransactionByHash = {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionByHash",
            "id": 1234,
            "params": {
                "txHash": "0xb903239f8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238"
            }
        }
        self.sendTransaction = {
            "jsonrpc": "2.0",
            "id": 3000,
            'method': 'icx_sendTransaction',
            'params': {
                "version": "0x3",
                "from": create_address(data=b'from'),
                "to": create_address(data=b'to', is_eoa=False),
                "value": "0xde0b6b3a7640000",
                "stepLimit": "0x12345",
                "timestamp": "0x563a6cf330136",
                "nid": "0x3fcb",
                "nonce": "0x1",
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA=",
            }
        }

        self.sendTransaction_call = {
            "jsonrpc": "2.0",
            "id": 3001,
            'method': 'icx_sendTransaction',
            'params': {
                "version": "0x3",
                "from": create_address(data=b'from'),
                "to": create_address(data=b'to', is_eoa=False),
                "value": "0xde0b6b3a7640000",
                "stepLimit": "0x12345",
                "timestamp": "0x563a6cf330136",
                "nid": "0x3fcb",
                "nonce": "0x1",
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA=",
                "dataType": "call",
                "data": {
                    "method": "transfer",
                    "params": {
                        "to": create_address(data=b'someone'),
                        "value": "0x1"
                    }
                }
            }
        }

        self.sendTransaction_deploy = {
            "jsonrpc": "2.0",
            "id": 3002,
            'method': 'icx_sendTransaction',
            'params': {
                "version": "0x3",
                "from": create_address(data=b'from'),
                "to": create_address(data=b'to', is_eoa=False),
                "value": "0xde0b6b3a7640000",
                "stepLimit": "0x12345",
                "timestamp": "0x563a6cf330136",
                "nid": "0x3fcb",
                "nonce": "0x1",
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA=",
                "dataType": "deploy",
                "data": {
                    "contentType": "application/zip",
                    "content": "0x0102c2",
                    "params": {
                        "arg1": "value1",
                        "arg2": "value2"
                    }
                }
            }
        }

        self.sendTransaction_message = {
            "jsonrpc": "2.0",
            "id": 3003,
            'method': 'icx_sendTransaction',
            'params': {
                "version": "0x3",
                "from": create_address(data=b'from'),
                "to": create_address(data=b'to', is_eoa=False),
                "value": "0xde0b6b3a7640000",
                "stepLimit": "0x12345",
                "timestamp": "0x563a6cf330136",
                "nid": "0x3fcb",
                "nonce": "0x1",
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA=",
                "dataType": "deploy",
                "data": "0xmessage"
            }
        }

    def test_getLastBlock(self):
        full_data = self.getLastBlock

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        required_keys = ['jsonrpc', 'id']
        self.check_more(full_data=full_data, data=full_data, required_keys=required_keys)

    def test_getBlockByHeight(self):
        full_data = self.getBlockByHeight

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['height']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getBlockByHash(self):
        full_data = self.getBlockByHash

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['hash']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_call(self):
        full_data = self.call

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['to', 'dataType', 'data']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

        data = params['data']
        required_keys = ['method']
        self.check_more(full_data=full_data, data=data, required_keys=required_keys)

    def test_getBalance(self):
        full_data = self.getBalance

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['address']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getScoreApi(self):
        full_data = self.getScoreApi

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['address']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getTotalSupply(self):
        full_data = self.getTotalSupply

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        required_keys = ['jsonrpc', 'id', 'method']
        self.check_more(full_data=full_data, data=full_data, required_keys=required_keys)

    def test_getTransactionResult(self):
        full_data = self.getTransactionResult

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['txHash']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_getTransactionByHash(self):
        full_data = self.getTransactionByHash

        # check default function
        self.check_valid(full_data=full_data)

        # check required key validation
        params = full_data['params']
        required_keys = ['txHash']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

    def test_sendTransaction(self):
        send_txs = [
            self.sendTransaction,
            self.sendTransaction_call,
            self.sendTransaction_deploy,
            self.sendTransaction_message
        ]

        for data in send_txs:
            self.check_sendTransaction(data)

    def check_sendTransaction(self, full_data):
        # check default function
        self.check_valid(full_data=full_data)

        # remove non-required key and test
        params = full_data['params']
        params.pop('to')
        self.check_valid(full_data=full_data)

        # check full_data['params']
        required_keys = ['version', 'from', 'stepLimit', 'timestamp', 'nid', 'signature']
        self.check_more(full_data=full_data, data=params, required_keys=required_keys)

        # check full_data['params']['data']
        data = params.get('data', None)
        self.check_more(full_data=full_data, data=data, required_keys=[])

    def test_batch_request(self):
        batch_request = [self.call, self.sendTransaction, self.getTotalSupply]
        try:
            validate_jsonschema_v3(batch_request)
        except:
            self.fail('raise exception!')

    def test_format_checker(self):
        from iconrpcserver.server.json_rpc import validator
        # address
        inputs = [
            (create_address(data=b'test', is_eoa=True), True, "EOA address"),
            (create_address(data=b'test', is_eoa=False), True, "SCORE address"),
            (f'hx{"a"*40}', True, "valid length 42"),
            (f'hx{"a"*39}', False, "invalid length 41"),
            (f'hx{"a"*41}', False, "invalid length 43"),
            (f'hx{"a"*39}a', True, "valid lowercase string"),
            (f'hx{"a"*39}A', False, "invalid lowercase string"),
            (f'hx{"a"*39}w', False, "invalid hex string"),
            (f'0x{"a"*40}', False, "invalid prefix '0x'"),
            (b'hx{"a"*40}', False, "invalid type bytes"),
        ]
        self.validate_format_checker(validator.check_address, inputs)

        # address_eoa
        inputs = [
            (create_address(data=b'test', is_eoa=True), True, "EOA address"),
            (create_address(data=b'test', is_eoa=False), False, "SCORE address"),
            (f'hx{"a"*40}', True, "valid length 42"),
            (f'hx{"a"*39}', False, "invalid length 41"),
            (f'hx{"a"*41}', False, "invalid length 43"),
            (f'hx{"a"*39}a', True, "valid lowercase string"),
            (f'hx{"a"*39}A', False, "invalid lowercase string"),
            (f'hx{"a"*39}w', False, "invalid hex string"),
            (f'0x{"a"*40}', False, "invalid prefix '0x'"),
            (f'cx{"a"*40}', False, "invalid prefix 'cx'"),
            (b'hx{"a"*40}', False, "invalid type bytes"),
        ]
        self.validate_format_checker(validator.check_address_eoa, inputs)

        # address_score
        inputs = [
            (create_address(data=b'test', is_eoa=True), False, "EOA address"),
            (create_address(data=b'test', is_eoa=False), True, "SCORE address"),
            (f'cx{"a"*40}', True, "valid length 42"),
            (f'cx{"a"*39}', False, "invalid length 41"),
            (f'cx{"a"*41}', False, "invalid length 43"),
            (f'cx{"a"*39}a', True, "valid lowercase string"),
            (f'cx{"a"*39}A', False, "invalid lowercase string"),
            (f'cx{"a"*39}w', False, "invalid hex string"),
            (f'0x{"a"*40}', False, "invalid prefix '0x'"),
            (f'hx{"a"*40}', False, "invalid prefix 'hx'"),
            (b'cx{"a"*40}', False, "invalid type bytes"),
        ]
        self.validate_format_checker(validator.check_address_score, inputs)

        # int_16
        inputs = [
            ('0x123cf', True, "valid lowercase string"),
            ('0x123CF', False, "invalid lowercase string"),
            ('0x123w', False, "invalid hex string"),
            ('123cf', False, "invalid prefix"),
            ('cx123cf', False, "invalid prefix 'cx'"),
            ('hx123cf', False, "invalid prefix 'hx'"),
            (b'123cf}', False, "invalid type bytes"),
            (1234, False, "invalid type int"),
            (1e18, False, "invalid type float"),
        ]
        self.validate_format_checker(validator.check_int_16, inputs)

        # int_10
        inputs = [
            ('123', True, "valid decimal string"),
            ('123a', False, "invalid hex string"),
            ('0x123cf', False, "invalid prefix"),
            (b'123', False, "invalid type bytes"),
            (1234, False, "invalid type int"),
            (1e18, False, "invalid type float"),
        ]
        self.validate_format_checker(validator.check_int_10, inputs)

        # hash
        inputs = [
            (create_tx_hash(b'hash'), True, "valid lowercase string"),
            (f'0x{"a"*64}', True, "valid length"),
            (f'0x{"a"*63}', False, "invalid length 65"),
            (f'0x{"a"*65}', False, "invalid length 67"),
            (f'0x{"a"*63}a', True, "valid lowercase string"),
            (f'0x{"a"*63}A', False, "invalid lowercase string"),
            (f'0x{"a"*63}w', False, "invalid hex string"),
            (f'cx{"a"*64}', False, "invalid prefix 'cx'"),
            (f'hx{"a"*64}', False, "invalid prefix 'hx'"),
            (b'0x{"a"*64}', False, "invalid type bytes"),
        ]
        self.validate_format_checker(validator.check_hash, inputs)

        # hash_v2
        inputs = [
            (create_tx_hash(b'hash', is_v3=False), True, "valid lowercase string"),
            (f'{"a"*64}', True, "valid length"),
            (f'{"a"*63}', False, "invalid length 65"),
            (f'{"a"*65}', False, "invalid length 67"),
            (f'{"a"*63}a', True, "valid lowercase string"),
            (f'{"a"*63}A', False, "invalid lowercase string"),
            (f'{"a"*63}w', False, "invalid hex string"),
            (f'0x{"a"*62}', False, "invalid prefix '0x'"),
            (f'hx{"a"*62}', False, "invalid prefix 'cx'"),
            (f'hx{"a"*62}', False, "invalid prefix 'hx'"),
            (b'{"a"*64}', False, "invalid type bytes"),
        ]
        self.validate_format_checker(validator.check_hash_v2, inputs)

        # binary data
        inputs = [
            (f'0x01', True, "valid length even"),
            (f'0x1', False, "invalid length odd"),
            (f'0x1a', True, "valid lowercase string"),
            (f'0x1A', False, "invalid lowercase string"),
            (f'0x1w', False, "invalid hex string"),
            (f'cx01', False, "invalid prefix 'cx'"),
            (f'hx01', False, "invalid prefix 'hx'"),
            (b'0x01', False, "invalid type bytes"),
        ]
        self.validate_format_checker(validator.check_binary_data, inputs)

        pass

    def validate_format_checker(self, func: callable, case_list: list):
        for case in case_list:
            if func(case[0]) != case[1]:
                self.fail(f'error case : [{func.__name__}] {case[2]}')
