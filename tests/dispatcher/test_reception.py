import pytest

from iconrpcserver.dispatcher.default.websocket import Reception


@pytest.mark.asyncio
class TestReception:
    async def test_register_citizen_and_channel_returns_true(self, mock_channel_stub_factory):
        params_for_register_citizen_mock = {"return_value": True}
        mock_channel_stub = mock_channel_stub_factory(**params_for_register_citizen_mock)

        async with Reception(channel_name="", peer_id="", remote_target="") as registered:
            assert mock_channel_stub.mock_register_citizen.called
            assert registered

        assert mock_channel_stub.mock_unregister_citizen.called

    async def test_register_citizen_and_channel_returns_false(self, mock_channel_stub_factory):
        params_for_register_citizen_mock = {"return_value": False}
        mock_channel_stub = mock_channel_stub_factory(**params_for_register_citizen_mock)

        async with Reception(channel_name="", peer_id="", remote_target="") as registered:
            assert mock_channel_stub.mock_register_citizen.called
            assert not registered

        assert mock_channel_stub.mock_unregister_citizen.called

    async def test_register_citizen_and_raised_exc_during_communicate(self, mock_channel_stub_factory):
        params_for_register_citizen_mock = {"side_effect": RuntimeError("SUBSCRIBE_LIMIT or Already registered!!")}
        mock_channel_stub = mock_channel_stub_factory(**params_for_register_citizen_mock)

        async with Reception(channel_name="", peer_id="", remote_target="") as registered:
            assert mock_channel_stub.mock_register_citizen.called
            assert not registered

        assert mock_channel_stub.mock_unregister_citizen.called
