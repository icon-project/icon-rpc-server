import pytest

from iconrpcserver.dispatcher import GenericJsonRpcServerError
from iconrpcserver.dispatcher.v2 import Version2Dispatcher
from iconrpcserver.dispatcher.v3.icx import IcxDispatcher
from iconrpcserver.protos import message_code
from iconrpcserver.server.rest_property import RestProperty
from iconrpcserver.utils import json_rpc


@pytest.fixture
def rest_property():
    rest_prop = RestProperty()
    RestProperty().rs_target = "rs_target"
    rest_prop.relay_target = {"channel_name": "relay_target"}

    yield rest_prop

    RestProperty().rs_target = None
    RestProperty().relay_target = None


@pytest.mark.asyncio
class TestVersion2Dispatcher:
    async def test_relay_icx_tx_return_error_code_if_no_relay_target(self, rest_property):
        path = ""
        message = ""
        channel_name = "invalid_channel_name"
        relay_target = None

        response = await Version2Dispatcher._Version2Dispatcher__relay_icx_transaction(path, message, channel_name, relay_target)

        assert response.get("response_code") == message_code.Response.fail_invalid_peer_target


@pytest.mark.asyncio
class TestVersion3IcxDispatcher:
    async def test_relay_icx_tx_return_error_code_if_no_relay_target(self, rest_property):
        path = ""
        message = ""
        channel_name = "invalid_channel_name"
        relay_target = None

        with pytest.raises(GenericJsonRpcServerError):
            await IcxDispatcher._IcxDispatcher__relay_icx_transaction(path, message, channel_name, relay_target)


class TestNotClassified:
    @pytest.mark.asyncio
    async def test_relay_tx_request(self, monkeypatch):
        message = ""
        relay_target = ""
        path = ""

        async def mock_request(self_, method_name, message):
            return f"{method_name, message}"

        monkeypatch.setattr(json_rpc.CustomAiohttpClient, "request", mock_request)
        await json_rpc.relay_tx_request(relay_target=relay_target, message=message, path=path)
