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
            "required": ["version", "from", "to", "timestamp"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

SCHEMA_V3_DEBUG: dict = {
    "debug_estimateStep": debug_estimateStep_v3
}

validate_jsonschema_v3d = partial(validate_jsonschema, schemas=SCHEMA_V3_DEBUG)
