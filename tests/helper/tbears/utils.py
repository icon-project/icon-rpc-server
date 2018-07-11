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

import os
from time import time

from typing import TYPE_CHECKING, Optional
from tests.helper.tbears.src_to_zip import SrcToZip, ZipException, FillDeployPaylodException

if TYPE_CHECKING:
    from tests.helper.wallet import Wallet


def get_deploy_req_template():
    payload = {
        "version": "0x3",
        "from": "",
        "to": f'cx{"0"*40}',
        "stepLimit": "0x12345",
        "timestamp": f'{hex(get_now_time_stamp())}',
        "nonce": "0x1",
        "dataType": "deploy",
        "data": {
            "contentType": "application/zip",
            "content": "",
            "params": {

            }
        }
    }
    return payload


def get_send_token_req_template():
    payload = {
        "version": "0x3",
        "from": "",
        "to": "",
        "stepLimit": "0x12345",
        "timestamp": f'{hex(get_now_time_stamp())}',
        "nonce": "0x1",
        "dataType": "call",
        "data": {
            "method": "transfer1",
            "params": {
                "addr_to": "",
                "value": ""
            }
        }
    }
    return payload


def get_send_token_payload(wallet: 'Wallet', score_addr: str, data_addr: str, data_value: str) -> dict:
    payload = get_send_token_req_template()
    payload['from'] = f'{wallet.address}'
    payload['to'] = score_addr
    payload['data']['params']['addr_to'] = data_addr
    payload['data']['params']['value'] = data_value
    return payload


def get_deploy_payload(path: str, wallet: 'Wallet', step_limit: str=None, score_address: str=None,
                       params: dict=None) -> dict:
    payload = get_deploy_req_template()
    fill_optional_deploy_field(payload=payload, step_limit=step_limit, score_address=score_address,
                               params=params)
    fill_deploy_payload(payload, path, wallet)
    return payload


def fill_optional_deploy_field(payload: dict, step_limit: str = None, score_address: str = None,
                               params: dict = None):
    if step_limit:
        payload["stepLimit"] = step_limit
    if score_address:
        payload["to"] = score_address
    if params:
        payload["data"]["params"] = params


def fill_deploy_payload(payload: dict = None, project_root_path: str = None, wallet: Optional['Wallet'] = None):
    if not payload or not wallet:
        raise Exception
    if os.path.isdir(project_root_path) is False:
        raise Exception
    try:
        memory_zip = SrcToZip()
        memory_zip.zip_in_memory(project_root_path)
    except ZipException:
        raise FillDeployPaylodException
    else:
        payload['data']['content'] = f'0x{memory_zip.data.hex()}'
        payload['from'] = f'{wallet.address}'


# micro seconds
def get_now_time_stamp() -> int:
    return int(time() * 10 ** 6)