"""json rpc dispatcher version 3"""

import json
from typing import TYPE_CHECKING, Union

from iconcommons.logger import Logger
from jsonrpcserver import async_dispatch
from jsonrpcserver.methods import Methods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey
from iconrpcserver.default_conf.icon_rpcserver_constant import DISPATCH_V3_TAG
from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher import validate_jsonschema_v3
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

if TYPE_CHECKING:
    from sanic.request import Request as SanicRequest
    from jsonrpcserver.response import Response, DictResponse, BatchResponse

methods = Methods()


class Version3Dispatcher:
    @staticmethod
    async def dispatch(request: 'SanicRequest', channel_name: str = None):
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
            Logger.info(f'rest_server_v3 request with {req_json}', DISPATCH_V3_TAG)
            Logger.info(f"{client_ip} requested {req_json} on {url}")

            validate_jsonschema_v3(request=req_json)
        except GenericJsonRpcServerError as e:
            response = ExceptionResponse(e, id=req_json.get('id', 0), debug=False)
        except Exception as e:
            response = ExceptionResponse(e, id=req_json.get('id', 0), debug=False)
        else:
            response = await async_dispatch(request.body, methods, context=context)
        Logger.info(f'rest_server_v3 with response {response}', DISPATCH_V3_TAG)
        return sanic_response.json(response.deserialized(), status=response.http_status, dumps=json.dumps)
