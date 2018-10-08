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
from urllib.parse import urlsplit

from iconcommons.logger import Logger
from jsonrpcserver import config
from jsonrpcserver.aio import AsyncMethods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

from ...json_rpc import exception
from ...rest_property import RestProperty
from ....default_conf.icon_rpcserver_constant import ConfigKey, NodeType, ApiVersion, DISPATCH_V2_TAG
from ....protos import message_code
from ....server.json_rpc.validator import validate_jsonschema_v2
from ....utils.icon_service import make_request, response_to_json_query, ParamType
from ....utils.json_rpc import redirect_request_to_rs, get_block_v2_by_params
from ....utils.message_queue.stub_collection import StubCollection

config.log_requests = False
config.log_responses = False

methods = AsyncMethods()

JSONRPC_KEY = 'jsonrpc'
METHOD_KEY = 'method'
PARAMS_KEY = 'params'
ID_KEY = 'id'
JSON_KEY = 'json_key'
URL_KEY = 'url_key'


class Version2Dispatcher:

    @staticmethod
    async def dispatch(request):
        req_json = request.json
        url = request.url

        request_dict = {
            JSONRPC_KEY: req_json[JSONRPC_KEY],
            METHOD_KEY: req_json[METHOD_KEY],
            PARAMS_KEY: {
                JSON_KEY: req_json,
                URL_KEY: url
            },
            ID_KEY: req_json[ID_KEY]
        }

        if "node_" in req_json["method"]:
            return sanic_response.text("no support method!")

        try:
            client_ip = request.remote_addr if request.remote_addr else request.ip
            Logger.info(f'rest_server_v2 request with {req_json}', DISPATCH_V2_TAG)
            Logger.info(f"{client_ip} requested {req_json} on {url}")

            validate_jsonschema_v2(request=req_json)
        except exception.GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        else:
            response = await methods.dispatch(request_dict)
        Logger.info(f'rest_server_v2 response with {response}', DISPATCH_V2_TAG)
        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)

    @staticmethod
    def get_dispatch_protocol_from_url(url: str) -> str:
        return urlsplit(url).scheme

    @staticmethod
    @methods.add
    async def icx_sendTransaction(**kwargs):
        origin_params = kwargs[JSON_KEY]
        json_params = origin_params.get(PARAMS_KEY)
        if json_params is None:
            json_params = {}
        url = kwargs[URL_KEY]

        dispatch_protocol = Version2Dispatcher.get_dispatch_protocol_from_url(url)
        Logger.debug(f'Dispatch Protocol: {dispatch_protocol}')

        if RestProperty().node_type == NodeType.CitizenNode:
            return await redirect_request_to_rs(dispatch_protocol,
                                                json_params, RestProperty().rs_target, ApiVersion.v2.name)

        request = make_request("icx_sendTransaction", json_params, ParamType.send_tx)
        channel = StubCollection().conf[ConfigKey.CHANNEL]
        icon_stub = StubCollection().icon_score_stubs[channel]
        response = await icon_stub.async_task().validate_transaction(request)
        # Error Check
        response_to_json_query(response)

        channel_name = StubCollection().conf[ConfigKey.CHANNEL]
        channel_inner_tasks = StubCollection().channel_stubs[channel_name]
        response_code, tx_hash = await channel_inner_tasks.async_task().create_icx_tx(json_params)

        response_data = {'response_code': response_code}
        if response_code != message_code.Response.success:
            response_data['message'] = message_code.responseCodeMap[response_code][1]
        else:
            response_data['tx_hash'] = tx_hash

        return response_data

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(**kwargs):
        origin_params = kwargs[JSON_KEY]
        json_params = origin_params.get(PARAMS_KEY)
        if json_params is None:
            json_params = {}

        channel_name = StubCollection().conf[ConfigKey.CHANNEL]
        channel_stub = StubCollection().channel_stubs[channel_name]
        verify_result = {}

        message = None

        tx_hash = json_params["tx_hash"]
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
        origin_params = kwargs[JSON_KEY]
        json_params = origin_params.get(PARAMS_KEY)
        if json_params is None:
            json_params = {}
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        method = 'icx_getBalance'
        request = make_request(method, json_params, ParamType.get_balance)

        stub = StubCollection().icon_score_stubs[channel_name]
        response = await stub.async_task().query(request)
        return response_to_json_query(response, True)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**kwargs):
        origin_params = kwargs[JSON_KEY]
        json_params = origin_params.get(PARAMS_KEY)
        if json_params is None:
            json_params = {}

        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        method = 'icx_getTotalSupply'
        request = make_request(method, json_params, ParamType.get_total_supply)

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
        origin_params = kwargs[JSON_KEY]
        json_params = origin_params.get(PARAMS_KEY)
        if json_params is None:
            json_params = {}

        block_hash, response = await get_block_v2_by_params(block_hash=json_params["hash"])
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHeight(**kwargs):
        try:
            origin_params = kwargs[JSON_KEY]
            json_params = origin_params.get(PARAMS_KEY)
            if json_params is None:
                json_params = {}

            block_height = int(json_params["height"])
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
        origin_params = kwargs[JSON_KEY]
        json_params = origin_params.get(PARAMS_KEY)
        if json_params is None:
            json_params = {}

        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        address = json_params.get("address", None)
        index = json_params.get("index", None)

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
