"""json rpc dispatcher version 3"""

import json
from typing import Dict
from urllib.parse import urlparse

from iconcommons.logger import Logger
from jsonrpcserver import status

from iconrpcserver.dispatcher import GenericJsonRpcServerError, JsonError
from iconrpcserver.dispatcher.v3 import methods, ConfigKey
from iconrpcserver.utils import message_code
from iconrpcserver.utils.icon_service import (response_to_json_query,
                                              RequestParamType, ResponseParamType)
from iconrpcserver.utils.icon_service.converter import convert_params, make_request
from iconrpcserver.utils.json_rpc import (get_icon_stub_by_channel_name, get_channel_stub_by_channel_name,
                                          relay_tx_request, get_block_by_params, get_block_recipts_by_params)
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

BLOCK_v0_1a = '0.1a'
BLOCK_v0_3 = '0.3'


def check_response_code(response_code: message_code.Response):
    if response_code != message_code.Response.success:
        raise GenericJsonRpcServerError(
            code=JsonError.INVALID_PARAMS,
            message=message_code.responseCodeMap[response_code][1],
            http_status=status.HTTP_BAD_REQUEST
        )


class IcxDispatcher:
    @staticmethod
    @methods.add
    async def icx_call(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        method = 'icx_call'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getScoreApi(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        method = 'icx_getScoreApi'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    async def __relay_icx_transaction(path, message: dict, relay_target):
        if not relay_target:
            raise GenericJsonRpcServerError(
                code=JsonError.INTERNAL_ERROR,
                message=message_code.responseCodeMap[message_code.Response.fail_invalid_peer_target][1],
                http_status=status.HTTP_INTERNAL_ERROR
            )

        return await relay_tx_request(relay_target, message, path=path[1:])

    @staticmethod
    @methods.add
    async def icx_sendTransaction(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        url = context.get('url')

        path = urlparse(url).path

        method = 'icx_sendTransaction'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        icon_stub = score_stub
        response = await icon_stub.async_task().validate_transaction(request)
        # Error Check
        response_to_json_query(response)

        # DosGuard
        if StubCollection().conf.get(ConfigKey.DOS_GUARD_ENABLE, False):
            response = await icon_stub.async_task().dos_guard(kwargs)
            # Error Check
            response_to_json_query(response)

        channel_tx_creator_stub = StubCollection().channel_tx_creator_stubs[channel]
        response_code, tx_hash, relay_target = \
            await channel_tx_creator_stub.async_task().create_icx_tx(kwargs)

        if response_code == message_code.Response.fail_no_permission:
            return await IcxDispatcher.__relay_icx_transaction(path, kwargs, relay_target)

        if response_code != message_code.Response.success:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_REQUEST,
                message=message_code.responseCodeMap[response_code][1],
                http_status=message_code.get_response_http_status_code(response_code, status.HTTP_BAD_REQUEST)
            )

        if tx_hash is None:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_REQUEST,
                message='txHash is None',
                http_status=status.HTTP_BAD_REQUEST
            )

        return convert_params(tx_hash, ResponseParamType.send_tx)

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        request = convert_params(kwargs, RequestParamType.get_tx_result)
        channel_stub = StubCollection().channel_stubs[channel]
        verify_result = dict()

        tx_hash = request["txHash"]
        response_code, result = await channel_stub.async_task().get_invoke_result(tx_hash)

        if response_code == message_code.Response.fail_tx_not_invoked:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
                message=message_code.responseCodeMap[response_code][1],
                http_status=status.HTTP_BAD_REQUEST
            )
        elif response_code == message_code.Response.fail_invalid_key_error or \
                response_code == message_code.Response.fail:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
                message='Invalid params txHash',
                http_status=status.HTTP_BAD_REQUEST
            )

        if result:
            try:
                result_dict = json.loads(result)
                verify_result = result_dict
            except json.JSONDecodeError as e:
                Logger.warning(f"your result is not json, result({result}), {e}")

        response = convert_params(verify_result, ResponseParamType.get_tx_result)
        return response

    @staticmethod
    @methods.add
    async def icx_getTransactionByHash(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        request = convert_params(kwargs, RequestParamType.get_tx_result)
        channel_stub = StubCollection().channel_stubs[channel]

        response_code, tx_info = await channel_stub.async_task().get_tx_info(request["txHash"])
        if response_code == message_code.Response.fail_invalid_key_error:
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
                message='Invalid params txHash',
                http_status=status.HTTP_BAD_REQUEST
            )

        result = tx_info["transaction"]
        result['txHash'] = request['txHash']
        result["txIndex"] = tx_info["tx_index"]
        result["blockHeight"] = tx_info["block_height"]
        result["blockHash"] = tx_info["block_hash"]

        response = convert_params(result, ResponseParamType.get_tx_by_hash)
        return response

    @staticmethod
    @methods.add
    async def icx_getBalance(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        method = 'icx_getBalance'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(context: Dict[str, str], **kwargs):
        channel = context.get('channel')

        method = 'icx_getTotalSupply'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getBlock(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        request = convert_params(kwargs, RequestParamType.get_block)
        if all(param in request for param in ["hash", "height"]):
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
                message='Invalid params (only one parameter is allowed)',
                http_status=status.HTTP_BAD_REQUEST
            )
        if 'hash' in request:
            block_hash, result = await get_block_by_params(block_hash=request['hash'],
                                                           channel_name=channel)
        elif 'height' in request:
            block_hash, result = await get_block_by_params(block_height=request['height'],
                                                           channel_name=channel)
        else:
            block_hash, result = await get_block_by_params(block_height=-1,
                                                           channel_name=channel)

        response_code = result['response_code']
        check_response_code(response_code)

        block = result['block']
        if block['version'] == BLOCK_v0_1a:
            response = convert_params(result['block'], ResponseParamType.get_block_v0_1a_tx_v3)
        elif block['version'] == BLOCK_v0_3:
            response = convert_params(result['block'], ResponseParamType.get_block_v0_3_tx_v3)
        else:
            response = block
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getLastBlock(context: Dict[str, str], **kwargs):
        channel = context.get('channel')

        block_hash, result = await get_block_by_params(block_height=-1,
                                                       channel_name=channel)
        response = convert_params(result['block'], ResponseParamType.get_block_v0_1a_tx_v3)

        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getBlockByHash(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        request = convert_params(kwargs, RequestParamType.get_block_by_hash)
        block_hash, result = await get_block_by_params(block_hash=request['hash'],
                                                       channel_name=channel)

        response_code = result['response_code']
        check_response_code(response_code)

        response = convert_params(result['block'], ResponseParamType.get_block_v0_1a_tx_v3)
        return response

    @staticmethod
    @methods.add
    async def icx_getBlockByHeight(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        request = convert_params(kwargs, RequestParamType.get_block_by_height)

        block_hash, result = await get_block_by_params(block_height=request['height'],
                                                       channel_name=channel)
        response_code = result['response_code']
        check_response_code(response_code)

        response = convert_params(result['block'], ResponseParamType.get_block_v0_1a_tx_v3)
        return response

    @staticmethod
    @methods.add
    async def icx_getTransactionProof(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        channel_stub = get_channel_stub_by_channel_name(channel)

        tx_hash = kwargs['txHash']
        response = await channel_stub.async_task().get_tx_proof(tx_hash)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getReceiptProof(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        channel_stub = get_channel_stub_by_channel_name(channel)

        tx_hash = kwargs['txHash']
        response = await channel_stub.async_task().get_receipt_proof(tx_hash)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_proveTransaction(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        channel_stub = get_channel_stub_by_channel_name(channel)

        tx_hash = kwargs['txHash']
        proof = kwargs['proof']
        response = await channel_stub.async_task().prove_tx(tx_hash, proof)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_proveReceipt(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        channel_stub = get_channel_stub_by_channel_name(channel)

        tx_hash = kwargs['txHash']
        proof = kwargs['proof']
        response = await channel_stub.async_task().prove_receipt(tx_hash, proof)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getBlockReceipts(context: Dict[str, str], **kwargs):
        channel = context.get('channel')
        request = convert_params(kwargs, RequestParamType.get_block_receipts)
        if all(param in request for param in ["hash", "height"]):
            raise GenericJsonRpcServerError(
                code=JsonError.INVALID_PARAMS,
                message='Invalid params (only one parameter is allowed)',
                http_status=status.HTTP_BAD_REQUEST
            )
        if 'hash' in request:
            code, block_receipts = await get_block_recipts_by_params(
                block_hash=request['hash'],
                channel_name=channel
            )
        elif 'height' in request:
            code, block_receipts = await get_block_recipts_by_params(
                block_height=request['height'],
                channel_name=channel
            )
        else:
            code, block_receipts = await get_block_recipts_by_params(
                block_height=-1,
                channel_name=channel
            )

        check_response_code(code)
        response = convert_params(block_receipts, ResponseParamType.get_block_receipts)
        return response_to_json_query(response)
