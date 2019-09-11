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
from functools import partial

from iconrpcserver.dispatcher import validate_jsonschema

TX_V2_ORIGIN = {
    "from": {"type": "string", "format": "address_eoa"},
    "to": {"type": "string", "format": "address_eoa"},
    "value": {"type": "string", "format": "int_16"},
    "fee": {"type": "string", "format": "int_16"},
    "timestamp": {"type": "string", "format": "int_10"},
    "nonce": {"type": "string", "format": "int_10"},
    "tx_hash": {"type": "string", "format": "hash_hex_without_0x"},
    "signature": {"type": "string"},
}

icx_sendTransaction: dict = {
    "title": "icx_sendTransaction",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_sendtransaction",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": TX_V2_ORIGIN,
            "additionalProperties": False,
            "required": ["from", "to", "value", "fee", "timestamp", "tx_hash", "signature"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]

}

icx_getTransactionResult: dict = {
    "title": "icx_getBalance",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getbalance",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "tx_hash": {"type": "string", "format": "hash_hex_without_0x"},
            },
            "additionalProperties": False,
            "required": ["tx_hash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBalance: dict = {
    "title": "icx_getBalance",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getbalance",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "format": "address"},
            },
            "additionalProperties": False,
            "required": ["address"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBlockByHeight: dict = {
    "title": "icx_getBlockByHeight",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getblockbyheight",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "height": {"type": "string", "format": "int_10"},
                "channel": {"type": "string"},
            },
            "additionalProperties": False,
            "required": ["height"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBlockByHash: dict = {
    "title": "icx_getBlockByHash",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getblockbyhash",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "hash": {"type": "string", "format": "hash_hex_without_0x"},
            },
            "additionalProperties": False,
            "required": ["hash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getLastBlock: dict = {
    "title": "icx_getLastBlock",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getlastblock",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {"type": "object"},
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
}

icx_getTransactionByAddress: dict = {
    "title": "icx_getTransactionByAddress",
    "id": "googledoc.icx_getTransactionByAddress",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "format": "address_eoa"},
                "index": {"type": "number"},
            },
            "additionalProperties": False,
            "required": ["address", "index"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
}

icx_getTotalSupply: dict = {
    "title": "icx_getTotalSupply",
    "id": "googledoc.icx_getTotalSupply",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {"type": "object"},
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
}

SCHEMA_V2: dict = {
    "icx_sendTransaction": icx_sendTransaction,
    "icx_getTransactionResult": icx_getTransactionResult,
    "icx_getBalance": icx_getBalance,
    "icx_getTotalSupply": icx_getTotalSupply,
    "icx_getLastBlock": icx_getLastBlock,
    "icx_getBlockByHash": icx_getBlockByHash,
    "icx_getBlockByHeight": icx_getBlockByHeight,
    "icx_getTransactionByAddress": icx_getTransactionByAddress
}

validate_jsonschema_v2 = partial(validate_jsonschema, schema=SCHEMA_V2)
