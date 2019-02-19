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

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey, DISPATCH_V3REP_TAG
from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher import validate_jsonschema_v3
from iconrpcserver.utils.icon_service import response_to_json_query
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

config.log_requests = False
config.log_responses = False

methods = AsyncMethods()


class Version3RepDispatcher:
    """JSON RPC Rep dispatcher version 3.
    It is used for getting Rep information of ICON node.

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
            Logger.info(f'rest_server_v3rep request with {req_json}', DISPATCH_V3REP_TAG)
            Logger.info(f"{client_ip} requested {req_json} on {url}")

            validate_jsonschema_v3(request=req_json)
        except GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        except Exception as e:
            response = ExceptionResponse(e, request_id=req_json.get('id', 0))
        else:
            response = await methods.dispatch(req_json, context=context)
        Logger.info(f'rest_server_v3rep with response {response}', DISPATCH_V3REP_TAG)
        return sanic_response.json(response, status=response.http_status, dumps=json.dumps)

    @staticmethod
    @methods.add
    async def rep_getList(**kwargs):
        channel = kwargs['context']['channel']
        channel_infos = await StubCollection().peer_stub.async_task().get_channel_infos()
        channel_infos_by_channel = channel_infos.get(channel)

        rep_list = [{'id': peer['id']} for peer in channel_infos_by_channel['peers']]
        Logger.debug(f'rep list: {rep_list}')

        start_term_height = '0x0'
        end_term_height = '0x0'
        rep_root_hash = None
        # term_height, rep_root_hash should be updated after IISS is implemented.
        response = {
            'startTermHeight': start_term_height,
            'endTermHeight': end_term_height,
            'repRootHash': rep_root_hash,
            'rep': rep_list
        }
        return response_to_json_query(response)
