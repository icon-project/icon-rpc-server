# Copyright 2017 theloop Inc.
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
"""json rpc dispatcher"""

import json
import re

from jsonrpcserver import config
from jsonrpcserver.aio import AsyncMethods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

import rest.configure.configure as conf
from ....protos import message_code
from ...rest_property import RestProperty
from ...json_rpc import exception
from ....utils.icon_service import make_request, response_to_json_query, ParamType
from ....utils.json_rpc import redirect_request_to_rs, get_block_by_params
from ....utils.message_queue import StubCollection
from rest.server.json_rpc.validator import validate_jsonschema_v2

from iconservice.logger.logger import Logger

config.log_requests = False
config.log_responses = False

methods = AsyncMethods()


class Version2Dispatcher:
    @staticmethod
    async def dispatch(request):
        req = request.json

        if "node_" in req["method"]:
            return sanic_response.text("no support method!")

        try:
            validate_jsonschema_v2(request=req)
        except exception.GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req.get('id', 0))
        else:
            response = await methods.dispatch(req)

        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)

    @staticmethod
    @methods.add
    async def icx_sendTransaction(**kwargs):
        if RestProperty().node_type == conf.NodeType.CitizenNode:
            return await redirect_request_to_rs(kwargs, RestProperty().rs_target, conf.ApiVersion.v2.name)

        by_citizen = kwargs.get("node_type", False)
        if by_citizen:
            kwargs = kwargs["message"]

        request = make_request("icx_sendTransaction", kwargs, ParamType.send_tx)
        icon_stub = StubCollection().icon_score_stubs[conf.LOOPCHAIN_DEFAULT_CHANNEL]
        response = await icon_stub.async_task().validate_transaction(request)
        response_to_json_query(response)

        channel_inner_tasks = StubCollection().channel_stubs[conf.LOOPCHAIN_DEFAULT_CHANNEL]
        tx_hash = await channel_inner_tasks.async_task().create_icx_tx(kwargs)

        if tx_hash:
            code = message_code.Response.success
            message = tx_hash
        else:
            code = message_code.Response.fail_create_tx
            message = f"tx validate fail. tx data :: {kwargs}"

        response_data = {'response_code': code}

        if code != message_code.Response.success:
            response_data['message'] = message
        else:
            response_data['tx_hash'] = message

        return response_data

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(**kwargs):
        if RestProperty().node_type == conf.NodeType.CitizenNode:
            return await redirect_request_to_rs(kwargs, RestProperty().rs_target, conf.ApiVersion.v2.name)

        by_citizen = kwargs.get("node_type", False)
        if by_citizen:
            kwargs = kwargs["message"]

        channel_name = conf.LOOPCHAIN_DEFAULT_CHANNEL
        channel_stub = StubCollection().channel_stubs[channel_name]
        verify_result = {}

        tx_hash = kwargs["tx_hash"]
        if is_hex(tx_hash):
            response_code, result = await channel_stub.async_task().get_invoke_result(tx_hash)
            verify_result['response_code'] = str(response_code)
            if len(result) is not 0:
                try:
                    result_dict = json.loads(result)
                    verify_result['response'] = result_dict
                except json.JSONDecodeError as e:
                    Logger.warning(f"your result is not json, result({result}), {e}")
            if response_code == message_code.Response.success:
                verify_result['response'] = json.loads(result)
        else:
            verify_result['response_code'] = str(message_code.Response.fail_validate_params)
            verify_result['message'] = "Invalid transaction hash."

        return verify_result

    @staticmethod
    @methods.add
    async def icx_getBalance(**kwargs):
        channel_name = conf.LOOPCHAIN_DEFAULT_CHANNEL

        method = 'icx_getBalance'
        request = make_request(method, kwargs, ParamType.get_balance)

        stub = StubCollection().icon_score_stubs[channel_name]
        response = await stub.async_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**kwargs):
        channel_name = conf.LOOPCHAIN_DEFAULT_CHANNEL

        method = 'icx_getTotalSupply'
        request = make_request(method, kwargs, ParamType.get_total_supply)

        stub = StubCollection().icon_score_stubs[channel_name]
        response = await stub.async_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getLastBlock(**kwargs):
        block_hash, response = await get_block_by_params(block_height=-1)
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHash(**kwargs):
        block_hash, response = await get_block_by_params(block_hash=kwargs["hash"])
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHeight(**kwargs):
        block_hash, response = await get_block_by_params(block_height=int(kwargs["height"]))
        return response

    @staticmethod
    @methods.add
    async def icx_getLastTransaction(**kwargs):
        channel_name = conf.LOOPCHAIN_DEFAULT_CHANNEL

        return ""

    @staticmethod
    @methods.add
    async def icx_getTransactionByAddress(**kwargs):
        channel_name = conf.LOOPCHAIN_DEFAULT_CHANNEL

        address = kwargs.get("address", None)
        index = kwargs.get("index", None)

        if address is None or index is None:
            return {
                'response_code': message_code.Response.fail_illegal_params,
                'message': message_code.get_response_msg(message_code.Response.fail_illegal_params)
            }

        channel_stub = StubCollection().channel_stubs[channel_name]
        tx_list, next_index = await channel_stub.async_task().get_tx_by_address(
            address=address,
            index=index
        )

        response = {
            'next_index': next_index,
            'response': tx_list[:-1],
            'response_code': message_code.Response.success
        }
        return response


def is_hex(s):
    return re.fullmatch(r"^(0x)?[0-9a-f]{64}$", s or "") is not None



"""
### jsonrpc 기반 프로토콜
```
/api/v2 post
{
    "jsonrpc" : "2.0",
    "method": "send_transaction",
    "param": {
        "address" : "icxaa688d74eb5f98b577883ca203535d2aa4f0838c",
        "channl_name": "icon_public",
        "score_id": "icon_foundation/icx",
        "invoke_method": "send",
        "invoke_params": [{
            "a": "b",
            "b": "c"
        }],
        "signature": "FaqqMJexkFm1uUtCa85Ag9UwScWqxI0p7l648L7ZmAJfOEOTaoMB2AYRxz+Ekg22X8gRhwPRwSCB5OcXLrYO+Q==1"
    },
    "id": 1
}
```

### restapi 기반 프로토콜
```
/api/v1/transactions
{
    "address": "icxaa688d74eb5f98b577883ca203535d2aa4f0838c",
    "channel_name": "icon_public",
    "score_id": "icon_foundation/icx",
    "score": {
        "jsonrpc": "2.0",
        "method": "send",
        "params": {
            "a": "b",
            "b": "c"
        },
        "id": 1
    },
    "signature": "FaqqMJexkFm1uUtCa85Ag9UwScWqxI0p7l648L7ZmAJfOEOTaoMB2AYRxz+Ekg22X8gRhwPRwSCB5OcXLrYO+Q==1"
}
```
"""
