# Copyright 2018 ICON Foundation
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

from collections import namedtuple

from . import ValueType, RequestParamType, ResponseParamType

templates = dict()
CHANGE = object()
AddChange = namedtuple("AddChange", "value")
RemoveChange = namedtuple("RemoveChange", "")
ConvertChange = namedtuple("ConvertChange", "key")

# ======== templates for Request =========

templates[RequestParamType.send_tx] = {
    "method": ValueType.text,
    "params": {
        "version": ValueType.text,
        "from": ValueType.none,
        "to": ValueType.none,
        "value": ValueType.hex_0x_number,
        "stepLimit": ValueType.hex_0x_number,
        "timestamp": ValueType.hex_0x_number,
        "nonce": ValueType.hex_0x_number,
        "signature": ValueType.text,
        "dataType": ValueType.text,
        "txHash": ValueType.hex_number,
        CHANGE: {
            "tx_hash": ConvertChange("txHash"),
            "time_stamp": ConvertChange("timestamp")
        }
    },
    "genesisData": ValueType.none
}

templates[RequestParamType.call] = {
    "method": ValueType.text,
    "params": {
        "to": ValueType.none,
        "dataType": ValueType.text,
        "data": {
            "method": ValueType.text,
            "params": {
                "address": ValueType.none
            }
        }
    }
}

templates[RequestParamType.get_balance] = {
    "method": ValueType.text,
    "params": {
        "address": ValueType.none
    }
}

templates[RequestParamType.get_score_api] = templates[RequestParamType.get_balance]

templates[RequestParamType.get_total_supply] = {
    "method": ValueType.text
}

templates[RequestParamType.invoke] = {
    "block": {
        "blockHeight": ValueType.hex_0x_number,
        "blockHash": ValueType.hex_number,
        "timestamp": ValueType.hex_0x_number,
        "prevBlockHash": ValueType.hex_number,
        CHANGE: {
            "block_height": ConvertChange("blockHeight"),
            "block_hash": ConvertChange("blockHash"),
            "time_stamp": ConvertChange("timestamp")
        }
    },
    "transactions": [
        templates[RequestParamType.send_tx]
    ]
}

templates[RequestParamType.write_precommit_state] = {
    "blockHeight": ValueType.hex_0x_number,
    "blockHash": ValueType.hex_number
}

templates[RequestParamType.remove_precommit_state] = templates[RequestParamType.write_precommit_state]

templates[RequestParamType.get_block] = {
    "hash": ValueType.hex_number,
    "height": ValueType.integer
}

templates[RequestParamType.get_block_by_hash] = {
    "hash": ValueType.hex_number
}

templates[RequestParamType.get_block_by_height] = {
    "height": ValueType.integer
}

templates[RequestParamType.get_tx_result] = {
    "txHash": ValueType.hex_number
}

templates[RequestParamType.get_reps_by_hash] = {
    "repsHash": ValueType.hex_0x_hash_number
}

# ======== templates for Response =========

BLOCK_0_1a = {
    CHANGE: {
        "prevHash": ConvertChange("prev_block_hash"),
        "transactionsHash": ConvertChange("merkle_tree_root_hash"),
        "timestamp": ConvertChange("time_stamp"),
        "transactions": ConvertChange("confirmed_transaction_list"),
        "hash": ConvertChange("block_hash"),
        "leader": ConvertChange("peer_id"),
        "nextLeader": ConvertChange("next_leader"),
        "stateHash": RemoveChange(),
        "receiptsHash": RemoveChange(),
        "repsHash": RemoveChange(),
        "nextRepsHash": RemoveChange(),
        "leaderVotesHash": RemoveChange(),
        "prevVotesHash": RemoveChange(),
        "logsBloom": RemoveChange(),
        "leaderVotes": RemoveChange(),
        "prevVotes": RemoveChange()
    },
    "version": ValueType.text,
    "prev_block_hash": ValueType.hex_hash_number,
    "merkle_tree_root_hash": ValueType.hex_hash_number,
    "time_stamp": ValueType.integer,
    "confirmed_transaction_list": None,
    "block_hash": ValueType.hex_hash_number,
    "height": ValueType.integer,
    "peer_id": ValueType.text,
    "signature": ValueType.text,
    "next_leader": ValueType.text
}

BLOCK_0_3 = {
    "transactions": None
}

TX_V2 = [
    {
        CHANGE: {
            "txHash": ConvertChange("tx_hash"),
            "version": RemoveChange(),
            "stepLimit": RemoveChange(),
            "dataType": RemoveChange(),
            "data": RemoveChange(),
            "nid": RemoveChange(),
            "method": AddChange("icx_sendTransaction")
        },
        "timestamp": ValueType.integer_str,
        "tx_hash": ValueType.hex_hash_number
    }
]

TX_V3 = [
    {
        "txHash": ValueType.hex_0x_hash_number
    }
]

templates[ResponseParamType.get_block_v0_1a_tx_v3] = dict(BLOCK_0_1a)
templates[ResponseParamType.get_block_v0_1a_tx_v3]["confirmed_transaction_list"] = TX_V3

templates[ResponseParamType.get_block_v0_1a_tx_v2] = dict(BLOCK_0_1a)
templates[ResponseParamType.get_block_v0_1a_tx_v2]["confirmed_transaction_list"] = TX_V2

templates[ResponseParamType.get_block_v0_3_tx_v3] = dict(BLOCK_0_3)
templates[ResponseParamType.get_block_v0_3_tx_v3]["transactions"] = TX_V3

templates[ResponseParamType.get_tx_result] = {
    "txHash": ValueType.hex_0x_hash_number,
    "blockHash": ValueType.hex_0x_hash_number,
}

templates[ResponseParamType.get_tx_by_hash] = {
    "txHash": ValueType.hex_0x_hash_number,
    "blockHeight": ValueType.hex_0x_number,
    "blockHash": ValueType.hex_0x_hash_number,
    CHANGE: {
        "tx_hash": ConvertChange("txHash")
    }
}

templates[ResponseParamType.send_tx] = ValueType.hex_0x_hash_number

