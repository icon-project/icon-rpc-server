# -*- coding: utf-8 -*-

# Copyright 2017-2018 theloop Inc.
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
from enum import IntEnum


class SSLAuthType(IntEnum):
    none = 0
    server_only = 1
    mutual = 2


class NodeFunction(IntEnum):
    Block = 1 << 0  # 1
    Vote = 1 << 1  # 2
    Full = Block | Vote  # 3


class NodeType(IntEnum):
    CommunityNode = NodeFunction.Full  # 3
    CitizenNode = NodeFunction.Full ^ NodeFunction.Vote  # 1


class ApiVersion(IntEnum):
    v1 = 1
    v2 = 2
    v3 = 3


#rest
CONFIG_PATH = './rest_config.json'
REST_SERVER_PROCTITLE_FORMAT = "rest_server.{port}.{config}.{amqp_target}.{amqp_key}"


#loopchain
LOOPCHAIN_DEFAULT_CHANNEL = "loopchain_default"  # Default Channel Name
PORT_REST = 9000
PORT_DIFF_REST_SERVICE_CONTAINER = 1900

AMQP_TARGET = "127.0.0.1"
AMQP_KEY = "amqp_key"

PEER_QUEUE_NAME_FORMAT = "Peer.{amqp_key}"
CHANNEL_QUEUE_NAME_FORMAT = "Channel.{channel_name}.{amqp_key}"
ICON_SCORE_QUEUE_NAME_FORMAT = "IconScore.{channel_name}.{amqp_key}"

GUNICORN_WORKER_COUNT = 2

DISABLE_V1_API = True

REST_SSL_TYPE = SSLAuthType.none
DEFAULT_SSL_CERT_PATH = 'resources/ssl_test_cert/cert.pem'
DEFAULT_SSL_KEY_PATH = 'resources/ssl_test_cert/key.pem'
DEFAULT_SSL_TRUST_CERT_PATH = 'resources/ssl_test_ca/cert.pem'

IP_LOCAL = '127.0.0.1'
SUBSCRIBE_USE_HTTPS = False

GRPC_TIMEOUT = 30  # seconds
GRPC_RETRY = 5

REST_ADDITIONAL_TIMEOUT = 30  # seconds
SCORE_QUERY_TIMEOUT = 120

