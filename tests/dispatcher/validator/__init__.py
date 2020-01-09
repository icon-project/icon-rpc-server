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

import hashlib
import time


def create_address(data: bytes, is_eoa: bool = True):
    hash_value = hashlib.sha3_256(data).digest()
    return f'{"hx" if is_eoa else "cx"}{hash_value[-20:].hex()}'


def create_tx_hash(data: bytes=None, is_v3: bool = True):
    if data is None:
        data = int(time.time()).to_bytes(8, 'big')

    return f'{"0x" if is_v3 else ""}{hashlib.sha3_256(data).hexdigest()}'
