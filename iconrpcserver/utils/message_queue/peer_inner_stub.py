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

from earlgrey import MessageQueueStub, message_queue_task

from . import earlgrey_close


class PeerInnerTask:

    @message_queue_task
    async def get_channel_infos(self) -> dict:
        pass

    @message_queue_task
    async def get_node_info_detail(self) -> dict:
        pass


class PeerInnerStub(MessageQueueStub[PeerInnerTask]):
    TaskType = PeerInnerTask

    def _callback_connection_close(self, exc: Exception):
        earlgrey_close(func="IconScoreInnerStub", exc=exc)
