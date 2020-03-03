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

from iconcommons.logger import Logger
from jsonrpcclient.requests import Request
from jsonrpcserver import async_dispatch
from jsonrpcserver.methods import Methods
from websockets import exceptions

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey
from iconrpcserver.protos import message_code
from iconrpcserver.utils import get_now_timestamp
from iconrpcserver.utils.json_rpc import get_channel_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

ws_methods = Methods()


class Reception:
    """ register and unregister citizen by asynccontextmanager in websocket node_ws_Subscribe
    """

    def __init__(self, channel_name: str, peer_id: str, remote_target: str):
        self._peer_id = peer_id
        self._remote_target = remote_target
        self._channel_stub = get_channel_stub_by_channel_name(channel_name)

    async def __aenter__(self):
        connected_time = get_now_timestamp()
        try:
            self._registered = await self._channel_stub.async_task().register_citizen(
                peer_id=self._peer_id,
                target=self._remote_target,
                connected_time=connected_time
            )
        except Exception as e:
            Logger.warning(f"{type(e)} during register new citizen, {e}")
            self._registered = False

        if self._registered:
            Logger.debug(f"register citizen: {self._peer_id}")
        else:
            Logger.warning(f"Cannot register this citizen({self._peer_id})")

        return self._registered

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        Logger.debug(f"unregister citizen: {self._peer_id}")
        await self._channel_stub.async_task().unregister_citizen(peer_id=self._peer_id)


class WSDispatcher:
    PUBLISH_HEARTBEAT = "node_ws_PublishHeartbeat"
    PUBLISH_NEW_BLOCK = "node_ws_PublishNewBlock"

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
        await async_dispatch(ws_request, ws_methods, context=context)

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
                return await WSDispatcher.publish_unregister(ws, channel_name, peer_id, force=True)
            else:  # send first heartbeat to let citizen know it's registered
                await WSDispatcher._publish_heartbeat(ws)

            futures = [
                WSDispatcher.publish_heartbeat(ws),
                WSDispatcher.publish_new_block(ws, channel_name, height, peer_id),
                WSDispatcher.publish_unregister(ws, channel_name, peer_id)
            ]
            try:
                await asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)
            except Exception as e:
                pass

    @staticmethod
    async def publish_heartbeat(ws):
        call_method = WSDispatcher.PUBLISH_HEARTBEAT
        try:
            while True:
                await WSDispatcher._publish_heartbeat(ws)
                heartbeat_time = StubCollection().conf[ConfigKey.WS_HEARTBEAT_TIME]
                await asyncio.sleep(heartbeat_time)
        except exceptions.ConnectionClosed:
            Logger.debug("Connection Closed by child.")  # TODO: Useful message needed.
        except Exception as e:
            traceback.print_exc()  # TODO: Keep this tb?
            await WSDispatcher.send_exception(
                ws, call_method,
                exception=e,
                error_code=message_code.Response.fail_connection_closed
            )

    @staticmethod
    async def _publish_heartbeat(ws):
        call_method = WSDispatcher.PUBLISH_HEARTBEAT
        request = Request(call_method)
        Logger.debug(f"{call_method}: {request}")
        await ws.send(json.dumps(request))

    @staticmethod
    async def publish_new_block(ws, channel_name, height, peer_id):
        call_method = WSDispatcher.PUBLISH_NEW_BLOCK
        channel_stub = get_channel_stub_by_channel_name(channel_name)
        try:
            while True:
                new_block_dumped, confirm_info_bytes = await channel_stub.async_task().announce_new_block(
                    subscriber_block_height=height,
                    subscriber_id=peer_id
                )
                new_block: dict = json.loads(new_block_dumped)

                if "error" in new_block:
                    Logger.error(f"announce_new_block error: {new_block}, to citizen({peer_id})")
                    break

                confirm_info = confirm_info_bytes.decode('utf-8')
                request = Request(call_method, block=new_block, confirm_info=confirm_info)
                Logger.debug(f"{call_method}: {request}")

                await ws.send(json.dumps(request))
                height += 1
        except exceptions.ConnectionClosed:
            Logger.debug("Connection Closed by child.")  # TODO: Useful message needed.
        except Exception as e:
            traceback.print_exc()  # TODO: Keep this tb?
            await WSDispatcher.send_exception(
                ws, call_method,
                exception=e,
                error_code=message_code.Response.fail_announce_block
            )

    @staticmethod
    async def publish_unregister(ws, channel_name, peer_id, force: bool = False):
        call_method = WSDispatcher.PUBLISH_HEARTBEAT
        if force:  # unregister due to subscribe limit
            signal = True
            error_code = message_code.Response.fail_subscribe_limit
        else:
            channel_stub = get_channel_stub_by_channel_name(channel_name)
            signal = await channel_stub.async_task().wait_for_unregister_signal(peer_id)
            error_code = message_code.Response.fail_connect_to_leader
        if signal:
            await WSDispatcher.send_exception(
                ws, call_method,
                exception=ConnectionError("Unregistered"),
                error_code=error_code)

    @staticmethod
    async def send_exception(ws, method, exception, error_code):
        request = Request(method, error=str(exception), code=error_code)
        await ws.send(json.dumps(request))
