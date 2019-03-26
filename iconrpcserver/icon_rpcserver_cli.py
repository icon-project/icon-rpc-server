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

import argparse
import os
import signal
import subprocess
import sys
from enum import IntEnum

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger

from iconrpcserver.default_conf.icon_rpcserver_config import default_rpcserver_config
from iconrpcserver.default_conf.icon_rpcserver_constant import ConfigKey

ICON_RPCSERVER_CLI = "IconRpcServerCli"


class ExitCode(IntEnum):
    SUCCEEDED = 0
    COMMAND_IS_WRONG = 1


def main():
    parser = argparse.ArgumentParser(prog='iconrpcserver_cli.py', usage=f"""
    ==========================
    iconrpcserver server
    ==========================
    iconrpcserver commands:
        start : iconrpcserver start
        stop : iconrpcserver stop
        -p : rest_proxy port
        -c : json configure file path
        -at : amqp target info [IP]:[PORT]
        -ak : key sharing peer group using queue name. use it if one more peers connect one MQ
        -ch : loopchain channel ex) loopchain_default
        -fg : foreground process
        -tbears : tbears mode
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
    parser.add_argument("-tbears", dest=ConfigKey.TBEARS_MODE, action='store_true',
                        help="tbears mode")

    args = parser.parse_args()

    if len(args.command) < 1:
        parser.print_help()
        sys.exit(ExitCode.COMMAND_IS_WRONG.value)

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

    # set env config
    redirect_protocol = os.getenv(ConfigKey.REDIRECT_PROTOCOL)
    if redirect_protocol:
        conf.update_conf({ConfigKey.REDIRECT_PROTOCOL: redirect_protocol})
    else:
        from iconrpcserver.utils import to_low_camel_case
        low_camel_case_key = to_low_camel_case(ConfigKey.REDIRECT_PROTOCOL)
        redirect_protocol = conf.get(low_camel_case_key)
        if redirect_protocol is not None:
            conf.update_conf({ConfigKey.REDIRECT_PROTOCOL: redirect_protocol})

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
    if not _check_if_process_running(conf):
        start_process(conf)
    Logger.info(f'start_command done!', ICON_RPCSERVER_CLI)
    return ExitCode.SUCCEEDED


def stop(conf: 'IconConfig') -> int:
    if _check_if_process_running(conf):
        stop_process(conf)
    Logger.info(f'stop_command done!', ICON_RPCSERVER_CLI)
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
    if conf.get(ConfigKey.TBEARS_MODE, False):
        custom_argv.append('-tbears')

    is_foreground = conf.get('foreground', False)
    if is_foreground:
        from iconrpcserver.icon_rpcserver_app import run_in_foreground
        del conf['foreground']
        run_in_foreground(conf)
    else:
        subprocess.Popen([sys.executable, '-m', python_module_string, *custom_argv], close_fds=True)
    Logger.debug('start_process() end')


def stop_process(conf: 'IconConfig'):
    Logger.info(f'stop_process!', ICON_RPCSERVER_CLI)
    pids = _get_process_list_by_port(conf[ConfigKey.PORT])
    for p in pids:
        try:
            os.kill(int(p), signal.SIGKILL)
        except ValueError:
            continue


def _check_if_process_running(conf: 'IconConfig') -> bool:
    Logger.info(f'check_if_process_running!', ICON_RPCSERVER_CLI)
    if _get_process_list_by_port(conf[ConfigKey.PORT]):
        return True
    return False


def _get_process_list_by_port(port) -> list:
    if not isinstance(port, int):
        raise Exception('Invalid port number')
    result = subprocess.run(['lsof', '-i', f'TCP:{port}', '-t'], stdout=subprocess.PIPE)
    if result.returncode == 0:
        return result.stdout.split(b'\n')
    return []
