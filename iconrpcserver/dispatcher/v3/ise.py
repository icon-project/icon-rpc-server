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

from typing import Any, Optional

from iconrpcserver.dispatcher.v3 import methods
from iconrpcserver.utils.icon_service import make_request, response_to_json_query
from iconrpcserver.utils.json_rpc import get_icon_stub_by_channel_name


class IseDispatcher:
    HASH_KEY_DICT = ['hash', 'blockHash', 'txHash', 'prevBlockHash']

    @staticmethod
    @methods.add
    async def ise_getStatus(**kwargs):
        channel = kwargs['context']['channel']
        method = 'ise_getStatus'
        request = make_request(method, kwargs)
        score_stub = get_icon_stub_by_channel_name(channel)
        response = await score_stub.async_task().query(request)
        error = response.get('error')
        if error is None:
            IseDispatcher._hash_convert(None, response)
        return response_to_json_query(response)

    @staticmethod
    def _hash_convert(key: Optional[str], response: Any):
        if key is None:
            result = response
        else:
            result = response[key]
        if isinstance(result, dict):
            for key in result:
                IseDispatcher._hash_convert(key, result)
        elif key in IseDispatcher.HASH_KEY_DICT:
            if isinstance(result, str):
                if not result.startswith('0x'):
                    response[key] = f'0x{result}'
