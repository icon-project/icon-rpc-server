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
from jsonrpcserver.aio import AsyncMethods
from jsonrpcclient.request import Request
from sanic import response

from iconrpcserver.protos import message_code
from iconrpcserver.utils.icon_service import ParamType, convert_params
from iconrpcserver.utils.json_rpc import get_block_by_params, get_channel_stub_by_channel_name
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey


methods = AsyncMethods()
ws_methods = AsyncMethods()


class NodeDispatcher:
    @staticmethod
    async def dispatch(request, channel_name=None):
        req = json.loads(request.body.decode())
        req["params"] = req.get("params", {})

        if 'message' in req['params']:
            req['params'] = req['params']['message']

        req["params"]["method"] = request.json["method"]

        if "node_" not in req["params"]["method"]:
            return response.text("no support method!")

        context = {
            "channel": channel_name
        }

        dispatch_response = await methods.dispatch(req, context=context)
        return response.json(dispatch_response, status=dispatch_response.http_status)

    @staticmethod
    async def websocket_dispatch(request, ws, channel_name=None):
        request = await ws.recv()
        request = json.loads(request)
        context = {
            "channel": channel_name,
            "peer_id": request.get("peer_id"),
            "ws": ws
        }
        await ws_methods.dispatch(request, context=context)

    @staticmethod
    @methods.add
    async def node_GetChannelInfos(**kwargs):
        channel_infos = await StubCollection().peer_stub.async_task().get_channel_infos()

        channel_infos = {"channel_infos": channel_infos}
        return channel_infos

    @staticmethod
    @methods.add
    async def node_AnnounceConfirmedBlock(**kwargs):
        try:
            channel = kwargs['context']['channel']
            del kwargs['context']
            channel = channel if channel is not None else kwargs['channel']
        except KeyError:
            channel = kwargs['channel']
        block, commit_state = kwargs['block'], kwargs.get('commit_state', "{}")
        channel_stub = get_channel_stub_by_channel_name(channel)
        response_code = await channel_stub.async_task().announce_confirmed_block(block.encode('utf-8'), commit_state)
        return {"response_code": response_code,
                "message": message_code.get_response_msg(response_code)}

    @staticmethod
    @methods.add
    async def node_GetBlockByHeight(**kwargs):
        try:
            channel = kwargs['context']['channel']
            del kwargs['context']
            channel = channel if channel is not None else kwargs.get('channel', None)
        except KeyError:
            channel = kwargs.get("channel", None)
        request = convert_params(kwargs, ParamType.get_block_by_height_request)
        block_hash, response = await get_block_by_params(channel_name=channel, block_height=request['height'],
                                                         with_commit_state=True)
        return response

    @staticmethod
    @ws_methods.add
    async def node_ws_Subscribe(**kwargs):
        context = kwargs.pop('context')
        channel_name = context["channel"]
        ws = context["ws"]

        height = kwargs['height']
        peer_id = kwargs['peer_id']

        await NodeDispatcher.channel_register(ws, channel_name, peer_id)

        futures = [
            NodeDispatcher.publish_heartbeat(ws, channel_name, peer_id),
            NodeDispatcher.publish_new_block(ws, channel_name, height)
        ]

        await asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)
        await NodeDispatcher.channel_unregister(ws, channel_name, peer_id)

    @staticmethod
    async def channel_register(ws, channel_name: str, peer_id: str):
        channel_stub = get_channel_stub_by_channel_name(channel_name)
        approved = await channel_stub.async_task().register_subscriber(peer_id=peer_id)

        if not approved:
            raise RuntimeError("This peer can no longer take more subscribe requests.")

        Logger.debug(f"register subscriber: {peer_id}")

    @staticmethod
    async def channel_unregister(ws, channel_name: str, peer_id: str):
        channel_stub = get_channel_stub_by_channel_name(channel_name)
        await channel_stub.async_task().unregister_subscriber(peer_id=peer_id)

        Logger.debug(f"unregister subscriber: {peer_id}")

    @staticmethod
    async def publish_heartbeat(ws, channel_name, peer_id):
        async def _publish_heartbeat():
            channel_stub = get_channel_stub_by_channel_name(channel_name)
            exception = None
            while ws.open:
                try:
                    is_registered = channel_stub.async_task().is_registered_subscriber(peer_id=peer_id)
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
                    new_block: dict = json.loads(
                        await channel_stub.async_task().announce_new_block(subscriber_block_height=height)
                    )
                    Logger.debug(f"publish_new_block: {new_block}")
                    request = Request("node_ws_PublishNewBlock", block=new_block)

                    await ws.send(json.dumps(request))
                    height += 1
            except Exception as e:
                traceback.print_exc()
                raise e

        await asyncio.ensure_future(_publish_new_block())
