"""json rpc dispatcher"""

import json
import re
from typing import TYPE_CHECKING, Dict, Union
from urllib.parse import urlparse

from iconcommons.logger import Logger
from jsonrpcserver import async_dispatch
from jsonrpcserver.methods import Methods
from jsonrpcserver.response import ExceptionResponse
from sanic import response as sanic_response

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey, ApiVersion, DISPATCH_V2_TAG
from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher import validate_jsonschema_v2
from iconrpcserver.utils import message_code
from iconrpcserver.utils.icon_service import response_to_json_query, RequestParamType
from iconrpcserver.utils.icon_service.converter import make_request
from iconrpcserver.utils.json_rpc import relay_tx_request, get_block_v2_by_params
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

if TYPE_CHECKING:
    from sanic.request import Request as SanicRequest
    from jsonrpcserver.response import Response, DictResponse, BatchResponse

methods = Methods()


class Version2Dispatcher:

    @staticmethod
    async def dispatch(request: 'SanicRequest'):
        req = request.json
        url = request.url

        context = {
            "url": url
        }

        response: Union[Response, DictResponse, BatchResponse]
        try:
            client_ip = request.remote_addr if request.remote_addr else request.ip
            Logger.info(f'rest_server_v2 request with {req}', DISPATCH_V2_TAG)
            Logger.info(f"{client_ip} requested {req} on {url}")

            validate_jsonschema_v2(request=req)
        except GenericJsonRpcServerError as e:
            Logger.debug(f'dispatch() validate exception = {e}')
            response = ExceptionResponse(e, id=req.get('id', 0), debug=False)
        else:
            response = await async_dispatch(request.body, methods, context=context)

        Logger.info(f'rest_server_v2 response with {response}', DISPATCH_V2_TAG)
        return sanic_response.json(response.deserialized(), status=response.http_status, dumps=json.dumps)

    @staticmethod
    async def __relay_icx_transaction(path, message, relay_target):
        if not relay_target:
            response_code = message_code.Response.fail_invalid_peer_target
            return {'response_code': response_code,
                    'message': message_code.responseCodeMap[response_code][1],
                    'tx_hash': None}

        return await relay_tx_request(relay_target, message, path[1:], ApiVersion.v2.name)

    @staticmethod
    @methods.add
    async def icx_sendTransaction(context: Dict[str, str], **kwargs):
        url = context.get('url')
        path = urlparse(url).path

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
            return await Version2Dispatcher.__relay_icx_transaction(path, kwargs, relay_target)

        response_data = {'response_code': response_code}
        if response_code != message_code.Response.success:
            response_data['message'] = message_code.responseCodeMap[response_code][1]
        else:
            response_data['tx_hash'] = tx_hash

        return response_data

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(context: Dict[str, str], **kwargs):
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
    async def icx_getBalance(context: Dict[str, str], **kwargs):
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        method = 'icx_getBalance'
        request = make_request(method, kwargs, RequestParamType.get_balance)

        stub = StubCollection().icon_score_stubs[channel_name]
        response = await stub.async_task().query(request)
        return response_to_json_query(response, True)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(context: Dict[str, str], **kwargs):
        channel_name = StubCollection().conf[ConfigKey.CHANNEL]

        method = 'icx_getTotalSupply'
        request = make_request(method, kwargs, RequestParamType.get_total_supply)

        stub = StubCollection().icon_score_stubs[channel_name]
        response = await stub.async_task().query(request)
        return response_to_json_query(response, True)

    @staticmethod
    @methods.add
    async def icx_getLastBlock(context: Dict[str, str], **kwargs):
        block_hash, response = await get_block_v2_by_params(block_height=-1)
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHash(context: Dict[str, str], **kwargs):
        block_hash, response = await get_block_v2_by_params(block_hash=kwargs["hash"])
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHeight(context: Dict[str, str], **kwargs):
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
    async def icx_getTransactionByAddress(context: Dict[str, str], **kwargs):
        """
        FIXME : deprecated?

        :param kwargs:
        :return:
        """
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
