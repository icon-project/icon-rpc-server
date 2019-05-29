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
"""json rpc dispatcher version 3"""

from iconcommons.logger import Logger

from iconrpcserver.dispatcher.v3 import methods
from iconrpcserver.utils.icon_service import response_to_json_query, make_request
from iconrpcserver.utils.json_rpc import get_icon_stub_by_channel_name


class RepDispatcher:
    @staticmethod
    @methods.add
    async def rep_getList(**kwargs):
        channel = kwargs['context']['channel']
        score_stub = get_icon_stub_by_channel_name(channel)
        method = "ise_getPReps"
        request = make_request(method, kwargs)

        response = score_stub.sync_task().call(request)
        rep_list = [{"id": rep_info["id"], "target": rep_info["target"]}
                    for rep_info in response["result"]["preps"]]
        Logger.debug(f'rep list: {rep_list}')

        start_term_height = '0x0'
        end_term_height = '0x0'
        rep_hash = ''
        # term_height, rep_root_hash should be updated after IISS is implemented.
        response = {
            'startTermHeight': start_term_height,
            'endTermHeight': end_term_height,
            'repHash': rep_hash,
            'rep': rep_list
        }
        return response_to_json_query(response)
