import argparse
import setproctitle

import gunicorn
from gunicorn.six import iteritems
import gunicorn.app.base

from iconrpcserver.default_conf.icon_rpcserver_config import default_rpcserver_config
from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey, ICON_RPCSERVER_PROCTITLE_FORMAT
from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger

from .server.peer_service_stub import PeerServiceStub
from .server.rest_server import ServerComponents


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
    parser.add_argument("-p", type=str, dest=ConfigKey.PORT_REST,
                        help="rest_proxy port")
    parser.add_argument("-c", type=str, dest=ConfigKey.CONFIG,
                        help="json configure file path")
    parser.add_argument("-at", type=str, dest=ConfigKey.AMQP_TARGET,
                        help="amqp target info [IP]:[PORT]")
    parser.add_argument("-ak", type=str, dest=ConfigKey.AMQP_KEY,
                        help="key sharing peer group using queue name. use it if one more peers connect one MQ")

    args = parser.parse_args()
    args_params = dict(vars(args))

    setproctitle.setproctitle(ICON_RPCSERVER_PROCTITLE_FORMAT.format(**args_params))

    conf = IconConfig(args.config, default_rpcserver_config)
    conf.load(args_params)
    Logger.load_config(conf)
    _run(conf)


def run_in_foreground(conf: 'IconConfig'):
    _run(conf)


def _run(conf: 'IconConfig'):
    # Setup port and host values.
    host = '0.0.0.0'

    # Connect gRPC stub.
    PeerServiceStub().conf = conf
    PeerServiceStub().rest_grpc_timeout = \
        conf[ConfigKey.GRPC_TIMEOUT] + conf[ConfigKey.REST_ADDITIONAL_TIMEOUT]
    PeerServiceStub().rest_score_query_timeout = \
        conf[ConfigKey.SCORE_QUERY_TIMEOUT] + conf[ConfigKey.REST_ADDITIONAL_TIMEOUT]
    PeerServiceStub().set_stub_port(conf[ConfigKey.PORT_REST] - conf[ConfigKey.PORT_DIFF_REST_SERVICE_CONTAINER],
                                    conf[ConfigKey.IP_LOCAL])
    ServerComponents().set_resource()

    Logger.debug(f"Run gunicorn webserver for HA. Port = {conf[ConfigKey.PORT_REST]}")

    # Configure SSL.
    ssl_context = ServerComponents().ssl_context
    certfile = ""
    keyfile = ""

    if ssl_context is not None:
        certfile = ssl_context[0]
        keyfile = ssl_context[1]

    options = {
        'bind': f"{host}:{conf[ConfigKey.PORT_REST]}",
        'workers': conf[ConfigKey.GUNICORN_WORKER_COUNT],
        'worker_class': "sanic.worker.GunicornWorker",
        'certfile': certfile,
        'SERVER_SOFTWARE': gunicorn.SERVER_SOFTWARE,
        'keyfile': keyfile
    }

    # Launch gunicorn web server.
    ServerComponents.conf = conf
    ServerComponents().ready(conf[ConfigKey.AMQP_TARGET], conf[ConfigKey.AMQP_KEY])
    StandaloneApplication(ServerComponents().app, options).run()
    Logger.error("Rest App Done!")


# Run as gunicorn web server.
if __name__ == "__main__":
    main()
