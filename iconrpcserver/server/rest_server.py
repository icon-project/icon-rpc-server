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
"""A module for restful API server of Peer"""

import _ssl
import ssl

from sanic import Sanic, response
from sanic.views import HTTPMethodView

import iconrpcserver.configure.configure as conf
from ..components import SingletonMetaClass
from .peer_service_stub import PeerServiceStub
from .rest_property import RestProperty
from .json_rpc.dispatcher.node import NodeDispatcher
from .json_rpc.dispatcher.version2 import Version2Dispatcher
from .json_rpc.dispatcher.version3 import Version3Dispatcher
from ..utils.message_queue.stub_collection import StubCollection

from iconcommons.logger import Logger


class ServerComponents(metaclass=SingletonMetaClass):
    def __init__(self):
        self.__app = Sanic(__name__)
        self.__app.config.KEEP_ALIVE = False

        # Decide whether to create context or not according to whether SSL is applied
        if conf.REST_SSL_TYPE == conf.SSLAuthType.none:
            self.__ssl_context = None
        elif conf.REST_SSL_TYPE == conf.SSLAuthType.server_only:
            self.__ssl_context = (conf.DEFAULT_SSL_CERT_PATH, conf.DEFAULT_SSL_KEY_PATH)
        elif conf.REST_SSL_TYPE == conf.SSLAuthType.mutual:
            self.__ssl_context = ssl.SSLContext(_ssl.PROTOCOL_SSLv23)

            self.__ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.__ssl_context.check_hostname = False

            self.__ssl_context.load_verify_locations(cafile=conf.DEFAULT_SSL_TRUST_CERT_PATH)
            self.__ssl_context.load_cert_chain(conf.DEFAULT_SSL_CERT_PATH, conf.DEFAULT_SSL_KEY_PATH)
        else:
            Logger.error(f"REST_SSL_TYPE must be one of [0,1,2]. But now conf.REST_SSL_TYPE is {conf.REST_SSL_TYPE}")

    @property
    def app(self):
        return self.__app

    @property
    def ssl_context(self):
        return self.__ssl_context

    def set_resource(self):
        self.__app.add_route(NodeDispatcher.dispatch, '/api/node/', methods=['POST'])

        self.__app.add_route(Version2Dispatcher.dispatch, '/api/v2', methods=['POST'])
        self.__app.add_route(Version3Dispatcher.dispatch, '/api/v3', methods=['POST'])

        self.__app.add_route(Disable.as_view(), '/api/v1', methods=['POST', 'GET'])
        self.__app.add_route(Status.as_view(), '/api/v1/status/peer')

    def ready(self, amqp_target, amqp_key):
        StubCollection().amqp_target = amqp_target
        StubCollection().amqp_key = amqp_key

        async def ready_tasks():
            Logger.debug('rest_server:initialize')
            await StubCollection().create_peer_stub()

            channels_info = await StubCollection().peer_stub.async_task().get_channel_infos()
            channel_name = None
            for channel_name, channel_info in channels_info.items():
                await StubCollection().create_channel_stub(channel_name)
                await StubCollection().create_icon_score_stub(channel_name)

            results = await StubCollection().peer_stub.async_task().get_channel_info_detail(channel_name)

            RestProperty().node_type = conf.NodeType(results[6])
            RestProperty().rs_target = results[3]

            Logger.debug(f'rest_server:initialize complete. '
                         f'node_type({RestProperty().node_type}), rs_target({RestProperty().rs_target})')

        self.__app.add_task(ready_tasks())

    def serve(self, amqp_target, amqp_key, api_port):
        self.ready(amqp_target, amqp_key)
        self.__app.run(host='0.0.0.0', port=api_port, debug=False, ssl=self.ssl_context)


class Status(HTTPMethodView):
    async def get(self, request):
        args = request.raw_args
        channel_name = conf.LOOPCHAIN_DEFAULT_CHANNEL if args.get('channel') is None else args.get('channel')
        return response.json(PeerServiceStub().get_status(channel_name))


class Disable(HTTPMethodView):
    async def get(self, request):
        return response.text("This api version not support any more!")

    async def post(self, request):
        return response.text("This api version not support any more!")
