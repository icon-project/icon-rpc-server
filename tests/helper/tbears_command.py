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

from typing import TYPE_CHECKING
from tests.helper.tbears.utils import get_deploy_payload, get_send_token_payload

if TYPE_CHECKING:
    from tests.helper.wallet import Wallet


def make_deploy_payload(score_name: str, wallet: 'Wallet') -> dict:
    return get_deploy_payload(score_name, wallet)


def make_send_token_payload(wallet: 'Wallet', score_addr: str, data_addr: str, data_value: str) -> dict:
    return get_send_token_payload(wallet, score_addr, data_addr, data_value)
