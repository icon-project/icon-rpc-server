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

import argparse
import subprocess
import sys
from enum import IntEnum

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger

from iconrpcserver.default_conf.icon_rpcserver_config import default_rpcserver_config
from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey

REST_SERVICE_STANDALONE = "RestServerStandAlone"


class ExitCode(IntEnum):
    SUCCEEDED = 0
    COMMAND_IS_WRONG = 1


def main():
    parser = argparse.ArgumentParser(prog='iconrpcserver_cli.py', usage=f"""
    ==========================
    iconrpcserver server
    ==========================
    iconrpcserver commands:
        start : icon_service start
        stop : icon_service stop
        -p : rest_proxy port
        -c : json configure file path
        -at : amqp target info [IP]:[PORT]
        -ak : key sharing peer group using queue name. use it if one more peers connect one MQ
        -ch : loopchain channel ex) loopchain_default
        -fg : foreground process
    """)

    parser.add_argument('command', type=str,
                        nargs='*',
                        choices=['start', 'stop'],
                        help='rest type [start|stop]')

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
    parser.add_argument("-fg", dest='foreground', action='store_true',
                        help="icon rpcserver run foreground")

    args = parser.parse_args()

    if len(args.command) < 1:
        parser.print_help()
        sys.exit(ExitCode.COMMAND_IS_WRONG.value)

    conf_path = args.config

    if conf_path is not None:
        if not IconConfig.valid_conf_path(conf_path):
            Logger.error(f'invalid config path {conf_path}')
            sys.exit(ExitCode.COMMAND_IS_WRONG.value)
    if conf_path is None:
        conf_path = str()

    conf = IconConfig(conf_path, default_rpcserver_config)
    conf.load(dict(vars(args)))
    Logger.load_config(conf)

    command = args.command[0]
    if command == 'start' and len(args.command) == 1:
        result = start(conf)
    elif command == 'stop' and len(args.command) == 1:
        result = stop(conf)
    else:
        parser.print_help()
        result = ExitCode.COMMAND_IS_WRONG.value
    sys.exit(result)


def start(conf: 'IconConfig') -> int:
    if not _is_running_icon_service(conf):
        start_process(conf)
    Logger.info(f'start_command done!', REST_SERVICE_STANDALONE)
    return ExitCode.SUCCEEDED


def stop(conf: 'IconConfig') -> int:
    if _is_running_icon_service(conf):
        stop_process(conf)
    Logger.info(f'stop_command done!', REST_SERVICE_STANDALONE)
    return ExitCode.SUCCEEDED


def start_process(conf: 'IconConfig'):
    Logger.debug('start_server() start')
    python_module_string = 'iconrpcserver.icon_rpcserver_app'

    converted_params = {'-p': conf[ConfigKey.PORT],
                        '-c': conf.get(ConfigKey.CONFIG),
                        '-at': conf[ConfigKey.AMQP_TARGET],
                        '-ak': conf[ConfigKey.AMQP_KEY],
                        '-ch': conf[ConfigKey.CHANNEL]}

    custom_argv = []
    for k, v in converted_params.items():
        if v is None:
            continue
        custom_argv.append(k)
        custom_argv.append(str(v))

    is_foreground = conf.get('foreground', False)
    if is_foreground:
        from iconrpcserver.icon_rpcserver_app import run_in_foreground
        del conf['foreground']
        run_in_foreground(conf)
    else:
        subprocess.Popen([sys.executable, '-m', python_module_string, *custom_argv], close_fds=True)
    Logger.debug('start_process() end')


def stop_process(conf: 'IconConfig'):
    command = f'lsof -i :{conf[ConfigKey.PORT]} -t | xargs kill'
    subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    Logger.info(f'stop_process_rest_app!', REST_SERVICE_STANDALONE)


def _is_running_icon_service(conf: 'IconConfig') -> bool:
    return _check_service_running(conf)


def _check_service_running(conf: 'IconConfig') -> bool:
    Logger.info(f'check_serve_rest_app!', REST_SERVICE_STANDALONE)
    return find_procs_by_params(conf[ConfigKey.PORT])


def find_procs_by_params(port) -> bool:
    # Return a list of processes matching 'name'.
    command = f"lsof -i TCP:{port}"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    if result.returncode == 1:
        return False
    return True
