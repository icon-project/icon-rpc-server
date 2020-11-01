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

from typing import Tuple, List, Dict, Union, NoReturn, Optional

from earlgrey import MessageQueueStub, message_queue_task

from ...utils.message_queue import earlgrey_close


class ChannelInnerTask:
    @message_queue_task
    async def get_invoke_result(self, tx_hash) -> Tuple[int, str]:
        """Get invoke result

        :param tx_hash:
        :return: (response_code, invoke_result)
        """
        pass

    @message_queue_task
    async def get_tx_info(self, tx_hash) -> Tuple[int, dict]:
        """Get transaction info

        :param tx_hash:
        :return: (response_code, tx_info)
        """
        pass

    @message_queue_task
    async def get_tx_by_address(self, address, index) -> Tuple[list, int]:
        """Get transaction

        :param address:
        :param index:
        :return: (tx_list, next_index)
        """
        pass

    @message_queue_task
    async def get_block_v2(self, block_height, block_hash) -> Tuple[int, str, str]:
        """Get block via v2

        :param block_height:
        :param block_hash:
        :return: (response_code, block_hash, block_data_json)
        """
        pass

    @message_queue_task
    async def get_block(self, block_height, block_hash) -> Tuple[int, str, bytes, str]:
        """Get block via v3

        :param block_height:
        :param block_hash:
        :return: (response_code, block_hash, confirm_info, block_data_json)
        """
        pass

    @message_queue_task
    async def announce_new_block(self, subscriber_block_height: int, subscriber_id: str) -> Tuple[str, bytes]:
        """Announce new block  websocket

        :param subscriber_block_height:
        :param subscriber_id:
        :return: (new_block_dumped, confirm_info_bytes)
        """
        pass

    @message_queue_task
    async def get_tx_proof(self, tx_hash: str) -> Union[list, dict]:
        """Get transaction proof

        :param tx_hash:
        :return: tx_proof list when success, error response when fail
        """
        pass

    @message_queue_task
    async def get_receipt_proof(self, tx_hash: str) -> Union[list, dict]:
        """Get receipt proof

        :param tx_hash:
        :return: receipt proof list when success, error response when fail
        """
        pass

    @message_queue_task
    async def prove_tx(self, tx_hash: str, proof: list) -> Union[str, dict]:
        """Prove transaction

        :param tx_hash:
        :param proof: proof list which response of get_tx_proof
        :return: if transaction proved, '0x1' else '0x0'. error response when something wrong
        """
        pass

    @message_queue_task
    async def prove_receipt(self, tx_hash: str, proof: list) -> Union[str, dict]:
        """Prove receipt

        :param tx_hash:
        :param proof: proof list which response of get_receipt_proof
        :return: if receipt proved, '0x1' else '0x0'. error response when something wrong
        """
        pass

    @message_queue_task
    async def get_citizens(self) -> List[Dict[str, str]]:
        """Get citizens

        :return: e.g. [ {"id": "peer_id", "target": "target", "connected_time": "connected_time"}, {...} ]
        """
        pass

    @message_queue_task
    async def register_citizen(self, peer_id: str, target: str, connected_time: str) -> bool:
        """Register citizen

        :param peer_id:
        :param target:
        :param connected_time:
        :return: True when citizen registered, False when register fail
        """
        pass

    @message_queue_task
    async def unregister_citizen(self, peer_id: str) -> NoReturn:
        """Unregister citizen

        :param peer_id:
        :return: no return
        """
        pass

    @message_queue_task
    async def get_reps_by_hash(self, reps_hash: str) -> List[Dict[str, str]]:
        """Get reps list

        :param reps_hash:
        :return: reps_list that matching reps_hash.
            e.g. [ {"id": "x...", "p2pEndpoint": "ip_address:port" }, {...} ]
        """
        pass

    @message_queue_task
    async def get_status(self) -> dict:
        """Get status

        :return: e.g. {"nid": "0x3", "status": "Service is online : ...", ... , "versions": {...}}
        """
        pass

    @message_queue_task
    async def wait_for_unregister_signal(self, subscriber_id: str) -> bool:
        """Wait for unregister signal

        :param subscriber_id:
        :return: True when unregister finished
        """
        pass

    @message_queue_task
    async def get_block_receipts(self, block_height, block_hash) -> Tuple[int, str]:
        """Get block receipts via v3

        :param block_height:
        :param block_hash:
        :return: (response_code, block_receipts_json)
        """
        pass


class ChannelInnerStub(MessageQueueStub[ChannelInnerTask]):
    TaskType = ChannelInnerTask

    def _callback_connection_close(self, sender, exc: Optional[BaseException], *args, **kwargs):
        earlgrey_close(func="ChannelInnerStub", exc=exc)


class ChannelTxCreatorInnerTask:
    @message_queue_task
    async def create_icx_tx(self, kwargs) -> Tuple[int, str, str]:
        """Create icx transaction

        :param kwargs:
        :return: (response_code, tx_hash, relay_target)
        """
        pass


class ChannelTxCreatorInnerStub(MessageQueueStub[ChannelTxCreatorInnerTask]):
    TaskType = ChannelTxCreatorInnerTask

    def _callback_connection_close(self, sender, exc: Optional[BaseException], *args, **kwargs):
        earlgrey_close(func="ChannelTxCreatorInnerStub", exc=exc)
