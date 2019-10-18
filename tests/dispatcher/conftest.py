import functools

import pytest


class MockChannelInnerStub:
    def __init__(self, mock_register_citizen, mock_unregister_citizen):
        self.mock_register_citizen = mock_register_citizen
        self.mock_unregister_citizen = mock_unregister_citizen

    def async_task(self):
        return self

    async def register_citizen(self, peer_id, target, connected_time):
        return self.mock_register_citizen()

    async def unregister_citizen(self, peer_id):
        return self.mock_unregister_citizen()


@pytest.fixture
def mock_channel_stub_factory(mocker):
    def _mock_channel_stub(mocker_fixture, **kwargs_register_citizen_mock):
        channel_register_citizen = mocker_fixture.MagicMock(**kwargs_register_citizen_mock)
        channel_unregister_citizen = mocker_fixture.MagicMock()
        mock_channel_stub = MockChannelInnerStub(mock_register_citizen=channel_register_citizen,
                                                 mock_unregister_citizen=channel_unregister_citizen)

        def mock_get_channel_stub_by_channel_name(channel_name):
            return mock_channel_stub

        mocker.patch("iconrpcserver.dispatcher.default.websocket.get_channel_stub_by_channel_name", mock_get_channel_stub_by_channel_name)

        return mock_channel_stub

    return functools.partial(_mock_channel_stub, mocker_fixture=mocker)


