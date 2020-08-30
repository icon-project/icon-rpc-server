import json

import pytest
from mock import AsyncMock, MagicMock
from sanic import Sanic

from iconrpcserver.dispatcher.default import NodeDispatcher
from iconrpcserver.dispatcher.v2 import Version2Dispatcher
from iconrpcserver.dispatcher.v3 import Version3Dispatcher
from iconrpcserver.utils.message_queue.channel_inner_stub import (
    ChannelTxCreatorInnerStub, ChannelTxCreatorInnerTask, ChannelInnerTask, ChannelInnerStub
)
from iconrpcserver.utils.message_queue.icon_score_inner_stub import IconScoreInnerStub, IconScoreInnerTask
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

CHANNEL_STUB_NAME = "icon_dex"
CHANNEL_NAME = "icon_dex"
TX_RESULT_HASH = "0x4bf74e6aeeb43bde5dc8d5b62537a33ac8eb7605ebbdb51b015c1881b45b3aed"

# https://github.com/icon-project/icx_JSON_RPC
REQUESTS_V2 = {
    "icx_sendTransaction": {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 1234,
        "params": {
            "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
            "to": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd",
            "value": "0xde0b6b3a7640000",
            "fee": "0x12345",
            "timestamp": "1516942975500598",
            "nonce": "1",
            "tx_hash": "4bf74e6aeeb43bde5dc8d5b62537a33ac8eb7605ebbdb51b015c1881b45b3aed",
            "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA="
        }
    },
    "icx_getTransactionResult": {
        "jsonrpc": "2.0",
        "method": "icx_getTransactionResult",
        "id": 1234,
        "params": {
            "tx_hash": "9c60c91c5821ba70dee43d7ddc2a5b03b2958d8dffac6d35488b43b8a62ee372"
        }
    },
    "icx_getTransactionResult_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionResult",
            "id": 1234,
            "params": {
                "tx_hash": "9c60c91c5821ba70dee43d7ddc2a5b03b2958d8dffac6d35488b43b8a62ee372"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionResult",
            "id": 1234,
            "params": {
                "tx_hash": "375540830d475a73b704cf8dee9fa9eba2798f9d2af1fa55a85482e48daefd3b"
            }
        }
    ],
    "icx_getBalance": {
        "jsonrpc": "2.0",
        "method": "icx_getBalance",
        "id": 1234,
        "params": {
            "address": "hxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
        }
    },
    "icx_getBalance_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getBalance",
            "id": 1234,
            "params": {
                "address": "hxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBalance",
            "id": 1234,
            "params": {
                "address": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd"
            }
        }
    ],
    "icx_getBlockByHeight": {
        "jsonrpc": "2.0",
        "method": "icx_getBlockByHeight",
        "id": 1234,
        "params": {
            "height": "0"
        }
    },
    "icx_getBlockByHeight_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHeight",
            "id": 1234,
            "params": {
                "height": "1",
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHeight",
            "id": 1234,
            "params": {
                "height": "2",
            }
        }
    ],
    "icx_getBlockByHash": {
        "jsonrpc": "2.0",
        "method": "icx_getBlockByHash",
        "id": 1234,
        "params": {
            "hash": "cf43b3fd45981431a0e64f79d07bfcf703e064b73b802c5f32834eec72142190",
        }
    },
    "icx_getBlockByHash_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHash",
            "id": 1234,
            "params": {
                "hash": "3add53134014e940f6f6010173781c4d8bd677d9931a697f962483e04a685e5c",
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHash",
            "id": 1234,
            "params": {
                "hash": "2cd6b2a6edd6dbce861bd9b79e91b5bc8351e7c87430e93251dfcb309a8ecff8",
            }
        }
    ],
    "icx_getLastBlock": {
        "jsonrpc": "2.0",
        "id": 1234,
        "method": "icx_getLastBlock"
    }
}

# https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md
REQUESTS_V3 = {
    "icx_sendTransaction": {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 1234,
        "params": {
            "version": "0x3",
            "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
            "to": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd",
            "value": "0xde0b6b3a7640000",
            "stepLimit": "0x12345",
            "timestamp": "0x563a6cf330136",
            "nid": "0x3",
            "nonce": "0x1",
            "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA="
        }
    },
    "icx_getBlock": {
        "jsonrpc": "2.0",
        "method": "icx_getBlock",
        "id": 1234
    },
    "icx_getBlock_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlock",
            "id": 1234
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlock",
            "id": 1234,
            "params": {
                "height": "0x1"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlock",
            "id": 1234,
            "params": {
                "hash": "0xcf43b3fd45981431a0e64f79d07bfcf703e064b73b802c5f32834eec72142190",
            }
        },
    ],
    "icx_getLastBlock": {
        "jsonrpc": "2.0",
        "method": "icx_getLastBlock",
        "id": 1234
    },
    "icx_getBlockByHash": {
        "jsonrpc": "2.0",
        "method": "icx_getBlockByHash",
        "id": 1234,
        "params": {
            "hash": "0xcf43b3fd45981431a0e64f79d07bfcf703e064b73b802c5f32834eec72142190",
        }
    },
    "icx_getBlockByHash_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHash",
            "id": 1234,
            "params": {
                "hash": "0x3add53134014e940f6f6010173781c4d8bd677d9931a697f962483e04a685e5c",
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHash",
            "id": 1234,
            "params": {
                "hash": "0x2cd6b2a6edd6dbce861bd9b79e91b5bc8351e7c87430e93251dfcb309a8ecff8",
            }
        }
    ],
    "icx_getBlockByHeight": {
        "jsonrpc": "2.0",
        "method": "icx_getBlockByHeight",
        "id": 1234,
        "params": {
            "height": "0x0",
        }
    },
    "icx_getBlockByHeight_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHeight",
            "id": 1234,
            "params": {
                "height": "0x1",
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHeight",
            "id": 1234,
            "params": {
                "height": "0x2",
            }
        }
    ],
    "icx_call": {
        "jsonrpc": "2.0",
        "method": "icx_call",
        "id": 1234,
        "params": {
            "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
            "to": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32",
            "dataType": "call",
            "data": {
                "method": "get_balance",
                "params": {
                    "address": "hx1f9a3310f60a03934b917509c86442db703cbd52"
                }
            }
        }
    },
    "icx_call_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_call",
            "id": 1234,
            "params": {
                "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
                "to": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32",
                "dataType": "call",
                "data": {
                    "method": "get_balance",
                    "params": {
                        "address": "hx1f9a3310f60a03934b917509c86442db703cbd52"
                    }
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_call",
            "id": 1234,
            "params": {
                "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
                "to": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32",
                "dataType": "call",
                "data": {
                    "method": "get_balance",
                    "params": {
                        "address": "hxcd6f04b2a5184715ca89e523b6c823ceef2f9c3d"
                    }
                }
            }
        }
    ],
    "icx_getBalance": {
        "jsonrpc": "2.0",
        "method": "icx_getBalance",
        "id": 1234,
        "params": {
            "address": "hxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
        }
    },
    "icx_getBalance_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getBalance",
            "id": 1234,
            "params": {
                "address": "hxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getBalance",
            "id": 1234,
            "params": {
                "address": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd"
            }
        }
    ],
    "icx_getScoreApi": {
        "jsonrpc": "2.0",
        "method": "icx_getScoreApi",
        "id": 1234,
        "params": {
            "address": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
        }
    },
    "icx_getScoreApi_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getScoreApi",
            "id": 1234,
            "params": {
                "address": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getScoreApi",
            "id": 1234,
            "params": {
                "address": "cx502c47463314f01e84b1b203c315180501eb2481"
            }
        }
    ],
    "icx_getTotalSupply": {
        "jsonrpc": "2.0",
        "method": "icx_getTotalSupply",
        "id": 1234
    },
    "icx_getTransactionResult": {
        "jsonrpc": "2.0",
        "method": "icx_getTransactionResult",
        "id": 1234,
        "params": {
            "txHash": "0x9c60c91c5821ba70dee43d7ddc2a5b03b2958d8dffac6d35488b43b8a62ee372"
        }
    },
    "icx_getTransactionResult_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionResult",
            "id": 1234,
            "params": {
                "txHash": "0x9c60c91c5821ba70dee43d7ddc2a5b03b2958d8dffac6d35488b43b8a62ee372"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionResult",
            "id": 1234,
            "params": {
                "txHash": "0x375540830d475a73b704cf8dee9fa9eba2798f9d2af1fa55a85482e48daefd3b"
            }
        }
    ],
    "icx_getTransactionByHash": {
        "jsonrpc": "2.0",
        "method": "icx_getTransactionByHash",
        "id": 1234,
        "params": {
            "txHash": "0x9c60c91c5821ba70dee43d7ddc2a5b03b2958d8dffac6d35488b43b8a62ee372"
        }
    },
    "icx_getTransactionByHash_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionByHash",
            "id": 1234,
            "params": {
                "txHash": "0x9c60c91c5821ba70dee43d7ddc2a5b03b2958d8dffac6d35488b43b8a62ee372"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionByHash",
            "id": 1234,
            "params": {
                "txHash": "0x375540830d475a73b704cf8dee9fa9eba2798f9d2af1fa55a85482e48daefd3b"
            }
        }
    ],
    "icx_getTransactionProof": {
        "jsonrpc": "2.0",
        "method": "icx_getTransactionProof",
        "id": 1234,
        "params": {
            "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1"
        }
    },
    "icx_getTransactionProof_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionProof",
            "id": 1234,
            "params": {
                "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionProof",
            "id": 1234,
            "params": {
                "txHash": "0x375540830d475a73b704cf8dee9fa9eba2798f9d2af1fa55a85482e48daefd3b"
            }
        }
    ],
    "icx_getReceiptProof": {
        "jsonrpc": "2.0",
        "method": "icx_getReceiptProof",
        "id": 1234,
        "params": {
            "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1"
        }
    },
    "icx_getReceiptProof_batch": [
        {
            "jsonrpc": "2.0",
            "method": "icx_getReceiptProof",
            "id": 1234,
            "params": {
                "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "icx_getReceiptProof",
            "id": 1234,
            "params": {
                "txHash": "0x375540830d475a73b704cf8dee9fa9eba2798f9d2af1fa55a85482e48daefd3b"
            }
        }
    ],
    "icx_proveTransaction": {
        "jsonrpc": "2.0",
        "method": "icx_proveTransaction",
        "id": 1234,
        "params": {
            "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1",
            "proof":  [
                {
                    "left": "0xac1695c9d3ec0dedd7320d49e8b28bb76cb3f4332f99b396154d35cdb521efbc"
                },
                {
                    "right": "0xbb65b23173914f5618c4101b93a8a9e221814b3733dbd4cab6ae06f47982808e"
                }
            ]
        }
    },
    "icx_proveTransaction_batch": [
        {
            "jsonrpc" : "2.0",
            "method": "icx_proveTransaction",
            "id": 1234,
            "params": {
                "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1",
                "proof":  [
                    {
                        "left": "0xac1695c9d3ec0dedd7320d49e8b28bb76cb3f4332f99b396154d35cdb521efbc"
                    },
                    {
                        "right": "0xbb65b23173914f5618c4101b93a8a9e221814b3733dbd4cab6ae06f47982808e"
                    }
                ]
            }
        },
        {
            "jsonrpc" : "2.0",
            "method": "icx_proveTransaction",
            "id": 1234,
            "params": {
                "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1",
                "proof":  [
                    {
                        "left": "0xac1695c9d3ec0dedd7320d49e8b28bb76cb3f4332f99b396154d35cdb521efbc"
                    },
                    {
                        "right": "0xbb65b23173914f5618c4101b93a8a9e221814b3733dbd4cab6ae06f47982808e"
                    },
                    {
                        "right": "0xc845505ca7667bec30d03c67ba6cfa5a3829ed7d7f1250729bed5f780c31606e"
                    }
                ]
            }
        }
    ],
    "icx_proveReceipt": {
        "jsonrpc" : "2.0",
        "method": "icx_proveReceipt",
        "id": 1234,
        "params": {
            "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1",
            "proof":  [
                {
                    "left": "0xac1695c9d3ec0dedd7320d49e8b28bb76cb3f4332f99b396154d35cdb521efbc"
                },
                {
                    "right": "0xbb65b23173914f5618c4101b93a8a9e221814b3733dbd4cab6ae06f47982808e"
                }
            ]
        }
    },
    "icx_proveReceipt_batch": [
        {
            "jsonrpc" : "2.0",
            "method": "icx_proveReceipt",
            "id": 1234,
            "params": {
                "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1",
                "proof":  [
                    {
                        "left": "0xac1695c9d3ec0dedd7320d49e8b28bb76cb3f4332f99b396154d35cdb521efbc"
                    },
                    {
                        "right": "0xbb65b23173914f5618c4101b93a8a9e221814b3733dbd4cab6ae06f47982808e"
                    }
                ]
            }
        },
        {
            "jsonrpc" : "2.0",
            "method": "icx_proveReceipt",
            "id": 1234,
            "params": {
                "txHash": "0x6c85809ead0e601de5e84f063ef3b7d7c504b95a404356af6094f26a39713eb1",
                "proof":  [
                    {
                        "left": "0xac1695c9d3ec0dedd7320d49e8b28bb76cb3f4332f99b396154d35cdb521efbc"
                    },
                    {
                        "right": "0xbb65b23173914f5618c4101b93a8a9e221814b3733dbd4cab6ae06f47982808e"
                    },
                    {
                        "right": "0xc845505ca7667bec30d03c67ba6cfa5a3829ed7d7f1250729bed5f780c31606e"
                    }
                ]
            }
        }
    ]
}


class MockChannelInnerStub:
    def async_task(self):
        return self

    async def register_citizen(self, peer_id, target, connected_time):
        pass

    async def unregister_citizen(self, peer_id):
        pass

    async def wait_for_unregister_signal(self, peer_id):
        pass


@pytest.fixture(autouse=True)
def patch_stubcollection():
    mock_channel_stub: ChannelInnerStub = MockChannelInnerStub()
    StubCollection().channel_stubs[CHANNEL_STUB_NAME] = mock_channel_stub


@pytest.yield_fixture
def app():
    sanic_app = Sanic("test_sanic_app")

    sanic_app.add_route(NodeDispatcher.dispatch, '/api/node/', methods=['POST'])
    sanic_app.add_route(Version2Dispatcher.dispatch, '/api/v2/', methods=['POST'])
    sanic_app.add_route(Version3Dispatcher.dispatch, '/api/v3/', methods=['POST'])

    yield sanic_app


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


def create_channel_tx_creator_stub(**kwargs) -> ChannelTxCreatorInnerStub:
    """Create ChannelTxCreatorStub.

    Note that return value is actually `mock.Mock`.
    """
    task: ChannelTxCreatorInnerTask = AsyncMock(ChannelTxCreatorInnerTask)
    task.create_icx_tx.return_value = [
        kwargs.get("response_code"),
        kwargs.get("tx_hash", TX_RESULT_HASH),
        "relay_target"
    ]

    stub: ChannelTxCreatorInnerStub = MagicMock(ChannelTxCreatorInnerStub)
    stub.async_task.return_value = task

    return stub


def create_icon_score_stub(**kwargs) -> IconScoreInnerStub:
    """Create IconScoreInnerStub.

    Note that return value is actually `mock.Mock`.
    """
    task: IconScoreInnerTask = AsyncMock(IconScoreInnerTask)
    task.validate_transaction.return_value = "result"
    task.query.return_value = {
        "result": "0x2961fff8ca4a62327800000"
    }

    stub: IconScoreInnerStub = MagicMock(IconScoreInnerStub)
    stub.async_task.return_value = task

    return stub


def create_channel_stub(**kwargs) -> ChannelInnerStub:
    """Create ChannelInnerStub

    :param kwargs:
    :return:
    """

    task: ChannelInnerTask = AsyncMock(ChannelInnerTask)

    block_sample_response = {
        "version": "0.3",
        "height": 10324749,
        "signature": "d1PQ4ohfWlcn/rog105s23EcGheynGGXiclfejoBqXAD3Rcr3fdDk2knQSBym1p0tlF2XS0AByP5I1ixkQTNwAA=",
        "prev_block_hash": "826616f18d4759243f499c7a1b7a887036a736c5fd56be72ceec24657a915d9a",
        "merkle_tree_root_hash": "bae3dc17beacd58f8b66cc131397cbc58dd2661dc1cc493b6a904d62246c6eae",
        "time_stamp": 1572256968719354,
        "confirmed_transaction_list": [
            {
                "from": "hx399e2d2ba9a6431f9c35f899fc3c3e9c092f61a5",
                "to": "cx502c47463314f01e84b1b203c315180501eb2481",
                "version": "0x3",
                "nid": "0x1",
                "stepLimit": "0x7a120",
                "timestamp": "0x595f59a0613e8",
                "nonce": "0x1926",
                "dataType": "call",
                "data": {
                    "method": "transfer",
                    "params": {
                        "_to": "hx8bd3a649d5d11b9a5ea0e957a04649343d5ceef1",
                        "_value": "0x16345785d8a0000",
                        "_data": ""
                    }
                },
                "signature": "iX8vez6eeZywslpiXD5y0/eo5DTyY89aGI3nwx9ZXdgVdnyBHgJ0Sko0NHuR78TpEodA/aHVE5wsKhkhrNM7dAA=",
                "txHash": "0xbae3dc17beacd58f8b66cc131397cbc58dd2661dc1cc493b6a904d62246c6eae"
            }
        ],
        "block_hash": "d071ae4d4663bdbe4b5f635399323504edfcb7352b3ca7aabd2486873b6708ba",
        "peer_id": "hx49d9ad5be7c5b53f5c4429fe3dde1fe61510f12f",
        "next_leader": "hx49d9ad5be7c5b53f5c4429fe3dde1fe61510f12f"
    }

    # response_code, block_hash, confirm_info, block_data_json
    task.get_block.return_value = (
        kwargs.get("response_code"),
        "0xd071ae4d4663bdbe4b5f635399323504edfcb7352b3ca7aabd2486873b6708ba",
        b"confirm_info",
        json.dumps(block_sample_response)
    )

    # FIXME : for dipatcher v2
    task.get_block_v2.return_value = (
        kwargs.get("response_code"),
        "0xd071ae4d4663bdbe4b5f635399323504edfcb7352b3ca7aabd2486873b6708ba",
        json.dumps(block_sample_response)
    )

    invoke_sample_response = {
        "version": "0x3",
        "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
        "to": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd",
        "value": "0xde0b6b3a7640000",
        "stepLimit": "0x12345",
        "timestamp": "0x563a6cf330136",
        "nid": "0x3",
        "nonce": "0x1",
        "txHash": "0xb903239f8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238",
        "txIndex": "0x1",
        "blockHeight": "0x1234",
        "blockHash": "0xc71303ef8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238",
        "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA="
    }

    # response_code, invoke_result
    task.get_invoke_result.return_value = (
        kwargs.get("response_code"),
        json.dumps(invoke_sample_response)
    )

    tx_info_sample_response = {
        "transaction": {
            "version": "0x3",
            "timestamp": "0x5add84a7e9dbc",
            "dataType": "base",
            "data": {
                "prep": {
                    "irep": "0x2f4add6ae4f410b597a",
                    "rrep": "0x1c6",
                    "totalDelegation": "0xf5da59ab310a64b6f86caa",
                    "value": "0x2d3d9f272ab7de93"
                },
                "result": {
                    "coveredByFee": "0x3e9279b61b4800",
                    "coveredByOverIssuedICX": "0x0",
                    "issue": "0x2cff0cad749c9693"
                }
            }
        },
        "tx_index": "0x0",
        "block_height": "0x162d01b",
        "block_hash": "0xe3ea3e497d468a6c148ad853bae9ba2051334dad37c933bdb76e1a7a5a703382"
    }

    # response_code, tx_info
    task.get_tx_info.return_value = (
        kwargs.get("response_code"),
        tx_info_sample_response
    )

    proof_sample_response = [
        {
            "left": "0xac1695c9d3ec0dedd7320d49e8b28bb76cb3f4332f99b396154d35cdb521efbc"
        },
        {
            "right": "0xbb65b23173914f5618c4101b93a8a9e221814b3733dbd4cab6ae06f47982808e"
        }
    ]

    # response
    task.get_tx_proof.return_value = proof_sample_response

    # response
    task.get_receipt_proof.return_value = proof_sample_response

    # response
    task.prove_tx.return_value = '0x1'

    # response
    task.prove_receipt.return_value = '0x1'

    stub: ChannelInnerStub = MagicMock(ChannelInnerStub)
    stub.async_task.return_value = task

    return stub


@pytest.fixture(autouse=True)
def mocking_stub_collection():
    """Setup StubCollection and Teardown it after each test ends."""
    StubCollection().conf = {
        "channel": CHANNEL_NAME
    }
    StubCollection().icon_score_stubs[CHANNEL_NAME] = create_icon_score_stub()

    yield

    StubCollection().amqp_target = None
    StubCollection().amqp_key = None
    StubCollection().conf = None

    StubCollection().peer_stub = None
    StubCollection().channel_stubs = {}
    StubCollection().channel_tx_creator_stubs = {}
    StubCollection().icon_score_stubs = {}


class TestDispatcher:
    REQUESTS = {}

    @pytest.fixture
    def mock_channel_tx_creator(self):
        """Setup mocked ChannelTxCreator."""
        def _(response_code, tx_hash=TX_RESULT_HASH):
            channel_tx_creator_stub = create_channel_tx_creator_stub(response_code=response_code, tx_hash=tx_hash)
            StubCollection().channel_tx_creator_stubs[CHANNEL_NAME] = channel_tx_creator_stub

        return _

    @pytest.fixture
    def mock_channel(self):
        def _(response_code):
            channel_stub = create_channel_stub(response_code=response_code)
            StubCollection().channel_stubs[CHANNEL_NAME] = channel_stub

        return _
