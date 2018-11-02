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

from iconcommons.logger import Logger
from jsonrpcserver import config
from jsonrpcserver.aio import AsyncMethods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response


from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher import validate_jsonschema_v3
from iconrpcserver.utils.icon_service import make_request, response_to_json_query
from iconrpcserver.utils.json_rpc import get_icon_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey, DISPATCH_V3D_TAG


config.log_requests = False
config.log_responses = False

methods = AsyncMethods()


class Version3DebugDispatcher:
    """
    JSON RPC Debug dispatcher version 3.
    It is used for accessing to only citizen node.
    """
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
            Logger.info(f'rest_server_v3d request with {req_json}', DISPATCH_V3D_TAG)
            Logger.info(f"{client_ip} requested {req_json} on {url}")

            validate_jsonschema_v3(request=req_json)
        except GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        except Exception as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        else:
            response = await methods.dispatch(req_json, context=context)
        Logger.info(f'rest_server_v3d with response {response}', DISPATCH_V3D_TAG)
        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)

    @staticmethod
    @methods.add
    async def debug_estimateStep(**kwargs):
        channel = kwargs['context']['channel']
        method = 'debug_estimateStep'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        return response_to_json_query(response)
