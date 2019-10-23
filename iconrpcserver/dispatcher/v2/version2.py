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
"""json rpc dispatcher"""

import json
import re
from urllib.parse import urlparse

from iconcommons.logger import Logger
from jsonrpcserver import config
from jsonrpcserver.aio import AsyncMethods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey, ApiVersion, DISPATCH_V2_TAG
from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher import validate_jsonschema_v2
from iconrpcserver.protos import message_code
from iconrpcserver.utils import get_protocol_from_uri
from iconrpcserver.utils.icon_service import response_to_json_query, RequestParamType
from iconrpcserver.utils.icon_service.converter import make_request
from iconrpcserver.utils.json_rpc import relay_tx_request, get_block_v2_by_params
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

config.log_requests = False
config.log_responses = False

methods = AsyncMethods()


class Version2Dispatcher:

    @staticmethod
    async def dispatch(request):
        req = request.json
        url = request.url

        context = {
            "url": url
        }

        if "node_" in req["method"]:
            return sanic_response.text("no support method!")

        try:
            client_ip = request.remote_addr if request.remote_addr else request.ip
            Logger.info(f'rest_server_v2 request with {req}', DISPATCH_V2_TAG)
            Logger.info(f"{client_ip} requested {req} on {url}")

            validate_jsonschema_v2(request=req)
        except GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req.get('id', 0))
        else:
            response = await methods.dispatch(req, context=context)
        Logger.info(f'rest_server_v2 response with {response}', DISPATCH_V2_TAG)
        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)

    @staticmethod
    async def __relay_icx_transaction(url, path, message, channel_name, relay_target):
        if not relay_target:
            response_code = message_code.Response.fail_invalid_peer_target
            return {'response_code': response_code,
                    'message': message_code.responseCodeMap[response_code][1],
                    'tx_hash': None}

        dispatch_protocol = get_protocol_from_uri(url)
        Logger.debug(f'Dispatch Protocol: {dispatch_protocol}')
        redirect_protocol = StubCollection().conf.get(ConfigKey.REDIRECT_PROTOCOL)
        Logger.debug(f'Redirect Protocol: {redirect_protocol}')
        if redirect_protocol:
            dispatch_protocol = redirect_protocol
        Logger.debug(f'Protocol: {dispatch_protocol}')

        return await relay_tx_request(dispatch_protocol, message, relay_target, path[1:], ApiVersion.v2.name)

    @staticmethod
    @methods.add
    async def icx_sendTransaction(**kwargs):
        url = kwargs['context']['url']
        path = urlparse(url).path
        del kwargs['context']

        request = make_request("icx_sendTransaction", kwargs, RequestParamType.send_tx)
        channel = StubCollection().conf[ConfigKey.CHANNEL]
        icon_stub = StubCollection().icon_score_stubs[channel]
        response = await icon_stub.async_task().validate_transaction(request)
        # Error Check
        response_to_json_query(response)

        channel_name = StubCollection().conf[ConfigKey.CHANNEL]
        channel_tx_creator_stub = StubCollection().channel_tx_creator_stubs[channel_name]
        response_code, tx_hash, relay_target = \
            await channel_tx_creator_stub.async_task().create_icx_tx(kwargs)

        if response_code == message_code.Response.fail_no_permission:
            return await Version2Dispatcher.__relay_icx_transaction(url, path, kwargs, channel, relay_target)

        response_data = {'response_code': response_code}
        if response_code != message_code.Response.success:
            response_data['message'] = message_code.responseCodeMap[response_code][1]
        else:
            response_data['tx_hash'] = tx_hash

        return response_data

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(**kwargs):
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]
        channel_stub = StubCollection().channel_stubs[channel_name]
        verify_result = {}

        message = None

        tx_hash = kwargs["tx_hash"]
        if is_hex(tx_hash):
            response_code, result = await channel_stub.async_task().get_invoke_result(tx_hash)
            if response_code == message_code.Response.success:
                # loopchain success
                if result:
                    try:
                        # apply tx_result_convert
                        result_dict = json.loads(result)
                        fail_status = bool(result_dict.get('failure'))
                        if fail_status:
                            error_code = message_code.Response.fail_validate_params
                            message = "Invalid transaction hash."
                        else:
                            error_code = message_code.Response.success
                    except Exception as e:
                        error_message = f"your result is not json, result({result}), {e}"
                        Logger.warning(error_message)
                        error_code = message_code.Response.fail_validate_params
                        message = error_message
                else:
                    error_code = message_code.Response.fail_validate_params
                    message = 'tx_result is empty'
            else:
                error_code = message_code.Response.fail_validate_params
                message = "Invalid transaction hash."
        else:
            # fail
            error_code = message_code.Response.fail_validate_params
            message = "response_code is fail"

        # parsing response
        verify_result['response_code'] = str(error_code)
        if error_code == message_code.Response.success:
            verify_result['response'] = {'code': error_code}
        if message:
            verify_result['message'] = message

        return verify_result

    @staticmethod
    @methods.add
    async def icx_getBalance(**kwargs):
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        method = 'icx_getBalance'
        request = make_request(method, kwargs, RequestParamType.get_balance)

        stub = StubCollection().icon_score_stubs[channel_name]
        response = await stub.async_task().query(request)
        return response_to_json_query(response, True)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**kwargs):
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        method = 'icx_getTotalSupply'
        request = make_request(method, kwargs, RequestParamType.get_total_supply)

        stub = StubCollection().icon_score_stubs[channel_name]
        response = await stub.async_task().query(request)
        return response_to_json_query(response, True)

    @staticmethod
    @methods.add
    async def icx_getLastBlock(**kwargs):
        block_hash, response = await get_block_v2_by_params(block_height=-1)
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHash(**kwargs):
        block_hash, response = await get_block_v2_by_params(block_hash=kwargs["hash"])
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHeight(**kwargs):
        try:
            block_height = int(kwargs["height"])
        except Exception as e:
            verify_result = {
                'response_code': message_code.Response.fail_wrong_block_height,
                'message': f"Invalid block height. error: {e}"
            }
            return verify_result

        block_hash, response = await get_block_v2_by_params(block_height=block_height)
        return response

    @staticmethod
    @methods.add
    async def icx_getLastTransaction(**kwargs):
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        return ""

    @staticmethod
    @methods.add
    async def icx_getTransactionByAddress(**kwargs):
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

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
