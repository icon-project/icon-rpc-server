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
import logging
from typing import Tuple

import aiohttp
from iconcommons.logger import Logger
from jsonrpcclient import exceptions, Response
from jsonrpcclient.clients.aiohttp_client import AiohttpClient
from jsonrpcserver import status

from . import message_code
from ..default_conf.icon_rpcserver_constant import ConfigKey, ApiVersion
from ..dispatcher import GenericJsonRpcServerError, JsonError
from ..utils.icon_service.converter import convert_params
from ..utils.icon_service.templates import ResponseParamType
from ..utils.message_queue.stub_collection import StubCollection


class NewAiohttpClient(AiohttpClient):
    def validate_response(self, response: Response):
        if response.raw is not None and not 200 <= response.raw.status <= 299:
            try:
                data: dict = json.loads(response.text)
                error = data["error"]
                code = int(error["code"])
                message = error["message"]
            except Exception as e:
                code = JsonError.INTERNAL_ERROR
                message = f"ServerError: {response.text}"
            raise GenericJsonRpcServerError(
                code=code,
                message=message,
                http_status=status.HTTP_BAD_REQUEST
            )


async def relay_tx_request(relay_target, message, path, version=ApiVersion.v3.name):
    method_name = "icx_sendTransaction"

    relay_uri = f"{relay_target}/{path}"
    Logger.debug(f'relay_uri: {relay_uri}')

    async with aiohttp.ClientSession() as session:
        Logger.info(f"relay_tx_request : "
                    f"message[{message}], "
                    f"relay_target[{relay_target}], "
                    f"version[{version}], "
                    f"method[{method_name}]")
        try:
            response = await NewAiohttpClient(session, relay_uri, timeout=10).request(method_name, **message)
        except exceptions.ReceivedNon2xxResponseError as e:
            raise GenericJsonRpcServerError(
                code=JsonError.INTERNAL_ERROR,
                message=str(e),
                http_status=status.HTTP_BAD_REQUEST
            ) from e

        if isinstance(response.data, list):
            raise NotImplementedError(f"Received batch response. Data: {response.data}")
        else:
            result = response.data.result
            Logger.debug(f"relay_tx_request result[{result}]")

    return result


async def get_block_v2_by_params(block_height=None, block_hash="", with_commit_state=False):
    channel_name = StubCollection().conf[ConfigKey.CHANNEL]
    channel_stub = StubCollection().channel_stubs[channel_name]
    response_code, block_hash, block_data_json = \
        await channel_stub.async_task().get_block_v2(
            block_height=block_height,
            block_hash=block_hash
        )
    block = json.loads(block_data_json)  # if fail, block = {}

    if block:
        block = convert_params(block, ResponseParamType.get_block_v0_1a_tx_v2)

    result = {
        'response_code': response_code,
        'block': block
    }

    if 'commit_state' in result['block'] and not with_commit_state:
        del result['block']['commit_state']

    return block_hash, result


async def get_block_by_params(
        channel_name=None,
        block_height=None,
        block_hash="",
        with_commit_state=False
):
    channel_name = StubCollection().conf[ConfigKey.CHANNEL] if channel_name is None else channel_name

    try:
        channel_stub = get_channel_stub_by_channel_name(channel_name)
    except KeyError:
        raise GenericJsonRpcServerError(
            code=JsonError.INVALID_REQUEST,
            message="Invalid channel name",
            http_status=status.HTTP_BAD_REQUEST
        )

    response_code, block_hash, confirm_info, block_data_json = \
        await channel_stub.async_task().get_block(
            block_height=block_height,
            block_hash=block_hash
        )

    try:
        block = json.loads(block_data_json) if response_code == message_code.Response.success else {}
    except Exception as e:
        logging.error(f"get_block_by_params error caused by : {e}")
        block = {}

    result = {
        'response_code': response_code,
        'block': block,
        'confirm_info': confirm_info.decode('utf-8')
    }

    if 'commit_state' in result['block'] and not with_commit_state:
        del result['block']['commit_state']

    return block_hash, result


async def get_block_recipts_by_params(
        channel_name: str = None,
        block_height: int = None,
        block_hash: str = ""
) -> Tuple[int, list]:
    channel_name = StubCollection().conf[ConfigKey.CHANNEL] if channel_name is None else channel_name

    try:
        channel_stub = get_channel_stub_by_channel_name(channel_name)
    except KeyError:
        raise GenericJsonRpcServerError(
            code=JsonError.INVALID_REQUEST,
            message="Invalid channel name",
            http_status=status.HTTP_BAD_REQUEST
        )

    response_code, block_receipts = \
        await channel_stub.async_task().get_block_receipts(
            block_height=block_height,
            block_hash=block_hash
        )

    try:
        block_receipts: list = json.loads(block_receipts)
    except Exception as e:
        logging.error(f"get_block_receipts_by_params error caused by : {e}")
        block_receipts: list = []

    return response_code, block_receipts


def get_icon_stub_by_channel_name(channel_name):
    try:
        icon_stub = StubCollection().icon_score_stubs[channel_name]
    except KeyError:
        raise GenericJsonRpcServerError(
            code=JsonError.INVALID_REQUEST,
            message="Invalid channel name",
            http_status=status.HTTP_BAD_REQUEST
        )
    else:
        return icon_stub


def get_channel_stub_by_channel_name(channel_name):
    try:
        channel_stub = StubCollection().channel_stubs[channel_name]
    except KeyError:
        raise GenericJsonRpcServerError(
            code=JsonError.INVALID_REQUEST,
            message="Invalid channel name",
            http_status=status.HTTP_BAD_REQUEST
        )
    else:
        return channel_stub


def monkey_patch():
    from typing import Optional, Union, Dict
    from jsonrpcserver import dispatcher, log

    def _patched_log_(
            message: Union[str, bytes, bytearray],
            logger: logging.Logger,
            level: int = logging.INFO,
            extra: Optional[Dict] = None,
            trim: bool = False,
    ) -> None:
        """
        Log a request or response

        Args:
            message: JSON-RPC request or response string.
            logger:
            level: Log level.
            extra: More details to include in the log entry.
            trim: Abbreviate log messages.
        """
        if extra is None:
            extra = {}
        # Clean up the message for logging
        if message:
            if isinstance(message, (bytes, bytearray)):
                message = message.replace(b"\n", b"").replace(b"  ", b" ").replace(b"{ ", b"{")
            else:
                message = message.replace("\n", "").replace("  ", " ").replace("{ ", "{")
        if trim:
            message = log._trim_message(message)

        # Log.
        logger.log(level, message, extra=extra)

    dispatcher.log_ = _patched_log_
