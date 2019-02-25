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
from typing import TYPE_CHECKING, Tuple, List, Dict
from . import exit_process

if TYPE_CHECKING:
    from earlgrey import RobustConnection


class ChannelInnerTask:
    @message_queue_task
    async def get_invoke_result(self, tx_hash) -> Tuple[int, str]:
        pass

    @message_queue_task
    async def get_tx_info(self, tx_hash) -> Tuple[int, dict]:
        pass

    @message_queue_task
    async def get_tx_by_address(self, address, index) -> Tuple[list, int]:
        pass

    @message_queue_task
    async def get_block_v2(self, block_height,
                           block_hash,
                           block_data_filter,
                           tx_data_filter) -> Tuple[int, str, str, list]:
        pass

    @message_queue_task
    async def get_block(self, block_height,
                        block_hash,
                        block_data_filter,
                        tx_data_filter) -> Tuple[int, str, bytes, str, list]:
        pass

    @message_queue_task
    async def announce_new_block(self, subscriber_block_height: int) -> Tuple[str, bytes]:
        pass

    @message_queue_task
    async def get_tx_proof(self, tx_hash: str) -> list:
        pass

    @message_queue_task
    async def get_receipt_proof(self, tx_hash: str) -> list:
        pass

    @message_queue_task
    async def prove_tx(self, tx_hash: str, proof: list) -> str:
        pass

    @message_queue_task
    async def get_citizens(self) -> List[Dict[str, str]]:
        pass

    @message_queue_task
    async def register_citizen(self, peer_id, target, connected_time) -> bool:
        pass

    @message_queue_task
    async def unregister_citizen(self, peer_id):
        pass

    @message_queue_task
    async def is_citizen_registered(self, peer_id) -> bool:
        pass


class ChannelInnerStub(MessageQueueStub[ChannelInnerTask]):
    TaskType = ChannelInnerTask

    def _callback_connection_lost_callback(self, connection: 'RobustConnection'):
        exit_process()


class ChannelTxCreatorInnerTask:
    @message_queue_task
    async def create_icx_tx(self, kwargs) -> Tuple[int, str]:
        pass


class ChannelTxCreatorInnerStub(MessageQueueStub[ChannelTxCreatorInnerTask]):
    TaskType = ChannelTxCreatorInnerTask

    def _callback_connection_lost_callback(self, connection: 'RobustConnection'):
        exit_process()
