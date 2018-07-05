import argparse
import setproctitle

import gunicorn
from gunicorn.six import iteritems
import gunicorn.app.base

import rest.configure.configure as conf
from iconservice.logger import Logger

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
    parser.add_argument("-p", "--port", type=str, dest="port",
                        help="rest_proxy port")
    parser.add_argument("-o", "--configure_file_path", type=str, dest="config",
                        help="json configure file path")
    parser.add_argument("--amqp_target", type=str, dest="amqp_target",
                        help="amqp target info [IP]:[PORT]")
    parser.add_argument("--amqp_key", type=str, dest="amqp_key",
                        help="key sharing peer group using queue name. use it if one more peers connect one MQ")

    args = parser.parse_args()
    args_params = dict(vars(args))
    setproctitle.setproctitle(conf.REST_SERVER_PROCTITLE_FORMAT.format(**args_params))

    if args.config:
        conf.Configure().load_configure_json(args.config)
    config_path = conf.CONFIG_PATH
    Logger(config_path)

    # Setup port and host values.
    port = args.port or conf.PORT_REST
    port = int(port)
    host = '0.0.0.0'

    # Connect gRPC stub.
    PeerServiceStub().set_stub_port(port - conf.PORT_DIFF_REST_SERVICE_CONTAINER, conf.IP_LOCAL)
    ServerComponents().set_resource()

    api_port = port
    Logger.debug(f"Run gunicorn webserver for HA. Port = {api_port}")

    # Configure SSL.
    ssl_context = ServerComponents().ssl_context
    certfile = ""
    keyfile = ""

    if ssl_context is not None:
        certfile = ssl_context[0]
        keyfile = ssl_context[1]

    options = {
        'bind': f"{host}:{api_port}",
        'workers': conf.GUNICORN_WORKER_COUNT,
        'worker_class': "sanic.worker.GunicornWorker",
        'certfile': certfile,
        'SERVER_SOFTWARE': "loopchain",
        'keyfile': keyfile
    }

    amqp_target = args.amqp_target or conf.AMQP_TARGET
    amqp_key = args.amqp_key or conf.AMQP_KEY

    # Launch gunicorn web server.
    ServerComponents().ready(amqp_target, amqp_key)
    StandaloneApplication(ServerComponents().app, options).run()
    Logger.error("Rest App Done!")


# Run as gunicorn web server.
if __name__ == "__main__":
    main()
