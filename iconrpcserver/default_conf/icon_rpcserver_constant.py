# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import IntFlag


class SSLAuthType(IntFlag):
    none = 0
    server_only = 1
    mutual = 2


class NodeFunction(IntFlag):
    Block = 1 << 0  # 1
    Vote = 1 << 1  # 2
    Full = Block | Vote  # 3


class NodeType(IntFlag):
    CommunityNode = NodeFunction.Full  # 3
    CitizenNode = NodeFunction.Full ^ NodeFunction.Vote  # 1


class ApiVersion(IntFlag):
    v1 = 1
    v2 = 2
    v3 = 3


PEER_QUEUE_NAME_FORMAT = "Peer.{amqp_key}"
CHANNEL_QUEUE_NAME_FORMAT = "Channel.{channel_name}.{amqp_key}"
CHANNEL_TX_CREATOR_QUEUE_NAME_FORMAT = "ChannelTxCreator.{channel_name}.{amqp_key}"
ICON_SCORE_QUEUE_NAME_FORMAT = "IconScore.{channel_name}.{amqp_key}"


class ConfigKey:
    CONFIG = 'config'
    CHANNEL = 'channel'
    HOST = 'host'
    PORT = 'port'
    PORT_DIFF_REST_SERVICE_CONTAINER = 'portDiffRestServiceContainer'
    AMQP_TARGET = 'amqpTarget'
    AMQP_KEY = 'amqpKey'
    REST_SSL_TYPE = 'restSslType'
    DEFAULT_SSL_CERT_PATH = 'defaultSslCertPath'
    DEFAULT_SSL_KEY_PATH = 'defaultSslKeyPath'
    DEFAULT_SSL_TRUST_CERT_PATH = 'defaultSslTrustCertPath'
    IP_LOCAL = 'ipLocal'
    GRPC_TIMEOUT = 'grpcTimeout'
    GRPC_RETRY = 'grpcRetry'
    REST_ADDITIONAL_TIMEOUT = 'restAdditionalTimeout'
    SCORE_QUERY_TIMEOUT = 'scoreQueryTimeout'
    TBEARS_MODE = 'tbearsMode'
    REDIRECT_PROTOCOL = 'redirectProtocol'
    WS_HEARTBEAT_TIME = 'wsHeartBeatTime'
    REQUEST_MAX_SIZE = 'requestMaxSize'
    RELAY_TARGET = "relayTarget"
    GUNICORN_CONFIG = 'gunicornConfig'


ICON_RPC_SERVER_LOG_TAG = 'IconService'
DISPATCH_NODE_TAG = f'{ICON_RPC_SERVER_LOG_TAG}_dispatch_node'
DISPATCH_V2_TAG = f'{ICON_RPC_SERVER_LOG_TAG}_dispatch_v2'
DISPATCH_V3_TAG = f'{ICON_RPC_SERVER_LOG_TAG}_dispatch_v3'
DISPATCH_V3D_TAG = f'{ICON_RPC_SERVER_LOG_TAG}_dispatch_v3d'
