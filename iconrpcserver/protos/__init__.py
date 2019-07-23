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
""" A package for protos """

from iconcommons import Logger

try:
    # TODO : if protobuf useless, remove this
    # this import work when iconrpcserver run by loopchain
    from loopchain.protos import loopchain_pb2, loopchain_pb2_grpc
except ModuleNotFoundError as e:
    Logger.info(f"loopchain protobuf module not found try to import local"
                f" : {e}", "protos")
    import os
    import sys

    proto_path = os.path.dirname(os.path.relpath(__file__))
    sys.path.append(proto_path)

    # try import from local protobuf
    from . import loopchain_pb2, loopchain_pb2_grpc

__all__ = ['loopchain_pb2', 'loopchain_pb2_grpc']
