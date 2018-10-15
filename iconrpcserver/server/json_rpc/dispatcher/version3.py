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
from urllib.parse import urlsplit, urlparse

from iconcommons.logger import Logger
from jsonrpcserver import config, status
from jsonrpcserver.aio import AsyncMethods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

from ...json_rpc import exception
from ...rest_server import RestProperty
from ....default_conf.icon_rpcserver_constant import DISPATCH_V3_TAG
from ....protos import message_code
from ....server.json_rpc.validator import validate_jsonschema_v3
from ....utils.icon_service import make_request, response_to_json_query, ParamType, convert_params
from ....utils.json_rpc import redirect_request_to_rs, get_block_by_params, get_icon_stub_by_channel_name, \
    get_channel_stub_by_channel_name
from ....utils.message_queue.stub_collection import StubCollection
from ....default_conf.icon_rpcserver_constant import NodeType, ConfigKey

config.log_requests = False
config.log_responses = False

methods = AsyncMethods()


class Version3Dispatcher:
    HASH_KEY_DICT = ['hash', 'blockHash', 'txHash', 'prevBlockHash']

    @staticmethod
    async def dispatch(request, channel_name=None):
        req_json = request.json
        url = request.url
        channel = channel_name if channel_name is not None \
            else StubCollection().conf[ConfigKey.CHANNEL]

        context = {
            "url": url,
            "channel": channel,
        }

        try:
            client_ip = request.remote_addr if request.remote_addr else request.ip
            Logger.info(f'rest_server_v3 request with {req_json}', DISPATCH_V3_TAG)
            Logger.info(f"{client_ip} requested {req_json} on {url}")

            validate_jsonschema_v3(request=req_json)
        except exception.GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        except Exception as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        else:
            response = await methods.dispatch(req_json, context=context)
        Logger.info(f'rest_server_v3 with response {response}', DISPATCH_V3_TAG)
        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)

    @staticmethod
    def get_dispatch_protocol_from_url(url: str) -> str:
        return urlsplit(url).scheme

    @staticmethod
    @methods.add
    async def icx_call(**kwargs):
        channel = kwargs['context']['channel']
        method = 'icx_call'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getScoreApi(**kwargs):
        channel = kwargs['context']['channel']
        method = 'icx_getScoreApi'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_sendTransaction(**kwargs):
        channel = kwargs['context']['channel']
        url = kwargs['context']['url']
        path = urlparse(url).path
        del kwargs['context']

        if RestProperty().node_type == NodeType.CitizenNode:
            dispatch_protocol = Version3Dispatcher.get_dispatch_protocol_from_url(url)
            Logger.debug(f'Dispatch Protocol: {dispatch_protocol}')
            redirect_protocol = StubCollection().conf.get(ConfigKey.REDIRECT_PROTOCOL)
            Logger.debug(f'Redirect Protocol: {redirect_protocol}')
            if redirect_protocol:
                dispatch_protocol = redirect_protocol
            Logger.debug(f'Protocol: {dispatch_protocol}')

            return await redirect_request_to_rs(dispatch_protocol,
                                                kwargs, RestProperty().rs_target, path=path[1:])

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
        channel = kwargs['context']['channel']
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
        channel = kwargs['context']['channel']
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
        channel = kwargs['context']['channel']
        method = 'icx_getBalance'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**kwargs):
        channel = kwargs['context']['channel']

        method = 'icx_getTotalSupply'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getLastBlock(**kwargs):
        channel = kwargs['context']['channel']

        block_hash, result = await get_block_by_params(block_height=-1,
                                                       channel_name=channel)
        response = convert_params(result['block'], ParamType.get_block_response)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getBlockByHash(**kwargs):
        channel = kwargs['context']['channel']
        request = convert_params(kwargs, ParamType.get_block_by_hash_request)
        block_hash, result = await get_block_by_params(block_hash=request['hash'],
                                                       channel_name=channel)

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
        channel = kwargs['context']['channel']
        request = convert_params(kwargs, ParamType.get_block_by_height_request)
        block_hash, result = await get_block_by_params(block_height=request['height'],
                                                       channel_name=channel)
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
        channel = kwargs['context']['channel']
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
