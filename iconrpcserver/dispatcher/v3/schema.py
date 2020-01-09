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

TX_V3_ORIGIN = {
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
    "dataType": {"type": "string", "enum": ["call", "deploy", "message", "deposit"]},
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
            {"type": "string"},
            {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "withdraw"]},
                    "id": {"type": "string"}
                },
                "additionalProperties": False,
                "required": ["action"]
            }
        ],
    }
}

icx_getBlock: dict = {
    "title": "icx_getBlock",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "hash": {"type": "string", "format": "hash_hex_0x"},
                "height": {"type": "string", "format": "int_16"},
            },
            "additionalProperties": False
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
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

icx_getBlockByHeight: dict = {
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

icx_getBlockByHash: dict = {
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
                "hash": {"type": "string", "format": "hash_hex_0x"},
            },
            "additionalProperties": False,
            "required": ["hash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_call: dict = {
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

icx_getBalance: dict = {
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

icx_getScoreApi: dict = {
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

icx_getTransactionResult: dict = {
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
                "txHash": {"type": "string", "format": "hash_hex_0x"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getTransactionByHash: dict = {
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
                "txHash": {"type": "string", "format": "hash_hex_0x"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getTransactionProof: dict = {
    "title": "icx_getTransactionProof",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_gettransactionproof",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string", "format": "hash_hex_0x"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getReceiptProof: dict = {
    "title": "icx_getReceiptProof",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_getreceiptproof",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string", "format": "hash_hex_0x"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_proveTransaction: dict = {
    "title": "icx_proveTransaction",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_provetransaction",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string", "format": "hash_hex_0x"},
                "proof": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "left": {"type": "string", "format": "hash_hex_0x"},
                                },
                                "additionalProperties": False,
                                "required": ["left"]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "right": {"type": "string", "format": "hash_hex_0x"},
                                },
                                "additionalProperties": False,
                                "required": ["right"]
                            }
                        ],
                    }
                }
            },
            "additionalProperties": False,
            "required": ["txHash", "proof"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_proveReceipt: dict = {
    "title": "icx_proveReceipt",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_provetreceipt",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string", "format": "hash_hex_0x"},
                "proof": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "left": {"type": "string", "format": "hash_hex_0x"},
                                },
                                "additionalProperties": False,
                                "required": ["left"]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "right": {"type": "string", "format": "hash_hex_0x"},
                                },
                                "additionalProperties": False,
                                "required": ["right"]
                            }
                        ],
                    }
                }
            },
            "additionalProperties": False,
            "required": ["txHash", "proof"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

ise_getStatus: dict = {
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

icx_sendTransaction: dict = {
    "title": "icx_sendTransaction",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_sendtransaction",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "params": {
            "type": "object",
            "properties": TX_V3_ORIGIN,
            "additionalProperties": False,
            "required": ["version", "from", "to", "stepLimit", "timestamp", "nid", "signature"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]

}

rep_getListByHash: dict = {
    "title": "rep_getListByHash",
    "id": "https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#rep_getlist",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "params": {
            "type": "object",
            "properties": {
                "repsHash": {"type": "string", "format": "hash_hex_0x"}
            },
            "additionalProperties": False,
            "required": ["repsHash"]
        },
        "id": {"type": "number"},
    }
}

SCHEMA_V3: dict = {
    "icx_getBlock": icx_getBlock,
    "icx_getLastBlock": icx_getLastBlock,
    "icx_getBlockByHeight": icx_getBlockByHeight,
    "icx_getBlockByHash": icx_getBlockByHash,
    "icx_call": icx_call,
    "icx_getBalance": icx_getBalance,
    "icx_getScoreApi": icx_getScoreApi,
    "icx_getTotalSupply": icx_getTotalSupply,
    "icx_getTransactionResult": icx_getTransactionResult,
    "icx_getTransactionByHash": icx_getTransactionByHash,
    "icx_getTransactionProof": icx_getTransactionProof,
    "icx_getReceiptProof": icx_getReceiptProof,
    "icx_proveTransaction": icx_proveTransaction,
    "icx_proveReceipt": icx_proveReceipt,
    "icx_sendTransaction": icx_sendTransaction,
    "ise_getStatus": ise_getStatus,
    "rep_getListByHash": rep_getListByHash,
}

validate_jsonschema_v3 = partial(validate_jsonschema, schemas=SCHEMA_V3)
