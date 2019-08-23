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

import copy
import logging
import traceback

from . import ValueType
from .templates import (templates, CHANGE,
                        AddChange, RemoveChange, ConvertChange)


def convert_params(params, param_type):
    if param_type is None:
        return params

    obj = _convert(params, templates[param_type])
    return obj


def _convert(obj, template):
    if not obj or not template:
        return obj
    if isinstance(template, dict) and CHANGE in template:
        obj = _change_key(obj, template[CHANGE])

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


def _change_key(obj, change_dict):
    new_obj = copy.copy(obj)
    for key, change_value in change_dict.items():
        if isinstance(change_value, AddChange):
            if key not in new_obj:
                new_obj[key] = change_value.value
        elif isinstance(change_value, RemoveChange):
            if key in new_obj:
                del new_obj[key]
        elif isinstance(change_value, ConvertChange):
            if key in new_obj:
                del new_obj[key]
                new_obj[change_value.key] = obj[key]
        else:
            raise RuntimeError(f"Not expected change, {change_value}")

    return new_obj


def _convert_value(value, value_type):
    try:
        if value_type == ValueType.none:
            return value
        elif value_type == ValueType.text:
            return _convert_value_text(value)
        elif value_type == ValueType.integer:
            return _convert_value_integer(value)
        elif value_type == ValueType.integer_str:
            return _convert_value_integer_str(value)
        elif value_type == ValueType.hex_number:  # hash...(block_hash, tx_hash)
            return _convert_value_hex_number(value)
        elif value_type == ValueType.hex_0x_number:
            return _convert_value_hex_0x_number(value)
        elif value_type == ValueType.hex_hash_number:
            return _convert_value_hex_hash_number(value)
        elif value_type == ValueType.hex_0x_hash_number:
            return _convert_value_hex_0x_hash_number(value)

    except BaseException as e:
        traceback.print_exc()
        logging.error(f"Error : {e}, value : {value_type}:{value}")

    return value


def _convert_value_text(value):
    if isinstance(value, str):
        return value
    return str(value)


def _convert_value_integer(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value.startswith('0x') or value.startswith('-0x'):
            return int(value, 16)
        try:
            return int(value)
        except:
            pass
        return int(value, 16)


def _convert_value_integer_str(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        try:
            if value.startswith('0x') or value.startswith('-0x'):
                return str(int(value, 16))
            else:
                return str(int(value))
        except BaseException as e:
            traceback.print_exc()
            pass


def _convert_value_hex_number(value):
    if isinstance(value, int):
        return hex(value).replace('0x', '')
    if isinstance(value, str):
        hex(int(value, 16))  # if no raise
        return value.replace('0x', '')


def _convert_value_hex_0x_number(value):
    if isinstance(value, int):
        return hex(value)
    if isinstance(value, str):
        if value.startswith('0x') or value.startswith('-0x'):
            return value

        return hex(int(value))


def _convert_value_hex_hash_number(value):
    if isinstance(value, int):
        return hex(value).split("0x")[1]
    if isinstance(value, str):
        if value.startswith('0x') or value.startswith('-0x'):
            return value.split("0x")[1]
        else:
            return value


def _convert_value_hex_0x_hash_number(value):
    if isinstance(value, int):
        return hex(value)
    if isinstance(value, str):
        if value.startswith('0x') or value.startswith('-0x'):
            return value

        num = int(value, 16)
        hex(int(value, 16))
        if num > 0:
            return '0x' + value
        else:
            return '-0x' + value


def make_request(method, params, request_type=None):
    raw_request = {
        "method": method,
        "params": params
    }

    return convert_params(raw_request, request_type)
