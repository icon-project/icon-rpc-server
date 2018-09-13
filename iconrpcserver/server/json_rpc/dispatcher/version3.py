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
"""json rpc dispatcher version 3"""

import json
from typing import Any, Optional

from jsonrpcserver import config, status
from jsonrpcserver.aio import AsyncMethods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

from iconcommons.logger import Logger

from ....server.json_rpc.validator import validate_jsonschema_v3
from ....protos import message_code
from ...rest_server import RestProperty
from ...json_rpc import exception
from ....utils.icon_service import make_request, response_to_json_query, ParamType, convert_params
from ....utils.json_rpc import redirect_request_to_rs, get_block_by_params, get_icon_stub_by_channel_name
from ....utils.message_queue.stub_collection import StubCollection
from ....default_conf.icon_rpcserver_constant import NodeType

config.log_requests = False
config.log_responses = False

methods = AsyncMethods()

REST_SERVER_V3 = 'REST_SERVER_V3'

channel = None


class Version3Dispatcher:
    HASH_KEY_DICT = ['hash', 'blockHash', 'txHash', 'prevBlockHash']

    @staticmethod
    async def dispatch(request, channel_name=None):
        req = request.json
        global channel
        channel = channel_name
        Logger.info(f'rest_server_v3 request with {req}', REST_SERVER_V3)

        try:
            validate_jsonschema_v3(request=req)
        except exception.GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req.get('id', 0))
        else:
            response = await methods.dispatch(req)

        Logger.info(f'rest_server_v3 with response {response}', REST_SERVER_V3)
        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)

    @staticmethod
    @methods.add
    async def icx_call(**kwargs):
        method = 'icx_call'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getScoreApi(**kwargs):
        method = 'icx_getScoreApi'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_sendTransaction(**kwargs):
        if RestProperty().node_type == NodeType.CitizenNode:
            return await redirect_request_to_rs(kwargs, RestProperty().rs_target)

        method = 'icx_sendTransaction'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        icon_stub = score_stub
        response = await icon_stub.async_task().validate_transaction(request)
        # Error Check
        response_to_json_query(response)

        channel_stub = StubCollection().channel_stubs[channel]
        response_code, tx_hash = await channel_stub.async_task().create_icx_tx(kwargs)

        if response_code != message_code.Response.success:
            raise exception.GenericJsonRpcServerError(
                code=exception.JsonError.INVALID_REQUEST,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )

        if tx_hash is None:
            raise exception.GenericJsonRpcServerError(
                code=exception.JsonError.INVALID_REQUEST,
                message='txHash is None',
                http_status=status.HTTP_BAD_REQUEST
            )

        return convert_params(tx_hash, ParamType.send_tx_response)

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(**kwargs):
        request = convert_params(kwargs, ParamType.get_tx_request)
        channel_stub = StubCollection().channel_stubs[channel]
        verify_result = dict()

        tx_hash = request["txHash"]
        response_code, result = await channel_stub.async_task().get_invoke_result(tx_hash)

        if response_code == message_code.Response.fail_tx_not_invoked:
            raise exception.GenericJsonRpcServerError(
                code=exception.JsonError.INVALID_PARAMS,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )
        elif response_code == message_code.Response.fail_invalid_key_error or \
            response_code == message_code.Response.fail:
            raise exception.GenericJsonRpcServerError(
                code=exception.JsonError.INVALID_PARAMS,
                message='Invalid params txHash',
                http_status=status.HTTP_BAD_REQUEST
            )

        if result:
            try:
                result_dict = json.loads(result)
                verify_result = result_dict
            except json.JSONDecodeError as e:
                Logger.warning(f"your result is not json, result({result}), {e}")

        response = convert_params(verify_result, ParamType.get_tx_result_response)
        return response

    @staticmethod
    @methods.add
    async def icx_getTransactionByHash(**kwargs):
        request = convert_params(kwargs, ParamType.get_tx_request)

        channel_stub = StubCollection().channel_stubs[channel]

        response_code, tx_info = await channel_stub.async_task().get_tx_info(request["txHash"])
        if response_code == message_code.Response.fail_invalid_key_error:
            raise exception.GenericJsonRpcServerError(
                code=exception.JsonError.INVALID_PARAMS,
                message='Invalid params txHash',
                http_status=status.HTTP_BAD_REQUEST
            )

        result = tx_info["transaction"]
        result['txHash'] = request['txHash']
        result["txIndex"] = tx_info["tx_index"]
        result["blockHeight"] = tx_info["block_height"]
        result["blockHash"] = tx_info["block_hash"]

        response = convert_params(result, ParamType.get_tx_by_hash_response)
        return response

    @staticmethod
    @methods.add
    async def icx_getBalance(**kwargs):

        method = 'icx_getBalance'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**kwargs):

        method = 'icx_getTotalSupply'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getLastBlock(**kwargs):
        block_hash, result = await get_block_by_params(block_height=-1, channel_name=channel)
        response = convert_params(result['block'], ParamType.get_block_response)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getBlockByHash(**kwargs):
        request = convert_params(kwargs, ParamType.get_block_by_hash_request)
        block_hash, result = await get_block_by_params(block_hash=request['hash'], channel_name=channel)

        response_code = result['response_code']
        if response_code != message_code.Response.success:
            raise exception.GenericJsonRpcServerError(
                code=exception.JsonError.INVALID_PARAMS,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )

        response = convert_params(result['block'], ParamType.get_block_response)
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHeight(**kwargs):
        request = convert_params(kwargs, ParamType.get_block_by_height_request)

        block_hash, result = await get_block_by_params(block_height=request['height'], channel_name=channel)

        response_code = result['response_code']
        if response_code != message_code.Response.success:
            raise exception.GenericJsonRpcServerError(
                code=exception.JsonError.INVALID_PARAMS,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )

        response = convert_params(result['block'], ParamType.get_block_response)
        return response

    @staticmethod
    @methods.add
    async def icx_getLastTransaction(**kwargs):

        return ""

    @staticmethod
    @methods.add
    async def ise_getStatus(**kwargs):

        method = 'ise_getStatus'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        error = response.get('error')
        if error is None:
            Version3Dispatcher._hash_convert(None, response)
        return response_to_json_query(response)

    @staticmethod
    def _hash_convert(key: Optional[str], response: Any):
        if key is None:
            result = response
        else:
            result = response[key]
        if isinstance(result, dict):
            for key in result:
                Version3Dispatcher._hash_convert(key, result)
        elif key in Version3Dispatcher.HASH_KEY_DICT:
            if isinstance(result, str):
                if not result.startswith('0x'):
                    response[key] = f'0x{result}'
