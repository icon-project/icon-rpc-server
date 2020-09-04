import copy
from typing import TYPE_CHECKING

import pytest
from mock import AsyncMock

from iconrpcserver.dispatcher.v2 import Version2Dispatcher
from iconrpcserver.utils import message_code
from iconrpcserver.utils.json_rpc import relay_tx_request
from tests.dispatcher.conftest import TestDispatcher, REQUESTS_V2, TX_RESULT_HASH

if TYPE_CHECKING:
    from aiohttp import ClientResponse


@pytest.mark.asyncio
class TestVersion2Dispatcher(TestDispatcher):
    REQUESTS = REQUESTS_V2
    URI = "/api/v2"

    async def test_icx_sendTransaction(self, mock_channel_tx_creator, test_cli):
        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is a validator
        mock_channel_tx_creator(response_code=message_code.Response.success)

        # When I call dispatch method
        # json_response: dict = await Version2Dispatcher.icx_sendTransaction(**json_request)
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()
        result = result_json.get('result')

        # Then I should receive response code and tx hash as dict type
        assert result.get("response_code") == message_code.Response.success
        assert result.get("tx_hash") == TX_RESULT_HASH

    async def test_icx_sendTransaction_must_relay_if_no_permission(
            self, mock_channel_tx_creator, monkeypatch, test_cli
    ):
        # Mocking to check tx is relayed or not!
        mock_relay_tx_request = AsyncMock()
        monkeypatch.setattr(f"{Version2Dispatcher.__module__}.{relay_tx_request.__name__}", mock_relay_tx_request)
        mock_relay_tx_request.return_value = 'relay mock result'

        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is not a validator
        mock_channel_tx_creator(response_code=message_code.Response.fail_no_permission)

        # When I call dispatch method
        response: 'ClientResponse' = await test_cli.post(self.URI, json=json_request)

        # Then the server should relay tx to another node
        mock_relay_tx_request.assert_called()

    async def test_icx_getTransactionResult(self, mock_channel, test_cli):
        # Given I receives icx_getTransactionResult  request
        json_request = copy.deepcopy(self.REQUESTS["icx_getTransactionResult"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getTransactionResult_batch(self, mock_channel, test_cli):
        # Given I receives icx_getTransactionResult batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getTransactionResult_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getBalance(self, test_cli):
        # Given I receives icx_getBalance request
        json_request = copy.deepcopy(self.REQUESTS["icx_getBalance"])

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getBalance_batch(self, test_cli):
        # Given I receives icx_getBalance batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getBalance_batch"])

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getBlockByHeight(self, mock_channel, test_cli):
        # Given I receives icx_getBlockByHeight request
        json_request = copy.deepcopy(self.REQUESTS["icx_getBlockByHeight"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getBlockByHeight_batch(self, mock_channel, test_cli):
        # Given I receives icx_getBlockByHeight batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getBlockByHeight_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getBlockByHash(self, mock_channel, test_cli):
        # Given I receives icx_getBlockByHash request
        json_request = copy.deepcopy(self.REQUESTS["icx_getBlockByHash"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getBlockByHash_batch(self, mock_channel, test_cli):
        # Given I receives icx_getBlockByHash batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getBlockByHash_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getLastBlock(self, mock_channel, test_cli):
        # Given I receives icx_getLastBlock request
        json_request = copy.deepcopy(self.REQUESTS["icx_getLastBlock"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"
