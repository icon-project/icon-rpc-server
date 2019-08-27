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

import re
import time
from urllib.parse import urlsplit


def camel_to_upper_snake(camel: str) -> str:
    """convert lower/upper camel case to upper snake case

    Example:
        camelCase -> CAMEL_CASE
        CamelCase -> CAMEL_CASE
    :param camel:
    :return:
    """
    REG = r'(.[a-z]+)([A-Z])?'

    def snake(match):
        group2 = match.group(2)
        group2 = '_' + group2 if group2 else ''
        return match.group(1).upper() + group2

    return re.sub(REG, snake, camel)


def upper_camel_to_lower_camel(upper_camel: str) -> str:
    """convert upper camel case to lower camel case

    Example:
        CamelCase -> camelCase
    :param upper_camel:
    :return:
    """
    return upper_camel[0].lower() + upper_camel[1:]


def convert_upper_camel_method_to_lower_camel(method_name: str) -> str:
    """convert upper camel method to lower camel method

    Example:
        prefix_MethodName -> prefix_methodName

    :param method_name:
    :return:
    """
    prefix = method_name.split('_')[0]
    method = upper_camel_to_lower_camel(method_name.split('_')[1])
    return prefix + '_' + method


def get_now_timestamp():
    return hex(int(time.time() * 1_000_000))


def get_protocol_from_uri(uri: str) -> str:
    return urlsplit(uri).scheme