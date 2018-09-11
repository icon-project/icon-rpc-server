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

import argparse
import os
import sys

import gunicorn
import gunicorn.app.base
from earlgrey import asyncio, aio_pika
from gunicorn.six import iteritems
from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger

from iconrpcserver.default_conf.icon_rpcserver_config import default_rpcserver_config
from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey
from iconrpcserver.icon_rpcserver_cli import ICON_RPCSERVER_CLI, ExitCode
from iconrpcserver.server.peer_service_stub import PeerServiceStub
from iconrpcserver.server.rest_server import ServerComponents


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """Web server runner by gunicorn.

    """

    def init(self, parser, opts, args):
        pass

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main():

    # Response server name as loopchain, not gunicorn.
    gunicorn.SERVER_SOFTWARE = 'loopchain'

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=str, dest=ConfigKey.PORT, default=None,
                        help="rest_proxy port")
    parser.add_argument("-c", type=str, dest=ConfigKey.CONFIG, default=None,
                        help="json configure file path")
    parser.add_argument("-at", type=str, dest=ConfigKey.AMQP_TARGET, default=None,
                        help="amqp target info [IP]:[PORT]")
    parser.add_argument("-ak", type=str, dest=ConfigKey.AMQP_KEY, default=None,
                        help="key sharing peer group using queue name. use it if one more peers connect one MQ")
    parser.add_argument("-ch", dest=ConfigKey.CHANNEL, default=None,
                        help="icon score channel")
    parser.add_argument("-tbears", dest=ConfigKey.TBEARS_MODE, action='store_true',
                        help="tbears mode")

    args = parser.parse_args()

    conf_path = args.config

    if conf_path is not None:
        if not IconConfig.valid_conf_path(conf_path):
            print(f'invalid config file : {conf_path}')
            sys.exit(ExitCode.COMMAND_IS_WRONG.value)
    if conf_path is None:
        conf_path = str()

    conf = IconConfig(conf_path, default_rpcserver_config)
    conf.load()
    conf.update_conf(dict(vars(args)))
    Logger.load_config(conf)
    Logger.print_config(conf, ICON_RPCSERVER_CLI)

    _run_async(_check_rabbitmq())
    _run_async(_run(conf))


def _run_async(async_func):
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(async_func)


def run_in_foreground(conf: 'IconConfig'):
    _run_async(_check_rabbitmq())
    _run_async(_run(conf))


async def _check_rabbitmq():
    connection = None
    try:
        amqp_user_name = os.getenv("AMQP_USERNAME", "guest")
        amqp_password = os.getenv("AMQP_PASSWORD", "guest")
        connection = await aio_pika.connect(login=amqp_user_name, password=amqp_password)
        connection.connect()
    except ConnectionRefusedError:
        Logger.error("rabbitmq-service disable", ICON_RPCSERVER_CLI)
        exit(0)
    finally:
        if connection:
            await connection.close()


async def _run(conf: 'IconConfig'):
    # Setup port and host values.
    host = '0.0.0.0'

    # Connect gRPC stub.
    PeerServiceStub().conf = conf
    PeerServiceStub().rest_grpc_timeout = \
        conf[ConfigKey.GRPC_TIMEOUT] + conf[ConfigKey.REST_ADDITIONAL_TIMEOUT]
    PeerServiceStub().rest_score_query_timeout = \
        conf[ConfigKey.SCORE_QUERY_TIMEOUT] + conf[ConfigKey.REST_ADDITIONAL_TIMEOUT]
    PeerServiceStub().set_stub_port(int(conf[ConfigKey.PORT]) -
                                    int(conf[ConfigKey.PORT_DIFF_REST_SERVICE_CONTAINER]),
                                    conf[ConfigKey.IP_LOCAL])
    ServerComponents.conf = conf
    ServerComponents().set_resource()

    Logger.debug(f"Run gunicorn webserver for HA. Port = {conf[ConfigKey.PORT]}")

    # Configure SSL.
    ssl_context = ServerComponents().ssl_context
    certfile = ""
    keyfile = ""

    if ssl_context is not None:
        certfile = ssl_context[0]
        keyfile = ssl_context[1]

    options = {
        'bind': f"{host}:{conf[ConfigKey.PORT]}",
        'workers': conf[ConfigKey.GUNICORN_WORKER_COUNT],
        'worker_class': "sanic.worker.GunicornWorker",
        'certfile': certfile,
        'SERVER_SOFTWARE': gunicorn.SERVER_SOFTWARE,
        'keyfile': keyfile,
        'capture_output': True
    }

    if conf[Logger.CATEGORY].get(Logger.FILE_PATH, None):
        options['errorlog'] = conf[Logger.CATEGORY][Logger.FILE_PATH]

    # Launch gunicorn web server.
    ServerComponents.conf = conf
    ServerComponents().ready()
    StandaloneApplication(ServerComponents().app, options).run()
    Logger.error("Rest App Done!")


# Run as gunicorn web server.
if __name__ == "__main__":
    main()
