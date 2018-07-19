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
"""stub wrapper for gRPC stub.
This object has own channel information and support re-generation of gRPC stub."""

import grpc

from ..utils.message_queue.stub_collection import StubCollection
from ..default_conf.icon_rpcserver_constant import ConfigKey
from iconcommons.logger import Logger


class StubManager:
    def __init__(self, target, stub_type):
        self.__target = target
        self.__stub_type = stub_type
        self.__stub = None
        self.__channel = None

        self.__make_stub()

    def __make_stub(self):
        self.__channel = grpc.insecure_channel(self.__target)
        self.__stub = self.__stub_type(self.__channel)

    def call(self, method_name, message, timeout=None):
        if timeout is None:

            timeout = StubCollection().conf[ConfigKey.GRPC_TIMEOUT]

        e = None
        for _ in range(StubCollection().conf[ConfigKey.GRPC_RETRY]):
            try:
                stub_method = getattr(self.__stub, method_name)
                return stub_method(message, timeout)
            except Exception as e:
                self.__make_stub()
                Logger.warning(f"gRPC call fail method_name({method_name}), message({message}): {e}")

        raise e
