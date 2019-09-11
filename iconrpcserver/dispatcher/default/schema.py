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

validate_jsonschema_node = partial(validate_jsonschema, schema=SCHEMA_NODE)
