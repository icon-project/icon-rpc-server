# Copyright 2017 theloop Inc.
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
"""Wrapper for Stub to Peer Service"""

import json

from ..components import SingletonMetaClass
from ..protos import loopchain_pb2, loopchain_pb2_grpc
from ..utils.stub_manager import StubManager


class PeerServiceStub(metaclass=SingletonMetaClass):
    def __init__(self):
        self.__stub_to_peer_service = None
        self.conf = None
        self.rest_grpc_timeout = None
        self.rest_score_query_timeout = None

    def set_stub_port(self, port, IP_address):
        self.__stub_to_peer_service = StubManager(
            IP_address + ':' + str(port),
            loopchain_pb2_grpc.PeerServiceStub)

    def call(self, *args):
        # util.logger.spam(f"peer_service_stub:call target({self.__stub_to_peer_service.target})")
        return self.__stub_to_peer_service.call(*args)

    def get_status(self, channel: str):
        response = self.call("GetStatus",
                             loopchain_pb2.StatusRequest(request="", channel=channel),
                             self.rest_grpc_timeout)
        status_json_data = json.loads(response.status)
        status_json_data['block_height'] = response.block_height
        status_json_data['total_tx'] = response.total_tx
        status_json_data['leader_complaint'] = response.is_leader_complaining

        return status_json_data
