from typing import Optional, Any


class IconFunctionV3:
    HASH_KEY_DICT = ['hash', 'blockHash', 'txHash', 'prevBlockHash']

    @staticmethod
    def before_query(method_name: str, request, **kwargs):
        pass

    @staticmethod
    def after_query(method_name: str, response, **kwargs):
        if method_name == "ise_status":
            IconFunctionV3._handle_after_query_ise_status(response)

    @staticmethod
    def _handle_after_query_ise_status(response):
        error = response.get('error')
        if error is None:
            IconFunctionV3._hash_convert(None, response)

    @staticmethod
    def _hash_convert(key: Optional[str], response: Any):
        if key is None:
            result = response
        else:
            result = response[key]
        if isinstance(result, dict):
            for key in result:
                IconFunctionV3._hash_convert(key, result)
        elif key in IconFunctionV3.HASH_KEY_DICT:
            if isinstance(result, str):
                if not result.startswith('0x'):
                    response[key] = f'0x{result}'
