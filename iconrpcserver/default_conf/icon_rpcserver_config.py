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

import os
from .icon_rpcserver_constant import SSLAuthType, ConfigKey

default_rpcserver_config = \
    {
        "log": {
            "logger": "iconrpcserver"
        },
        ConfigKey.CHANNEL: "loopchain_default",
        ConfigKey.HOST: "0.0.0.0",
        ConfigKey.PORT: 9000,
        ConfigKey.PORT_DIFF_REST_SERVICE_CONTAINER: 1900,
        ConfigKey.AMQP_KEY: "amqp_key",
        ConfigKey.AMQP_TARGET: "127.0.0.1",
        ConfigKey.GUNICORN_CONFIG: {
            "workers": os.cpu_count() * 2 + 1,
            "worker_class": "sanic.worker.GunicornWorker",
            "graceful_timeout": 30
        },
        ConfigKey.REST_SSL_TYPE: SSLAuthType.none.value,
        ConfigKey.DEFAULT_SSL_CERT_PATH: "resources/ssl_test_cert/cert.pem",
        ConfigKey.DEFAULT_SSL_KEY_PATH: "resources/ssl_test_cert/key.pem",
        ConfigKey.DEFAULT_SSL_TRUST_CERT_PATH: "resources/ssl_test_ca/cert.pem",
        ConfigKey.IP_LOCAL: "127.0.0.1",
        ConfigKey.GRPC_TIMEOUT: 30,
        ConfigKey.GRPC_RETRY: 5,
        ConfigKey.REST_ADDITIONAL_TIMEOUT: 30,
        ConfigKey.SCORE_QUERY_TIMEOUT: 120,
        ConfigKey.WS_HEARTBEAT_TIME: 30,
        ConfigKey.REQUEST_MAX_SIZE: 2 * 1024 * 1024,
        ConfigKey.DOS_GUARD_ENABLE: False,
    }
