import pytest
from jsonrpcclient.response import Response, SuccessResponse

from mock import MagicMock
from iconrpcserver.dispatcher.v3.icx import IcxDispatcher
from iconrpcserver.dispatcher.validator import validate_jsonschema
from iconrpcserver.utils import json_rpc


@pytest.fixture
def mock_server(monkeypatch):
    async def mock_request(self_, method_name, **message):
        expected_method_name = IcxDispatcher.icx_sendTransaction.__name__
        if method_name != expected_method_name:
            raise RuntimeError(f"Relay Tx with wrong name! "
                               f"(expected: {expected_method_name}, actual: {method_name})")

        validate_jsonschema(message)

        response = MagicMock(Response)
        response.data = SuccessResponse(result="^^!", jsonrpc="2.0", id=1)

        return response

    monkeypatch.setattr(json_rpc.AiohttpClient, "request", mock_request)


@pytest.mark.asyncio
async def test_relay_tx_request(mock_server):
    relay_target = ""
    path = ""
    # https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_sendtransaction
    message = {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 1234,
        "params": {
            "version": "0x3",
            "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
            "to": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd",
            "value": "0xde0b6b3a7640000",
            "stepLimit": "0x12345",
            "timestamp": "0x563a6cf330136",
            "nid": "0x3",
            "nonce": "0x1",
            "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA="
        }
    }

    await json_rpc.relay_tx_request(relay_target=relay_target, message=message, path=path)
