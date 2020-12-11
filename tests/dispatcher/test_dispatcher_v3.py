import copy
from typing import TYPE_CHECKING

import pytest
from mock import AsyncMock

from iconrpcserver.dispatcher.v3.icx import IcxDispatcher
from iconrpcserver.utils import message_code
from iconrpcserver.utils.json_rpc import relay_tx_request
from tests.dispatcher.conftest import TestDispatcher, REQUESTS_V3

if TYPE_CHECKING:
    from aiohttp import ClientResponse


@pytest.mark.asyncio
class TestVersion3Dispatcher(TestDispatcher):
    REQUESTS = REQUESTS_V3
    URI = "/api/v3"

    async def test_icx_sendTransaction(self, mock_channel_tx_creator, test_cli):
        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is a validator
        mock_channel_tx_creator(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()
        tx_hash = result_json.get("result")

        # Then I should receive valid tx_hash
        assert tx_hash.startswith("0x") and len(tx_hash) == 2 + 64

    async def test_icx_sendTransaction_must_relay_if_no_permission(
            self, mock_channel_tx_creator, monkeypatch, test_cli
    ):
        # Mocking to check tx is relayed or not!
        mock_relay_tx_request = AsyncMock()
        monkeypatch.setattr(f"{IcxDispatcher.__module__}.{relay_tx_request.__name__}", mock_relay_tx_request)
        mock_relay_tx_request.return_value = "relay mock result"

        # Given I receives icx_sendTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_sendTransaction"])
        # And the node is a validator
        mock_channel_tx_creator(response_code=message_code.Response.fail_no_permission)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)

        # Then the server should relay tx to another node
        mock_relay_tx_request.assert_called()

    async def test_icx_getBlock(self, mock_channel, test_cli):
        # Given I receives icx_getBlock request
        json_request = copy.deepcopy(self.REQUESTS["icx_getBlock"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getBlock_batch(self, mock_channel, test_cli):
        # Given I receives icx_getBlock batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getBlock_batch"])
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

    async def test_icx_call(self, test_cli):
        # Given I receives icx_call request
        json_request = copy.deepcopy(self.REQUESTS["icx_call"])

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_call_batch(self, test_cli):
        # Given I receives icx_call batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_call_batch"])

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

    async def test_icx_getScoreApi(self, test_cli):
        # Given I receives icx_getScoreApi request
        json_request = copy.deepcopy(self.REQUESTS["icx_getScoreApi"])

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getScoreApi_batch(self, test_cli):
        # Given I receives icx_getTotalSupply batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getScoreApi_batch"])

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getTotalSupply(self, test_cli):
        # Given I receives icx_getTotalSupply request
        json_request = copy.deepcopy(self.REQUESTS["icx_getTotalSupply"])

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

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

    async def test_icx_getTransactionByHash(self, mock_channel, test_cli):
        # Given I receives icx_getTransactionByHash  request
        json_request = copy.deepcopy(self.REQUESTS["icx_getTransactionByHash"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getTransactionByHash_batch(self, mock_channel, test_cli):
        # Given I receives icx_getTransactionByHash batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getTransactionByHash_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getTransactionProof(self, mock_channel, test_cli):
        # Given I receives icx_getTransactionProof  request
        json_request = copy.deepcopy(self.REQUESTS["icx_getTransactionProof"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getTransactionProof_batch(self, mock_channel, test_cli):
        # Given I receives icx_getTransactionProof batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getTransactionProof_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getReceiptProof(self, mock_channel, test_cli):
        # Given I receives icx_getReceiptProof request
        json_request = copy.deepcopy(self.REQUESTS["icx_getReceiptProof"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getReceiptProof_batch(self, mock_channel, test_cli):
        # Given I receives icx_getReceiptProof batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getReceiptProof_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_proveTransaction(self, mock_channel, test_cli):
        # Given I receives icx_proveTransaction request
        json_request = copy.deepcopy(self.REQUESTS["icx_proveTransaction"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_proveTransaction_batch(self, mock_channel, test_cli):
        # Given I receives icx_proveTransaction batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_proveTransaction_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_proveReceipt(self, mock_channel, test_cli):
        # Given I receives icx_proveReceipt request
        json_request = copy.deepcopy(self.REQUESTS["icx_proveReceipt"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_proveReceipt_batch(self, mock_channel, test_cli):
        # Given I receives icx_proveReceipt batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_proveReceipt_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_proveReceipt(self, mock_channel, test_cli):
        # Given I receives icx_proveReceipt request
        json_request = copy.deepcopy(self.REQUESTS["icx_proveReceipt"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_proveReceipt_batch(self, mock_channel, test_cli):
        # Given I receives icx_proveReceipt batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_proveReceipt_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_ise_getStatus(self, mock_channel, test_cli):
        # Given I receives ise_getStatus request
        json_request = copy.deepcopy(self.REQUESTS["ise_getStatus"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_rep_getListByHash(self, mock_channel, test_cli):
        # Given I receives rep_getListByHash request
        json_request = copy.deepcopy(self.REQUESTS["rep_getListByHash"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_rep_getListByHash_batch(self, mock_channel, test_cli):
        # Given I receives rep_getListByHash batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["rep_getListByHash"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"

    async def test_icx_getBlockReceipts(self, mock_channel, test_cli):
        # Given I receives icx_getBlock request
        json_request = copy.deepcopy(self.REQUESTS["icx_getBlockReceipts"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request)
        result_json: dict = await response.json()

        # Then response is not error
        assert 'error' not in result_json, f"request = {json_request}"

    async def test_icx_getBlockReceipts_batch(self, mock_channel, test_cli):
        # Given I receives icx_getBlock batch request
        json_request_batch = copy.deepcopy(self.REQUESTS["icx_getBlockReceipts_batch"])
        # And the node is a validator
        mock_channel(response_code=message_code.Response.success)

        # When I call dispatch method
        response: ClientResponse = await test_cli.post(self.URI, json=json_request_batch)
        result_json: list = await response.json()

        # Then response is not error
        for json_data in result_json:
            assert 'error' not in json_data, f"request = {json_request_batch}"
