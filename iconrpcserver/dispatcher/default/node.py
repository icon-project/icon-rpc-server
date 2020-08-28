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
            response = ExceptionResponse(e, id=req_json.get('id', 0), debug=False)
        except Exception as e:
            response = ExceptionResponse(e, id=req_json.get('id', 0), debug=False)
        else:
            response: DictResponse = await async_dispatch(json.dumps(req_json), methods, context=context)

        Logger.info(f'rest_server_node with response {response}', DISPATCH_NODE_TAG)
        return sanic_response.json(response.deserialized(), status=response.http_status, dumps=json.dumps)

    @staticmethod
    @methods.add
    async def node_getChannelInfos(context: Dict[str, str], **kwargs):
        channel_infos = await StubCollection().peer_stub.async_task().get_channel_infos()
        return {"channel_infos": channel_infos}

    @staticmethod
    @methods.add
    async def node_getBlockByHeight(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        request = convert_params(kwargs, RequestParamType.get_block_by_height)
        block_hash, response = await get_block_by_params(channel_name=channel, block_height=request['height'],
                                                         with_commit_state=True)
        return response

    @staticmethod
    @methods.add
    async def node_getCitizens(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        channel_stub = get_channel_stub_by_channel_name(channel)
        citizens: List[Dict[str, str]] = await channel_stub.async_task().get_citizens()
        return {
            "citizens": citizens
        }
