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

import asyncio
import json
import traceback
from websockets import exceptions

from iconcommons.logger import Logger
from jsonrpcclient.request import Request
from jsonrpcserver.aio import AsyncMethods

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey
from iconrpcserver.protos import message_code
from iconrpcserver.utils.json_rpc import get_channel_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from iconrpcserver.utils import get_now_timestamp

ws_methods = AsyncMethods()


class Reception:
    """ register and unregister citizen by asynccontextmanager in websocket node_ws_Subscribe
    """

    def __init__(self, channel_name: str, peer_id: str, remote_target: str):
        self._peer_id = peer_id
        self._remote_target = remote_target
        self._channel_stub = get_channel_stub_by_channel_name(channel_name)

    async def __aenter__(self):
        connected_time = get_now_timestamp()
        self._registered = await self._channel_stub.async_task().register_citizen(
            peer_id=self._peer_id,
            target=self._remote_target,
            connected_time=connected_time
        )

        if self._registered:
            Logger.debug(f"register citizen: {self._peer_id}")
        else:
            Logger.warning(f"This peer can no longer take more subscribe requests.")

        return self._registered

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._registered:
            Logger.debug(f"unregister citizen: {self._peer_id}")
            await self._channel_stub.async_task().unregister_citizen(peer_id=self._peer_id)


class WSDispatcher:
    @staticmethod
    async def dispatch(request, ws, channel_name=None):
        ip = request.remote_addr or request.ip
        ws_request = json.loads(await ws.recv())
        context = {
            "channel": channel_name,
            "peer_id": ws_request.get("peer_id"),
            "ws": ws,
            "remote_target": f"{ip}:{request.port}"
        }
        await ws_methods.dispatch(ws_request, context=context)

    @staticmethod
    @ws_methods.add
    async def node_ws_Subscribe(**kwargs):
        context = kwargs.pop('context')
        channel_name = context["channel"]
        ws = context["ws"]
        remote_target = context['remote_target']

        height = kwargs['height']
        peer_id = kwargs['peer_id']

        async with Reception(channel_name, peer_id, remote_target) as registered:
            if not registered:
                await WSDispatcher.send_and_raise_exception(
                    ws=ws,
                    method="node_ws_PublishHeartbeat",
                    exception=RuntimeError("Unregistered"),
                    error_code=message_code.Response.fail_subscribe_limit)

            futures = [
                WSDispatcher.publish_heartbeat(ws),
                WSDispatcher.publish_new_block(ws, channel_name, height)
            ]

            await asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)

    @staticmethod
    async def publish_heartbeat(ws):
        exception = None
        while ws.open:
            try:
                request = Request("node_ws_PublishHeartbeat")
                Logger.debug(f"node_ws_PublishHeartbeat: {request}")
                await ws.send(json.dumps(request))
                heartbeat_time = StubCollection().conf[ConfigKey.WS_HEARTBEAT_TIME]
                await asyncio.sleep(heartbeat_time)
            except Exception as e:
                exception = e
                traceback.print_exc()
                break

        if not exception:
            exception = ConnectionError("Connection closed.")

        error_code = message_code.Response.fail_connection_closed
        await WSDispatcher.send_and_raise_exception(ws, "node_ws_PublishHeartbeat", exception, error_code)

    @staticmethod
    async def publish_new_block(ws, channel_name, height):
        exception = None
        error_code = None
        channel_stub = get_channel_stub_by_channel_name(channel_name)
        try:
            while ws.open:
                new_block_dumped, confirm_info_bytes = await \
                    channel_stub.async_task().announce_new_block(subscriber_block_height=height)
                new_block: dict = json.loads(new_block_dumped)
                confirm_info = confirm_info_bytes.decode('utf-8')
                request = Request("node_ws_PublishNewBlock", block=new_block, confirm_info=confirm_info)
                Logger.debug(f"node_ws_PublishNewBlock: {request}")

                await ws.send(json.dumps(request))
                height += 1
        except exceptions.ConnectionClosed as e:
            exception = e
            error_code = message_code.Response.fail_connection_closed
        except Exception as e:
            exception = e
            error_code = message_code.Response.fail_announce_block
            traceback.print_exc()

        if not exception:
            exception = ConnectionError("Connection closed.")

        await WSDispatcher.send_and_raise_exception(ws, "node_ws_PublishNewBlock", exception, error_code)

    @staticmethod
    async def send_and_raise_exception(ws, method, exception, error_code):
        request = Request(method, error=str(exception), code=error_code)
        await ws.send(json.dumps(request))
        raise exception
