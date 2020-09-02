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

import json
from typing import TYPE_CHECKING, Union

from iconcommons.logger import Logger
from jsonrpcserver import async_dispatch
from jsonrpcserver.methods import Methods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey, DISPATCH_V3D_TAG
from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher import validate_jsonschema_v3
from iconrpcserver.utils.icon_service import response_to_json_query
from iconrpcserver.utils.icon_service.converter import make_request
from iconrpcserver.utils.json_rpc import get_icon_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

if TYPE_CHECKING:
    from sanic.request import Request as SanicRequest
    from jsonrpcserver.response import Response, DictResponse, BatchResponse

methods = Methods()


class Version3DebugDispatcher:
    """
    JSON RPC Debug dispatcher version 3.
    It is used for accessing to only citizen node.
    """
    @staticmethod
    async def dispatch(request: 'SanicRequest', channel_name=None):
        req_json = request.json
        url = request.url
        channel = (channel_name if channel_name is not None
                   else StubCollection().conf[ConfigKey.CHANNEL])

        context = {
            "url": url,
            "channel": channel,
        }

        response: Union[Response, DictResponse, BatchResponse]
        try:
            client_ip = request.remote_addr if request.remote_addr else request.ip
            Logger.info(f'rest_server_v3d request with {req_json}', DISPATCH_V3D_TAG)
            Logger.info(f"{client_ip} requested {req_json} on {url}")

            validate_jsonschema_v3(request=req_json)
        except GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, id=req_json.get('id', 0), debug=False)
        except Exception as e:
            response = ExceptionResponse(e, id=req_json.get('id', 0), debug=False)
        else:
            response = await async_dispatch(request.body, methods, context=context)
        Logger.info(f'rest_server_v3d with response {response}', DISPATCH_V3D_TAG)
        return sanic_response.json(response.deserialized(), status=response.http_status, dumps=json.dumps)

    @staticmethod
    @methods.add
    async def debug_estimateStep(context, **kwargs):
        channel = context.get('channel')
        method = 'debug_estimateStep'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def debug_getAccount(context, **kwargs):
        channel = context.get('channel')
        method = "debug_getAccount"
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        return response_to_json_query(response)
