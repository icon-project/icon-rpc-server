import pytest
from mock import AsyncMock

from iconrpcserver.dispatcher.default.websocket import Reception
from iconrpcserver.utils.message_queue.stub_collection import StubCollection
from .conftest import CHANNEL_STUB_NAME, MockChannelInnerStub


@pytest.mark.asyncio
class TestReception:
    async def test_register_citizen_and_channel_returns_true(self):
        channel_stub: MockChannelInnerStub = StubCollection().channel_stubs[CHANNEL_STUB_NAME]
        channel_stub.register_citizen = AsyncMock(return_value=True)
        channel_stub.unregister_citizen = AsyncMock()

        async with Reception(channel_name=CHANNEL_STUB_NAME, peer_id="", remote_target="") as registered:
            assert channel_stub.register_citizen.called
            assert registered

        assert channel_stub.unregister_citizen.called

    async def test_register_citizen_and_channel_returns_false(self):
        channel_stub: MockChannelInnerStub = StubCollection().channel_stubs[CHANNEL_STUB_NAME]
        channel_stub.register_citizen = AsyncMock(return_value=False)
        channel_stub.unregister_citizen = AsyncMock()

        async with Reception(channel_name=CHANNEL_STUB_NAME, peer_id="", remote_target="") as registered:
            assert channel_stub.register_citizen.called
            assert not registered

        assert channel_stub.unregister_citizen.called

    async def test_register_citizen_and_raised_exc_during_communicate(self):
        channel_stub: MockChannelInnerStub = StubCollection().channel_stubs[CHANNEL_STUB_NAME]
        channel_stub.register_citizen = AsyncMock(side_effect=RuntimeError("SUBSCRIBE_LIMIT or Already registered!!"))
        channel_stub.unregister_citizen = AsyncMock()

        async with Reception(channel_name=CHANNEL_STUB_NAME, peer_id="", remote_target="") as registered:
            assert channel_stub.register_citizen.called
            assert not registered

        assert channel_stub.unregister_citizen.called
