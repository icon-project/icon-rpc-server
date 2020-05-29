import copy

import pytest
from mock import MagicMock, AsyncMock

from iconrpcserver.dispatcher.v2 import Version2Dispatcher
from iconrpcserver.dispatcher.v3.icx import IcxDispatcher
from iconrpcserver.utils import message_code
from iconrpcserver.utils.json_rpc import relay_tx_request
from iconrpcserver.utils.message_queue.channel_inner_stub import ChannelTxCreatorInnerStub, ChannelTxCreatorInnerTask
from iconrpcserver.utils.message_queue.icon_score_inner_stub import IconScoreInnerStub, IconScoreInnerTask
from iconrpcserver.utils.message_queue.stub_collection import StubCollection

CHANNEL_NAME = "icon_dex"
TX_RESULT_HASH = "0x4bf74e6aeeb43bde5dc8d5b62537a33ac8eb7605ebbdb51b015c1881b45b3aed"


def create_channel_tx_creator_stub(**kwargs) -> ChannelTxCreatorInnerStub:
    """Create ChannelTxCreatorStub.

    Note that return value is actually `mock.Mock`.
    """
    task: ChannelTxCreatorInnerTask = AsyncMock(ChannelTxCreatorInnerTask)
    task.create_icx_tx.return_value = [
        kwargs.get("response_code"),
        kwargs.get("tx_hash", TX_RESULT_HASH),
        "relay_target"
    ]

    stub: ChannelTxCreatorInnerStub = MagicMock(ChannelTxCreatorInnerStub)
    stub.async_task.return_value = task

    return stub


def create_icon_score_stub(**kwargs) -> IconScoreInnerStub:
    """Create IconScoreInnerStub.

    Note that return value is actually `mock.Mock`.
    """
    task: IconScoreInnerTask = AsyncMock(IconScoreInnerTask)
    task.validate_transaction.return_value = "result"

    stub: IconScoreInnerStub = MagicMock(IconScoreInnerStub)
    stub.async_task.return_value = task

    return stub


@pytest.fixture(autouse=True)
def mocking_stub_collection():
    """Setup StubCollection and Teardown it after each test ends."""
    StubCollection().conf = {
        "channel": CHANNEL_NAME
    }
    StubCollection().icon_score_stubs[CHANNEL_NAME] = create_icon_score_stub()

    yield

    StubCollection().amqp_target = None
    StubCollection().amqp_key = None
    StubCollection().conf = None

    StubCollection().peer_stub = None
    StubCollection().channel_stubs = {}
    StubCollection().channel_tx_creator_stubs = {}
    StubCollection().icon_score_stubs = {}


class _TestDispatcher:
    # https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#coin-transfer
    REQUESTS = {
        "icx_sendTransaction": {
            "context": {
                "url": "https://URL.com",
                "channel": "icon_dex",
            },
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
    }

    @pytest.fixture
    def mock_channel_tx_creator(self):
        """Setup mocked ChannelTxCreator."""
        def _(response_code, tx_hash=TX_RESULT_HASH):
            channel_tx_creator_stub = create_channel_tx_creator_stub(response_code=response_code, tx_hash=tx_hash)
            StubCollection().channel_tx_creator_stubs[CHANNEL_NAME] = channel_tx_creator_stub

        return _


@pytest.mark.asyncio
class TestDispatcherV2(_TestDispatcher):
    async def test_icx_sendTransaction(self, mock_channel_tx_creator):
        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is a validator
        mock_channel_tx_creator(response_code=message_code.Response.success)

        # When I call dispatch method
        json_response: dict = await Version2Dispatcher.icx_sendTransaction(**json_request)

        # Then I should receive response code and tx hash as dict type
        assert json_response["response_code"] == message_code.Response.success
        assert json_response["tx_hash"] == TX_RESULT_HASH

    async def test_icx_sendTransaction_must_relay_if_no_permission(self, mock_channel_tx_creator, monkeypatch):
        # Mocking to check tx is relayed or not!
        mock_relay_tx_request = AsyncMock()
        monkeypatch.setattr(f"{Version2Dispatcher.__module__}.{relay_tx_request.__name__}", mock_relay_tx_request)

        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is not a validator
        mock_channel_tx_creator(response_code=message_code.Response.fail_no_permission)

        # When I call dispatch method
        json_response: dict = await Version2Dispatcher.icx_sendTransaction(**json_request)

        # Then the server should relay tx to another node
        mock_relay_tx_request.assert_called()


@pytest.mark.asyncio
class TestDispatcherV3Icx(_TestDispatcher):
    async def test_icx_sendTransaction(self, mock_channel_tx_creator):
        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is a validator
        mock_channel_tx_creator(response_code=message_code.Response.success)

        # When I call dispatch method
        tx_hash: str = await IcxDispatcher.icx_sendTransaction(**json_request)

        # Then I should receive valid tx_hash
        assert tx_hash.startswith("0x") and len(tx_hash) == 2 + 64

    async def test_icx_sendTransaction_must_relay_if_no_permission(self, mock_channel_tx_creator, monkeypatch):
        # Mocking to check tx is relayed or not!
        mock_relay_tx_request = AsyncMock()
        monkeypatch.setattr(f"{IcxDispatcher.__module__}.{relay_tx_request.__name__}", mock_relay_tx_request)

        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is a validator
        mock_channel_tx_creator(response_code=message_code.Response.fail_no_permission)

        # When I call dispatch method
        tx_hash: str = await IcxDispatcher.icx_sendTransaction(**json_request)

        # Then the server should relay tx to another node
        mock_relay_tx_request.assert_called()
