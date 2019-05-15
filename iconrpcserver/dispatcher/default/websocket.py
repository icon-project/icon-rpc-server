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
from jsonrpcclient.request import Request
from jsonrpcserver.aio import AsyncMethods

from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey
from iconrpcserver.utils.json_rpc import get_channel_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from iconrpcserver.utils import get_now_timestamp

methods = AsyncMethods()
ws_methods = AsyncMethods()


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

        await WSDispatcher.channel_register(ws, channel_name, peer_id, remote_target)

        futures = [
            WSDispatcher.publish_heartbeat(ws, channel_name, peer_id),
            WSDispatcher.publish_new_block(ws, channel_name, height)
        ]

        try:
            await asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)
        finally:
            await WSDispatcher.channel_unregister(ws, channel_name, peer_id)

    @staticmethod
    async def channel_register(ws, channel_name: str, peer_id: str, remote_target: str):
        channel_stub = get_channel_stub_by_channel_name(channel_name)
        connected_time = get_now_timestamp()
        approved = await channel_stub.async_task().register_citizen(
            peer_id=peer_id,
            target=remote_target,
            connected_time=connected_time
        )

        if not approved:
            raise RuntimeError("This peer can no longer take more subscribe requests.")

        Logger.debug(f"register citizen: {peer_id}")

    @staticmethod
    async def channel_unregister(ws, channel_name: str, peer_id: str):
        channel_stub = get_channel_stub_by_channel_name(channel_name)
        await channel_stub.async_task().unregister_citizen(peer_id=peer_id)

        Logger.debug(f"unregister citizen: {peer_id}")

    @staticmethod
    async def publish_heartbeat(ws, channel_name, peer_id):
        async def _publish_heartbeat():
            channel_stub = get_channel_stub_by_channel_name(channel_name)
            exception = None
            while ws.open:
                try:
                    is_registered = await channel_stub.async_task().is_citizen_registered(peer_id=peer_id)
                    if is_registered:
                        request = Request("node_ws_PublishHeartbeat")
                        await ws.send(json.dumps(request))
                        heartbeat_time = StubCollection().conf[ConfigKey.WS_HEARTBEAT_TIME]
                        await asyncio.sleep(heartbeat_time)
                        continue

                    raise RuntimeError("Unregistered")

                except Exception as e:
                    exception = e
                    traceback.print_exc()
                    break

            if not exception:
                exception = ConnectionError("Connection closed.")

            request = Request("node_ws_PublishHeartbeat",
                              error=str(exception))
            await ws.send(json.dumps(request))
            raise exception

        await asyncio.ensure_future(_publish_heartbeat())

    @staticmethod
    async def publish_new_block(ws, channel_name, height):
        async def _publish_new_block():
            nonlocal height

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
            except Exception as e:
                traceback.print_exc()
                raise e

        await asyncio.ensure_future(_publish_new_block())
