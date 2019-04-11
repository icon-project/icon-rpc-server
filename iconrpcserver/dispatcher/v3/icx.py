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
from urllib.parse import urlsplit, urlparse

from iconcommons.logger import Logger
from jsonrpcserver import status

from iconrpcserver.dispatcher import GenericJsonRpcServerError, JsonError
from iconrpcserver.server.rest_property import RestProperty
from iconrpcserver.protos import message_code
from iconrpcserver.dispatcher.v3 import methods
from iconrpcserver.utils.icon_service import make_request, response_to_json_query, ParamType, convert_params
from iconrpcserver.utils.json_rpc import relay_tx_request, get_block_by_params, get_icon_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from iconrpcserver.default_conf.icon_rpcserver_constant import NodeType, ConfigKey


class IcxDispatcher:
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
            dispatch_protocol = IcxDispatcher.get_dispatch_protocol_from_url(url)
            Logger.debug(f'Dispatch Protocol: {dispatch_protocol}')
            redirect_protocol = StubCollection().conf.get(ConfigKey.REDIRECT_PROTOCOL)
            Logger.debug(f'Redirect Protocol: {redirect_protocol}')
            if redirect_protocol:
                dispatch_protocol = redirect_protocol
            Logger.debug(f'Protocol: {dispatch_protocol}')

            relay_target = RestProperty().relay_target
            relay_target = relay_target if relay_target is not None else RestProperty().rs_target

            return await relay_tx_request(dispatch_protocol, kwargs, relay_target, path=path[1:])

        method = 'icx_sendTransaction'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        icon_stub = score_stub
        response = await icon_stub.async_task().validate_transaction(request)
        # Error Check
        response_to_json_query(response)

        channel_tx_creator_stub = StubCollection().channel_tx_creator_stubs[channel]
        response_code, tx_hash = await channel_tx_creator_stub.async_task().create_icx_tx(kwargs)

        if response_code != message_code.Response.success:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_REQUEST,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )

        if tx_hash is None:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_REQUEST,
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
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )
        elif response_code == message_code.Response.fail_invalid_key_error or \
                response_code == message_code.Response.fail:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
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
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
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
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
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
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )

        response = convert_params(result['block'], ParamType.get_block_response)
        return response

    @staticmethod
    @methods.add
    async def icx_getLastTransaction(**kwargs):

        return ""
