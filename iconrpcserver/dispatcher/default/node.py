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
# limitations under the License.'

import json
from typing import Dict, List

from iconcommons.logger import Logger
from jsonrpcserver import async_dispatch
from jsonrpcserver.methods import Methods
from jsonrpcserver.response import DictResponse, ExceptionResponse
from sanic import response as sanic_response

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey, DISPATCH_NODE_TAG
from iconrpcserver.dispatcher import GenericJsonRpcServerError, validate_jsonschema_node
from iconrpcserver.utils import convert_upper_camel_method_to_lower_camel
from iconrpcserver.utils.icon_service import RequestParamType
from iconrpcserver.utils.icon_service.converter import convert_params
from iconrpcserver.utils.json_rpc import get_block_by_params, get_channel_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

methods = Methods()


class NodeDispatcher:
    @staticmethod
    async def dispatch(request, channel_name=None):
        req_json = request.json
        url = request.url
        channel = channel_name if channel_name else StubCollection().conf[ConfigKey.CHANNEL]
        req_json['method'] = convert_upper_camel_method_to_lower_camel(req_json['method'])

        if 'params' in req_json and 'message' in req_json['params']:  # this will be removed after update.
            req_json['params'] = req_json['params']['message']

        context = {
            'url': url,
            'channel': channel
        }

        try:
            client_ip = request.remote_addr if request.remote_addr else request.ip
            Logger.info(f'rest_server_node request with {req_json}', DISPATCH_NODE_TAG)
            Logger.info(f'{client_ip} requested {req_json} on {url}')

            validate_jsonschema_node(request=req_json)
        except GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        except Exception as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        else:
            if "params" in req_json:
                req_json["params"]["context"] = context
            else:
                req_json["params"] = {"context": context}
            response: DictResponse = await async_dispatch(json.dumps(req_json), methods)
        Logger.info(f'rest_server_node with response {response}', DISPATCH_NODE_TAG)
        return sanic_response.json(response.deserialized(), status=response.http_status, dumps=json.dumps)

    @staticmethod
    @methods.add
    async def node_getChannelInfos(**kwargs):
        channel_infos = await StubCollection().peer_stub.async_task().get_channel_infos()
        return {"channel_infos": channel_infos}

    @staticmethod
    @methods.add
    async def node_getBlockByHeight(**kwargs):
        channel = kwargs['context']['channel']
        request = convert_params(kwargs, RequestParamType.get_block_by_height)
        block_hash, response = await get_block_by_params(channel_name=channel, block_height=request['height'],
                                                         with_commit_state=True)
        return response

    @staticmethod
    @methods.add
    async def node_getCitizens(**kwargs):
        channel = kwargs['context']['channel']
        channel_stub = get_channel_stub_by_channel_name(channel)
        citizens: List[Dict[str, str]] = await channel_stub.async_task().get_citizens()
        return {
            "citizens": citizens
        }
