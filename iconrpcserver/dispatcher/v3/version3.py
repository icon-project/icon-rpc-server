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

from iconcommons.logger import Logger
from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey
from iconrpcserver.default_conf.icon_rpcserver_constant import DISPATCH_V3_TAG
from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher import validate_jsonschema_v3
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from jsonrpcserver import config
from jsonrpcserver import async_dispatch
from jsonrpcserver.methods import Methods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

config.log_requests = False
config.log_responses = False

methods = Methods()


class Version3Dispatcher:
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
        except GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        except Exception as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        else:
            response = await async_dispatch(req_json, methods, context=context)
        Logger.info(f'rest_server_v3 with response {response}', DISPATCH_V3_TAG)
        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)
