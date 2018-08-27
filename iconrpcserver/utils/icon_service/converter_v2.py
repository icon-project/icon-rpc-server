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

import copy
import logging
import traceback
from enum import Enum

key_converting = object()


class ParamType(Enum):
    get_block = 0


class ValueType(Enum):
    none = 0
    text = 1
    integer = 2
    integer_str = 3
    hex_hash_number = 4


def convert_params(params, param_type):
    if param_type is None:
        return params

    obj = _convert(params, templates[param_type])
    return obj


def _convert(obj, template):
    if not obj or not template:
        return copy.deepcopy(obj)

    if isinstance(template, dict) and key_converting in template:
        obj = _convert_key(obj, template[key_converting])

    if isinstance(obj, dict) and isinstance(template, dict):
        new_obj = dict()
        for key, value in obj.items():
            new_value = _convert(value, template.get(key, None))
            new_obj[key] = new_value

    elif isinstance(obj, list) and isinstance(template, list):
        new_obj = list()
        for item in obj:
            new_item = _convert(item, template[0])
            new_obj.append(new_item)

    elif isinstance(template, ValueType):
        new_obj = _convert_value(obj, template)

    else:
        new_obj = obj

    return new_obj


def _convert_key(obj, key_convert_dict):
    new_obj = dict()
    for key in obj:
        if key in key_convert_dict:
            old_key = key
            new_key = key_convert_dict[old_key]
            new_obj[new_key] = obj[old_key]
        else:
            new_obj[key] = obj[key]

    return new_obj


def _convert_value(value, value_type):
    try:
        if value_type == ValueType.none:
            return value
        elif value_type == ValueType.integer_str:
            return _convert_value_integer_str(value)
        elif value_type == ValueType.hex_hash_number:
            return _convert_value_hex_hash_number(value)

    except BaseException as e:
        traceback.print_exc()
        logging.error(f"Error : {e}, value : {value_type}:{value}")

    return value


def _convert_value_integer_str(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        try:
            return str(int(value, 16))
        except BaseException as e:
            traceback.print_exc()
            pass


def _convert_value_hex_hash_number(value):
    if isinstance(value, int):
        return hex(value)
    if isinstance(value, str):
        if value.startswith('0x') or value.startswith('-0x'):
            return value.split("0x")[1]
        else:
            return value


templates = dict()

templates[ParamType.get_block] = {
    "confirmed_transaction_list": [
        {
            "timestamp": ValueType.integer_str,
            "tx_hash": ValueType.hex_hash_number,
            key_converting: {
                "txHash": "tx_hash"
            }
        }
    ]
}
