import pytest

from iconrpcserver.utils.message_queue.channel_inner_stub import ChannelInnerStub
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

CHANNEL_STUB_NAME = "icon_dex"


class MockChannelInnerStub:
    def async_task(self):
        return self

    async def register_citizen(self, peer_id, target, connected_time):
        pass

    async def unregister_citizen(self, peer_id):
        pass

    async def wait_for_unregister_signal(self, peer_id):
        pass


@pytest.fixture(autouse=True)
def patch_stubcollection():
    mock_channel_stub: ChannelInnerStub = MockChannelInnerStub()
    StubCollection().channel_stubs[CHANNEL_STUB_NAME] = mock_channel_stub
