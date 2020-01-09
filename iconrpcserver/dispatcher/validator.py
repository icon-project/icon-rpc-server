# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

import re

from jsonrpcserver import status
from jsonschema import Draft4Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from .exception import GenericJsonRpcServerError, JsonError


def validate_jsonschema(request: object, schemas: dict):
    """ Validate JSON-RPC v3 schema.

    refer to
    v2 : https://github.com/icon-project/icx_JSON_RPC
    v3 : https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3

    :param request: JSON-RPC request to validate
    :param schemas: The schema to validate with
    :return: N/A
    """
    # get JSON-RPC batch request
    if isinstance(request, list):
        for req in request:
            validate_jsonschema(req, schemas=schemas)
        return

    # get schema for 'method'
    schema: dict = None
    method = request.get('method', None)

    if method and isinstance(method, str):
        schema = schemas.get(method, None)
    if schema is None:
        raise GenericJsonRpcServerError(code=JsonError.METHOD_NOT_FOUND,
                                        message=f"JSON schema validation error: Method not found",
                                        http_status=status.HTTP_BAD_REQUEST)

    # create a new validator with format_checker
    validator = Draft4Validator(schema=schema, format_checker=format_checker)

    # check request
    try:
        validator.validate(request)
    except ValidationError as e:
        if e.schema_path[-1] == "additionalProperties":
            if len(e.path) == 0:
                message = f"There is an invalid key in 1st depth"
            else:
                message = f"There is an invalid key in '{e.path[-1]}'"
        elif len(e.path) > 0:
            message = f"'{e.path[-1]}' has an invalid value"
        else:
            message = f"Invalid params"

        raise GenericJsonRpcServerError(code=JsonError.INVALID_PARAMS,
                                        message=f"JSON schema validation error: {message}",
                                        http_status=status.HTTP_BAD_REQUEST)


def is_lowercase_hex_string(value: str) -> bool:
    """Check whether value is hexadecimal format or not

    :param value: text
    :return: True(lowercase hexadecimal) otherwise False
    """

    try:
        result = re.match('[0-9a-f]+', value)
        return len(result.group(0)) == len(value)
    except:
        pass

    return False


format_checker = FormatChecker()


@format_checker.checks('address')
def check_address(address: str):
    if isinstance(address, str) and len(address) == 42 and is_lowercase_hex_string(address[2:]) \
            and (address.startswith('cx') or address.startswith('hx')):
        return True

    return False


@format_checker.checks('address_eoa')
def check_address_eoa(address: str):
    if isinstance(address, str) and len(address) == 42 and is_lowercase_hex_string(address[2:]) \
            and address.startswith('hx'):
        return True

    return False


@format_checker.checks('address_score')
def check_address_score(address: str):
    if isinstance(address, str) and len(address) == 42 and is_lowercase_hex_string(address[2:]) \
            and address.startswith('cx'):
        return True

    return False


@format_checker.checks('int_10')
def check_int_10(value: str):
    if not isinstance(value, str):
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False


@format_checker.checks('int_16')
def check_int_16(value: str):
    if isinstance(value, str) and value.startswith('0x') and is_lowercase_hex_string(value[2:]):
        return True

    return False


@format_checker.checks('hash')
def check_hash(value: str):
    if isinstance(value, str) and len(value) == 66 and value.startswith('0x') and is_lowercase_hex_string(value[2:]):
        return True

    return False


@format_checker.checks('hash_v2')
def check_hash_v2(value: str):
    if isinstance(value, str) and len(value) == 64 and is_lowercase_hex_string(value):
        return True

    return False


@format_checker.checks('binary_data')
def check_binary_data(value: str):
    if isinstance(value, str) and len(value) % 2 == 0 and value.startswith('0x') and is_lowercase_hex_string(value[2:]):
        return True

    return False
