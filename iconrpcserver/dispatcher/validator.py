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

import re

from jsonrpcserver import status
from jsonschema import Draft4Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from .exception import GenericJsonRpcServerError, JsonError

node_getChannelInfos: dict = {
    "title": "node_getChannelInfos",
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

node_getBlockByHeight: dict = {
    "title": "node_getBlockByHeight",
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

node_getCitizens: dict = {
    "title": "node_getCitizens",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {"type": "object"}
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
}

SCHEMA_NODE: dict = {
    "node_getChannelInfos": node_getChannelInfos,
    "node_getBlockByHeight": node_getBlockByHeight,
    "node_getCitizens": node_getCitizens
}


def validate_jsonschema_node(request: object):
    validate_jsonschema(request, SCHEMA_NODE)


icx_sendTransaction_v2: dict = {
    "title": "icx_sendTransaction",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_sendtransaction",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "from": {"type": "string", "format": "address_eoa"},
                "to": {"type": "string", "format": "address_eoa"},
                "value": {"type": "string", "format": "int_16"},
                "fee": {"type": "string", "format": "int_16"},
                "timestamp": {"type": "string", "format": "int_10"},
                "nonce": {"type": "string", "format": "int_10"},
                "tx_hash": {"type": "string", "format": "hash_v2"},
                "signature": {"type": "string"},
            },
            "additionalProperties": False,
            "required": ["from", "to", "value", "fee", "timestamp", "tx_hash", "signature"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]

}

icx_getTransactionResult_v2: dict = {
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
                "tx_hash": {"type": "string", "format": "hash_v2"},
            },
            "additionalProperties": False,
            "required": ["tx_hash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBalance_v2: dict = {
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

icx_getBlockByHeight_v2: dict = {
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

icx_getBlockByHash_v2: dict = {
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
                "hash": {"type": "string", "format": "hash_v2"},
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

icx_getTransactionByAddress_v2: dict = {
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
    "icx_sendTransaction": icx_sendTransaction_v2,
    "icx_getTransactionResult": icx_getTransactionResult_v2,
    "icx_getBalance": icx_getBalance_v2,
    "icx_getTotalSupply": icx_getTotalSupply,
    "icx_getLastBlock": icx_getLastBlock,
    "icx_getBlockByHash": icx_getBlockByHash_v2,
    "icx_getBlockByHeight": icx_getBlockByHeight_v2,
    "icx_getTransactionByAddress": icx_getTransactionByAddress_v2
}


def validate_jsonschema_v2(request: object):
    validate_jsonschema(request, SCHEMA_V2)


icx_getBlockByHeight_v3: dict = {
    "title": "icx_getBlockByHeight",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_getblockbyheight",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "height": {"type": "string", "format": "int_16"},
            },
            "additionalProperties": False,
            "required": ["height"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBlockByHash_v3: dict = {
    "title": "icx_getBlockByHash",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_getblockbyhash",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "hash": {"type": "string", "format": "hash"},
            },
            "additionalProperties": False,
            "required": ["hash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_call_v3: dict = {
    "title": "icx_call",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_call",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string", "enum": ["icx_call"]},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "from": {"type": "string", "format": "address_eoa"},
                "to": {"type": "string", "format": "address_score"},
                "dataType": {"type": "string", "enum": ["call"]},
                "data": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string"},
                        "params": {"type": "object"}
                    },
                    "additionalProperties": False,
                    "required": ["method"]
                },
            },
            "additionalProperties": False,
            "required": ["to", "dataType", "data"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBalance_v3: dict = {
    "title": "icx_getBalance",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_getbalance",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "format": "address"}
            },
            "additionalProperties": False,
            "required": ["address"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getScoreApi_v3: dict = {
    "title": "icx_getScoreApi",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_getscoreapi",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "format": "address_score"}
            },
            "additionalProperties": False,
            "required": ["address"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getTransactionResult_v3: dict = {
    "title": "icx_getTransactionResult",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_gettransactionresult",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string", "format": "hash"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getTransactionByHash_v3: dict = {
    "title": "icx_getTransactionByHash",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_gettransactionbyhash",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string", "format": "hash"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

ise_getStatus_v3: dict = {
    "title": "ise_getStatus",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#ise_getstatus",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_sendTransaction_v3: dict = {
    "title": "icx_sendTransaction",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_sendtransaction",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "version": {"type": "string", "format": "int_16"},
                "from": {"type": "string", "format": "address_eoa"},
                "to": {"type": "string", "format": "address"},
                "value": {"type": "string", "format": "int_16"},
                "message": {"type": "string"},
                "stepLimit": {"type": "string", "format": "int_16"},
                "timestamp": {"type": "string", "format": "int_16"},
                "nid": {"type": "string", "format": "int_16"},
                "nonce": {"type": "string", "format": "int_16"},
                "signature": {"type": "string"},
                "dataType": {"type": "string", "enum": ["call", "deploy", "message"]},
                "data": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string"},
                                "params": {"type": "object"}
                            },
                            "additionalProperties": False,
                            "required": ["method"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "contentType": {"type": "string", "enum": ["application/zip", "application/tbears"]},
                                "content": {"type": "string"},  # tbears get string content
                                "params": {"type": "object"}
                            },
                            "additionalProperties": False,
                            "required": ["contentType", "content"]
                        },
                        {"type": "string"}
                    ],
                }
            },
            "additionalProperties": False,
            "required": ["version", "from", "to", "stepLimit", "timestamp", "nid", "signature"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]

}

debug_estimateStep_v3: dict = {
    "title": "debug_estimateStep",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#debug_estimateStep",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "version": {"type": "string", "format": "int_16"},
                "from": {"type": "string", "format": "address_eoa"},
                "to": {"type": "string", "format": "address"},
                "value": {"type": "string", "format": "int_16"},
                "message": {"type": "string"},
                "timestamp": {"type": "string", "format": "int_16"},
                "nid": {"type": "string", "format": "int_16"},
                "nonce": {"type": "string", "format": "int_16"},
                "dataType": {"type": "string", "enum": ["call", "deploy", "message"]},
                "data": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string"},
                                "params": {"type": "object"}
                            },
                            "additionalProperties": False,
                            "required": ["method"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "contentType": {"type": "string", "enum": ["application/zip", "application/tbears"]},
                                "content": {"type": "string"},  # tbears get string content
                                "params": {"type": "object"}
                            },
                            "additionalProperties": False,
                            "required": ["contentType", "content"]
                        },
                        {"type": "string"}
                    ],
                }
            },
            "additionalProperties": False,
            "required": ["version", "from", "to","timestamp"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]

}

rep_getList_v3: dict = {
    "title": "rep_getList",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#rep_getlist",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
    }
}


SCHEMA_V3: dict = {
    "icx_getLastBlock": icx_getLastBlock,
    "icx_getBlockByHeight": icx_getBlockByHeight_v3,
    "icx_getBlockByHash": icx_getBlockByHash_v3,
    "icx_call": icx_call_v3,
    "icx_getBalance": icx_getBalance_v3,
    "icx_getScoreApi": icx_getScoreApi_v3,
    "icx_getTotalSupply": icx_getTotalSupply,
    "icx_getTransactionResult": icx_getTransactionResult_v3,
    "icx_getTransactionByHash": icx_getTransactionByHash_v3,
    "icx_sendTransaction": icx_sendTransaction_v3,
    "debug_estimateStep": debug_estimateStep_v3,
    "ise_getStatus": ise_getStatus_v3,
    "rep_getList": rep_getList_v3
}


def validate_jsonschema_v3(request: object):
    validate_jsonschema(request, SCHEMA_V3)


def validate_jsonschema(request: object, schemas: dict = SCHEMA_V3):
    """ Validate JSON-RPC v3 schema.

    refer to
    v2 : https://github.com/icon-project/icx_JSON_RPC
    v3 : https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3

    :param request: JSON-RPC request to validate
    :param schemas: The schema to validate with
    :return: N/A
    """
    # get JSON-RPC batch request
    if isinstance(request, list):
        for req in request:
            validate_jsonschema(req, schemas=schemas)
        return

    # get schema for 'method'
    schema: dict = None
    method = request.get('method', None)

    if method and isinstance(method, str):
        schema = schemas.get(method, None)
    if schema is None:
        raise GenericJsonRpcServerError(code=JsonError.METHOD_NOT_FOUND,
                                        message=f"JSON schema validation error: Method not found",
                                        http_status=status.HTTP_BAD_REQUEST)

    # create a new validator with format_checker
    validator = Draft4Validator(schema=schema, format_checker=format_checker)

    # check request
    try:
        validator.validate(request)
    except ValidationError as e:
        if e.schema_path[-1] == "additionalProperties":
            if len(e.path) == 0:
                message = f"There is an invalid key in 1st depth"
            else:
                message = f"There is an invalid key in '{e.path[-1]}'"
        elif len(e.path) > 0:
            message = f"'{e.path[-1]}' has an invalid value"
        else:
            message = f"Invalid params"

        raise GenericJsonRpcServerError(code=JsonError.INVALID_PARAMS,
                                        message=f"JSON schema validation error: {message}",
                                        http_status=status.HTTP_BAD_REQUEST)


def is_lowercase_hex_string(value: str) -> bool:
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


format_checker = FormatChecker()


@format_checker.checks('address')
def check_address(address: str):
    if isinstance(address, str) and len(address) == 42 and is_lowercase_hex_string(address[2:]) \
            and (address.startswith('cx') or address.startswith('hx')):
        return True

    return False


@format_checker.checks('address_eoa')
def check_address_eoa(address: str):
    if isinstance(address, str) and len(address) == 42 and is_lowercase_hex_string(address[2:]) \
            and address.startswith('hx'):
        return True

    return False


@format_checker.checks('address_score')
def check_address_score(address: str):
    if isinstance(address, str) and len(address) == 42 and is_lowercase_hex_string(address[2:]) \
            and address.startswith('cx'):
        return True

    return False


@format_checker.checks('int_10')
def check_int_10(value: str):
    if not isinstance(value, str):
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False


@format_checker.checks('int_16')
def check_int_16(value: str):
    if isinstance(value, str) and value.startswith('0x') and is_lowercase_hex_string(value[2:]):
        return True

    return False


@format_checker.checks('hash')
def check_hash(value: str):
    if isinstance(value, str) and len(value) == 66 and value.startswith('0x') and is_lowercase_hex_string(value[2:]):
        return True

    return False


@format_checker.checks('hash_v2')
def check_hash_v2(value: str):
    if isinstance(value, str) and len(value) == 64 and is_lowercase_hex_string(value):
        return True

    return False


@format_checker.checks('binary_data')
def check_binary_data(value: str):
    if isinstance(value, str) and len(value) % 2 == 0 and value.startswith('0x') and is_lowercase_hex_string(value[2:]):
        return True

    return False
