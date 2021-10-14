# Copyright 2019 ICON Foundation
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
"""A module for restful API server of Peer"""

import _ssl
import ssl
from http import HTTPStatus

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from sanic import Sanic, response
from sanic.log import LOGGING_CONFIG_DEFAULTS
from sanic.views import HTTPMethodView
from sanic_cors import CORS

from ..components import SingletonMetaClass
from ..default_conf.icon_rpcserver_constant import ConfigKey, SSLAuthType
from ..dispatcher.default import NodeDispatcher, WSDispatcher
from ..dispatcher.v2 import Version2Dispatcher
from ..dispatcher.v3 import Version3Dispatcher
from ..dispatcher.v3d import Version3DebugDispatcher
from ..utils.message_queue.stub_collection import StubCollection


class ServerComponents(metaclass=SingletonMetaClass):
    conf: 'IconConfig' = None

    def __init__(self):
        self.__app = Sanic(__name__, log_config=self._make_log_config())
        self.__app.config.KEEP_ALIVE = False
        self.__app.config.REQUEST_MAX_SIZE = ServerComponents.conf[ConfigKey.REQUEST_MAX_SIZE]
        CORS(self.__app)

        # jsonrpcserver 'dispatch()' to get bytes type for first parameter
        from iconrpcserver.utils import json_rpc
        json_rpc.monkey_patch()

        # Decide whether to create context or not according to whether SSL is applied

        rest_ssl_type = ServerComponents.conf[ConfigKey.REST_SSL_TYPE]
        if rest_ssl_type == SSLAuthType.none:
            self.__ssl_context = None
        elif rest_ssl_type == SSLAuthType.server_only:

            self.__ssl_context = (ServerComponents.conf[ConfigKey.DEFAULT_SSL_CERT_PATH],
                                  ServerComponents.conf[ConfigKey.DEFAULT_SSL_KEY_PATH])
        elif rest_ssl_type == SSLAuthType.mutual:
            self.__ssl_context = ssl.SSLContext(_ssl.PROTOCOL_SSLv23)

            self.__ssl_context.verify_mode = _ssl.CERT_REQUIRED
            self.__ssl_context.check_hostname = False

            self.__ssl_context.load_verify_locations(
                cafile=ServerComponents.conf[ConfigKey.DEFAULT_SSL_TRUST_CERT_PATH])

            self.__ssl_context.load_cert_chain(ServerComponents.conf[ConfigKey.DEFAULT_SSL_CERT_PATH],
                                               ServerComponents.conf[ConfigKey.DEFAULT_SSL_KEY_PATH])
        else:
            Logger.error(f"REST_SSL_TYPE must be one of [0,1,2]. But now conf.REST_SSL_TYPE is {rest_ssl_type}")

    def _make_log_config(self) -> dict:
        log_config = LOGGING_CONFIG_DEFAULTS
        log_config['loggers'] = {}
        log_config['handlers'] = {}
        log_config['formatters'] = {}
        return log_config

    @property
    def app(self):
        return self.__app

    @property
    def ssl_context(self):
        return self.__ssl_context

    def set_resource(self):
        self.__app.add_route(NodeDispatcher.dispatch, '/api/node/<channel_name:str>', methods=['POST'])
        self.__app.add_route(NodeDispatcher.dispatch, '/api/node/', methods=['POST'])

        self.__app.add_route(Version2Dispatcher.dispatch, '/api/v2', methods=['POST'])
        self.__app.add_route(Version3Dispatcher.dispatch, '/api/v3/<channel_name:str>', methods=['POST'])
        self.__app.add_route(Version3Dispatcher.dispatch, '/api/v3/', methods=['POST'])

        self.__app.add_route(Version3DebugDispatcher.dispatch, '/api/debug/v3/<channel_name:str>', methods=['POST'])
        self.__app.add_route(Version3DebugDispatcher.dispatch, '/api/debug/v3/', methods=['POST'])

        self.__app.add_route(Disable.as_view(), '/api/v1', methods=['POST', 'GET'])
        self.__app.add_route(Status.as_view(), '/api/v1/status/peer')
        self.__app.add_route(Avail.as_view(), '/api/v1/avail/peer')

        self.__app.add_websocket_route(WSDispatcher.dispatch, '/api/ws/<channel_name:str>')

    def ready(self):
        StubCollection().amqp_target = ServerComponents.conf[ConfigKey.AMQP_TARGET]
        StubCollection().amqp_key = ServerComponents.conf[ConfigKey.AMQP_KEY]
        StubCollection().conf = ServerComponents.conf

        @self.__app.listener("before_server_start")
        async def ready_tasks(app, loop):
            Logger.debug('rest_server:initialize')

            if self.conf.get(ConfigKey.TBEARS_MODE, False):
                channel_name = self.conf.get(ConfigKey.CHANNEL, 'loopchain_default')
                await StubCollection().create_channel_stub(channel_name)
                await StubCollection().create_channel_tx_creator_stub(channel_name)
                await StubCollection().create_icon_score_stub(channel_name)
            else:
                await StubCollection().create_peer_stub()
                channels = await StubCollection().peer_stub.async_task().get_channel_infos()
                for channel_name in channels:
                    await StubCollection().create_channel_stub(channel_name)
                    await StubCollection().create_channel_tx_creator_stub(channel_name)
                    await StubCollection().create_icon_score_stub(channel_name)

            Logger.debug(f'rest_server:initialize complete.')

    def serve(self, api_port):
        self.ready()
        self.__app.run(host='0.0.0.0', port=api_port, debug=False, ssl=self.ssl_context)


async def get_channel_status(channel_name) -> dict:
    channel_stub = StubCollection().channel_stubs[channel_name]
    status_data: dict = await channel_stub.async_task().get_status()

    return status_data


class Status(HTTPMethodView):
    async def get(self, request, *args, **kwargs):
        channel_name = request.args.get('channel') or ServerComponents.conf.get(ConfigKey.CHANNEL)
        status_data: dict = await get_channel_status(channel_name)

        return response.json(status_data)


class Avail(HTTPMethodView):
    async def get(self, request, *args, **kwargs):
        channel_name = request.args.get('channel') or ServerComponents.conf.get(ConfigKey.CHANNEL)
        status = HTTPStatus.OK
        result: dict = await get_channel_status(channel_name)

        if not result['service_available']:
            status = HTTPStatus.SERVICE_UNAVAILABLE

        return response.json(result, status=status)


class Disable(HTTPMethodView):
    async def get(self, request, *args, **kwargs):
        return response.text("This api version not support any more!")

    async def post(self, request, *args, **kwargs):
        return response.text("This api version not support any more!")
