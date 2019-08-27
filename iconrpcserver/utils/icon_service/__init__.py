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

from enum import Enum
from typing import Any

from jsonrpcserver import status


class ValueType(Enum):
    none = 0
    text = 1
    integer = 2
    integer_str = 3
    hex_number = 4
    hex_0x_number = 5
    hex_hash_number = 6
    hex_0x_hash_number = 7


class RequestParamType(Enum):
    send_tx = 0
    call = 1
    get_balance = 2
    get_score_api = 3
    get_total_supply = 4
    invoke = 5
    write_precommit_state = 6
    remove_precommit_state = 7
    get_block_by_hash = 8
    get_block_by_height = 9
    get_tx_result = 10
    get_reps_by_hash = 11


class ResponseParamType(Enum):
    send_tx = 0
    get_tx_by_hash = 1
    get_tx_result = 2
    get_block_v0_1a_tx_v2 = 3
    get_block_v0_1a_tx_v3 = 4


def check_error_response(result: Any):
    return isinstance(result, dict) and result.get('error')


def response_to_json_query(response, is_convert: bool = False):
    from iconrpcserver.dispatcher import GenericJsonRpcServerError
    if check_error_response(response):
        response = response['error']
        raise GenericJsonRpcServerError(
            code=-abs(response['code']),
            message=response['message'],
            http_status=status.HTTP_BAD_REQUEST
        )
    else:
        if is_convert:
            response = {
                'response': response,
                "response_code": 0
            }

    return response
