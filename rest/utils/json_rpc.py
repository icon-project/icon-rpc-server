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

import logging
import json
import aiohttp

from jsonrpcclient.aiohttp_client import aiohttpClient

import rest.configure.configure as conf
from ..utils.message_queue import StubCollection
from ..protos import message_code


async def redirect_request_to_rs(message, rs_target, version='v3'):
    rs_url = f"{'https' if conf.SUBSCRIBE_USE_HTTPS else 'http'}://{rs_target}/api/{version}"
    async with aiohttp.ClientSession() as session:
        result = await aiohttpClient(session, rs_url).request(
            method_name=message["method"], message=message, node_type=conf.NodeType.CitizenNode)

    return result


async def get_block_by_params(block_height=None, block_hash=""):
    channel_name = conf.LOOPCHAIN_DEFAULT_CHANNEL
    block_data_filter = "prev_block_hash, height, block_hash, merkle_tree_root_hash," \
                        " time_stamp, peer_id, signature"
    tx_data_filter = "icx_origin_data"
    channel_stub = StubCollection().channel_stubs[channel_name]
    response_code, block_hash, block_data_json, tx_data_json_list = \
        await channel_stub.async_task().get_block(
            block_height=block_height,
            block_hash=block_hash,
            block_data_filter=block_data_filter,
            tx_data_filter=tx_data_filter
        )

    try:
        result = {
            'response_code': response_code,
            'block': json.loads(block_data_json)
        }
    except Exception as e:
        logging.error(f"get_block_by_params error caused by : {e}")
        result = {
            'response_code': message_code.Response.fail_wrong_block_hash,
            'block': {}
        }
    return block_hash, result
