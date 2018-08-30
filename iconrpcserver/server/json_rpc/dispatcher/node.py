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

import json

from jsonrpcserver.aio import AsyncMethods
from sanic import response

from ....protos import message_code
from ....utils.json_rpc import get_block_by_params
from ....utils.message_queue.stub_collection import StubCollection

methods = AsyncMethods()


class NodeDispatcher:
    @staticmethod
    async def dispatch(request):
        req = json.loads(request.body.decode())
        req["params"] = req.get("params", {})
        req["params"]["method"] = request.json["method"]

        if "node_" not in req["params"]["method"]:
            return response.text("no support method!")

        dispatch_response = await methods.dispatch(req)
        return response.json(dispatch_response, status=dispatch_response.http_status)

    @staticmethod
    @methods.add
    async def node_GetChannelInfos(**kwargs):
        channel_infos = await StubCollection().peer_stub.async_task().get_channel_infos()

        channel_infos = {"channel_infos": channel_infos}
        return channel_infos

    @staticmethod
    @methods.add
    async def node_Subscribe(**kwargs):
        channel, peer_target = kwargs['message']['channel'], kwargs['message']['peer_target']
        channel_stub = StubCollection().channel_stubs[channel]
        response_code = await channel_stub.async_task().add_audience_subscriber(peer_target=peer_target)
        return {"response_code": response_code,
                "message": message_code.get_response_msg(response_code)}

    @staticmethod
    @methods.add
    async def node_Unsubscribe(**kwargs):
        channel, peer_target = kwargs['message']['channel'], kwargs['message']['peer_target']
        channel_stub = StubCollection().channel_stubs[channel]
        response_code = await channel_stub.async_task().remove_audience_subscriber(peer_target=peer_target)
        return {"response_code": response_code,
                "message": message_code.get_response_msg(response_code)}

    @staticmethod
    @methods.add
    async def node_AnnounceConfirmedBlock(**kwargs):
        channel, block, commit_state = kwargs['message']['channel'], kwargs['message']['block'], \
                                       kwargs['message'].get('commit_state', "")
        channel_stub = StubCollection().channel_stubs[channel]
        response_code = await channel_stub.async_task().announce_confirmed_block(block.encode('utf-8'), commit_state)
        return {"response_code": response_code,
                "message": message_code.get_response_msg(response_code)}

    @staticmethod
    @methods.add
    async def node_GetBlockByHeight(**kwargs):
        block_hash, response = await get_block_by_params(block_height=kwargs['message']['height'],
                                                         with_commit_state=True)
        return response
