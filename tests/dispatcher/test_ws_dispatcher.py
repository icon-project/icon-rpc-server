import json

import pytest
from mock import AsyncMock
from jsonrpcclient.requests import Request

from iconrpcserver.dispatcher.default.websocket import WSDispatcher
from iconrpcserver.utils import message_code
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from .conftest import CHANNEL_STUB_NAME


class MockWebSocket:
    async def send(self, *args, **kwargs):
        pass


@pytest.fixture
def request_dict():
    ws = MockWebSocket()
    ws.send = AsyncMock()

    peer_id = "0xaaaaaa"
    context = {
        "channel": "icon_dex",
        "peer_id": peer_id,
        "ws": ws,
        "remote_target": f"iii.pp.ii.ppp:pppp"
    }

    return {
        "context": context,
        "height": 1,
        "peer_id": peer_id
    }


@pytest.mark.asyncio
class TestWSDispatcherBasic:
    async def test_send_exception_check_parameters(self):
        ws = MockWebSocket()
        ws.send = AsyncMock()
        expected_method = "fake_method"
        expected_exc = RuntimeError("test")
        expected_error_code = message_code.Response.fail_subscribe_limit

        expected_request = Request(method=expected_method, error=str(expected_exc), code=expected_error_code)
        expected_called_params = dict(expected_request)

        await WSDispatcher.send_exception(ws, method=expected_method, exception=expected_exc, error_code=expected_error_code)

        actual_called_params, _ = ws.send.call_args
        actual_called_params: dict = json.loads(actual_called_params[0])

        # Remove id because jsonrpc call auto-increments request id.
        expected_called_params.pop("id")
        actual_called_params.pop("id")

        assert actual_called_params == expected_called_params


@pytest.mark.asyncio
class TestWSDispatcherRegister:
    async def test_do_publish_if_register_succeed(self, request_dict):
        channel_stub = StubCollection().channel_stubs[CHANNEL_STUB_NAME]
        channel_stub.register_citizen = AsyncMock(return_value=True)

        WSDispatcher.publish_heartbeat = AsyncMock()
        WSDispatcher.publish_new_block = AsyncMock()
        WSDispatcher.publish_unregister = AsyncMock()

        await WSDispatcher.node_ws_Subscribe(**request_dict)

        assert WSDispatcher.publish_heartbeat.called
        assert WSDispatcher.publish_new_block.called
        assert WSDispatcher.publish_unregister.called

    async def test_no_publish_if_register_fail(self, request_dict):
        channel_stub = StubCollection().channel_stubs[CHANNEL_STUB_NAME]
        channel_stub.register_citizen = AsyncMock(return_value=False)

        WSDispatcher.publish_heartbeat = AsyncMock()
        WSDispatcher.publish_new_block = AsyncMock()
        WSDispatcher.publish_unregister = AsyncMock()

        await WSDispatcher.node_ws_Subscribe(**request_dict)

        assert not WSDispatcher.publish_heartbeat.called
        assert not WSDispatcher.publish_new_block.called
        assert WSDispatcher.publish_unregister.called

    async def test_no_publish_if_exc_during_register(self, request_dict):
        channel_stub = StubCollection().channel_stubs[CHANNEL_STUB_NAME]
        channel_stub.register_citizen = AsyncMock(return_value=False)

        WSDispatcher.publish_heartbeat = AsyncMock()
        WSDispatcher.publish_new_block = AsyncMock()
        WSDispatcher.publish_unregister = AsyncMock()

        await WSDispatcher.node_ws_Subscribe(**request_dict)

        assert not WSDispatcher.publish_heartbeat.called
        assert not WSDispatcher.publish_new_block.called
        assert WSDispatcher.publish_unregister.called

