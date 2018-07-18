# Copyright [theloop]
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

from typing import Dict

import rest.configure.configure as conf
from ...components.singleton import SingletonMetaClass
from .peer_inner_stub import PeerInnerStub
from .channel_inner_stub import ChannelInnerStub
from .icon_score_inner_stub import IconScoreInnerStub
from iconcommons.logger import Logger


class StubCollection(metaclass=SingletonMetaClass):
    def __init__(self):
        self.amqp_target = None
        self.amqp_key = None

        self.peer_stub: PeerInnerStub = None
        self.channel_stubs: Dict[str, ChannelInnerStub] = {}
        self.icon_score_stubs: Dict[str, IconScoreInnerStub] = {}

    async def create_peer_stub(self):
        queue_name = conf.PEER_QUEUE_NAME_FORMAT.format(amqp_key=self.amqp_key)
        self.peer_stub = PeerInnerStub(self.amqp_target, queue_name)
        await self.peer_stub.connect()
        return self.peer_stub

    async def create_channel_stub(self, channel_name):
        queue_name = conf.CHANNEL_QUEUE_NAME_FORMAT.format(
            channel_name=channel_name, amqp_key=self.amqp_key)
        stub = ChannelInnerStub(self.amqp_target, queue_name)
        await stub.connect()
        self.channel_stubs[channel_name] = stub

        Logger.debug(f"ChannelTasks : {channel_name}, Queue : {queue_name}")
        return stub

    async def create_icon_score_stub(self, channel_name):
        queue_name = conf.ICON_SCORE_QUEUE_NAME_FORMAT.format(
            channel_name=channel_name, amqp_key=self.amqp_key
        )
        stub = IconScoreInnerStub(self.amqp_target, queue_name)
        await stub.connect()
        self.icon_score_stubs[channel_name] = stub
        return stub
