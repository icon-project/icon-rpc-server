import json

import pytest
from jsonrpcclient.request import Request

from iconrpcserver.dispatcher.default.websocket import WSDispatcher
from iconrpcserver.protos import message_code


@pytest.fixture
def request_dict():
    peer_id = "0xaaaaaa"
    context = {
        "channel": "icon_dex",
        "peer_id": peer_id,
        "ws": "mock_ws",
        "remote_target": f"iii.pp.ii.ppp:pppp"
    }

    return {
        "context": context,
        "height": 1,
        "peer_id": peer_id
    }


@pytest.mark.asyncio
class TestWSDispatcher:
    @pytest.fixture
    def mock_publish_method_factory(self, mocker, mock_channel_stub_factory):
        def _mock_publish_method(**kwargs_for_mock):
            check_by_this_method = mocker.MagicMock(**kwargs_for_mock)

            async def _this_async_mock_will_substitute_origin_func(*args, **kwargs):
                return check_by_this_method(*args, **kwargs)

            return check_by_this_method, _this_async_mock_will_substitute_origin_func

        return _mock_publish_method

    async def test_do_publish_if_register_succeed(self, mocker, request_dict, mock_channel_stub_factory, mock_publish_method_factory):
        mock_value = {"return_value": True}
        mock_channel_stub_factory(**mock_value)
        publish_heartbeat, mock_publish_heartbeat = mock_publish_method_factory(**mock_value)
        publish_new_block, mock_publish_new_block = mock_publish_method_factory(**mock_value)

        mocker.patch.object(WSDispatcher, "publish_heartbeat", new=mock_publish_heartbeat)
        mocker.patch.object(WSDispatcher, "publish_new_block", new=mock_publish_new_block)
        await WSDispatcher.node_ws_Subscribe(**request_dict)

        assert publish_heartbeat.called
        assert publish_new_block.called

    async def test_no_publish_if_register_fail(self, mocker, request_dict, mock_channel_stub_factory, mock_publish_method_factory):
        mock_value = {"return_value": False}
        mock_channel_stub_factory(**mock_value)
        publish_heartbeat, mock_publish_heartbeat = mock_publish_method_factory(**mock_value)
        publish_new_block, mock_publish_new_block = mock_publish_method_factory(**mock_value)
        send_exception, mock_send_exception = mock_publish_method_factory(**mock_value)

        mocker.patch.object(WSDispatcher, "publish_heartbeat", new=mock_publish_heartbeat)
        mocker.patch.object(WSDispatcher, "publish_new_block", new=mock_publish_new_block)
        mocker.patch.object(WSDispatcher, "send_exception", new=mock_send_exception)
        await WSDispatcher.node_ws_Subscribe(**request_dict)

        assert not publish_heartbeat.called
        assert not publish_new_block.called
        assert send_exception.called

    async def test_no_publish_if_exc_during_register(self, mocker, request_dict, mock_channel_stub_factory, mock_publish_method_factory):
        reception_mock_value = {"side_effect": RuntimeError("REGISTER FAILED DURING CHANNEL STUB")}
        mock_channel_stub_factory(**reception_mock_value)

        mock_publish_value = {"return_value": True}
        publish_heartbeat, mock_publish_heartbeat = mock_publish_method_factory(**mock_publish_value)
        publish_new_block, mock_publish_new_block = mock_publish_method_factory(**mock_publish_value)
        send_exception, mock_send_exception = mock_publish_method_factory(**mock_publish_value)

        mocker.patch.object(WSDispatcher, "publish_heartbeat", new=mock_publish_heartbeat)
        mocker.patch.object(WSDispatcher, "publish_new_block", new=mock_publish_new_block)
        mocker.patch.object(WSDispatcher, "send_exception", new=mock_send_exception)
        await WSDispatcher.node_ws_Subscribe(**request_dict)

        assert not publish_heartbeat.called
        assert not publish_new_block.called
        assert send_exception.called

    async def test_send_exception(self, mocker, mock_channel_stub_factory):
        class MockWebSocket:
            def __init__(self, mocker_fixture):
                self.mock_send = mocker_fixture.MagicMock()

            async def send(self, *args, **kwargs):
                self.mock_send(*args, **kwargs)

        ws = MockWebSocket(mocker)
        expected_method = "fake_method"
        expected_exc = RuntimeError("test")
        expected_error_code = message_code.Response.fail_subscribe_limit

        await WSDispatcher.send_exception(ws, method=expected_method, exception=expected_exc, error_code=expected_error_code)

        expected_request = Request(method=expected_method, error=str(expected_exc), code=expected_error_code)
        expected_called_params = dict(expected_request)

        actual_called_params, _ = ws.mock_send.call_args
        actual_called_params: dict = json.loads(actual_called_params[0])

        # Remove id because jsonrpc call auto-increments request id.
        expected_called_params.pop("id")
        actual_called_params.pop("id")

        assert actual_called_params == expected_called_params
