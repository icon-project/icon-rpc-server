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
import sys
import subprocess
from enum import IntEnum

import rest
import rest.configure.configure as conf
from icon_common.logger import Logger

REST_SERVICE_STANDALONE = "RestServerStandAlone"


class ExitCode(IntEnum):
    SUCCEEDED = 0
    COMMAND_IS_WRONG = 1


def main():
    parser = argparse.ArgumentParser(prog='rest_cli.py', usage=f"""
    ==========================
    JsonRpcRest server version : {rest.__version__}
    ==========================
    JsonRpcRest commands:
        start : icon_service start
        stop : icon_service stop
        -p[--port] : rest_proxy port
        -o[--configure_file_path] : json configure file path
        --amqp_target : amqp target info [IP]:[PORT]
        --amqp_key : key sharing peer group using queue name. use it if one more peers connect one MQ
    """)

    parser.add_argument('command', type=str,
                        nargs='*',
                        choices=['start', 'stop'],
                        help='rest type [start|stop]')

    parser.add_argument("-p", "--port", type=str, dest="port",
                        help="rest_proxy port")
    parser.add_argument("-o", "--configure_file_path", type=str, dest="config",
                        help="json configure file path")
    parser.add_argument("--amqp_target", type=str, dest="amqp_target",
                        help="amqp target info [IP]:[PORT]")
    parser.add_argument("--amqp_key", type=str, dest="amqp_key",
                        help="key sharing peer group using queue name. use it if one more peers connect one MQ")

    args = parser.parse_args()

    if len(args.command) < 1:
        parser.print_help()
        sys.exit(ExitCode.COMMAND_IS_WRONG.value)

    if args.config:
        conf.Configure().load_configure_json(args.config)
    config_path = conf.CONFIG_PATH
    port = args.port or conf.PORT_REST
    amqp_target = args.amqp_target or conf.AMQP_TARGET
    amqp_key = args.amqp_key or conf.AMQP_KEY

    params = {'port': port,
              'config': config_path,
              'amqp_target': amqp_target,
              'amqp_key': amqp_key}

    Logger(config_path)

    command = args.command[0]
    if command == 'start' and len(args.command) == 1:
        result = start(params)
    elif command == 'stop' and len(args.command) == 1:
        result = stop(params)
    else:
        parser.print_help()
        result = ExitCode.COMMAND_IS_WRONG.value
    sys.exit(result)


def start(params: dict) -> int:
    if not is_serve_rest_server(params):
        start_process(params)
    Logger.info(f'start_command done!', REST_SERVICE_STANDALONE)
    return ExitCode.SUCCEEDED


def stop(params: dict) -> int:
    if is_serve_rest_server(params):
        stop_process(params)
    Logger.info(f'stop_command done!', REST_SERVICE_STANDALONE)
    return ExitCode.SUCCEEDED


def start_process(params: dict):
    Logger.debug('start_server() start')
    python_module_string = 'rest.rest_app'

    converted_params = {'-p': params['port'],
                        '-o': params['config'],
                        '--amqp_target': params['amqp_target'],
                        '--amqp_key': params['amqp_key']}

    custom_argv = []
    for k, v in converted_params.items():
        custom_argv.append(k)
        custom_argv.append(str(v))

    subprocess.Popen([sys.executable, '-m', python_module_string, *custom_argv], close_fds=True)
    Logger.debug('start_process() end')


def stop_process(params: dict):
    command = f"pkill gunicorn"
    subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    Logger.info(f'stop_process_rest_app!', REST_SERVICE_STANDALONE)


def is_serve_rest_server(params: dict) -> bool:
    return _check_serve(params)


def _check_serve(params: dict) -> bool:
    Logger.info(f'check_serve_rest_app!', REST_SERVICE_STANDALONE)
    # proc_title = conf.REST_SERVER_PROCTITLE_FORMAT.format(**params)
    # return find_procs_by_params(proc_title)
    return find_procs_by_params("gunicorn")


def find_procs_by_params(name) -> bool:
    # Return a list of processes matching 'name'.
    command = f"ps -ef | grep {name} | grep -v grep"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    if result.returncode == 1:
        return False
    return True
