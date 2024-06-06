import json
import os
import typing
import httpx
import pytest
from pytest_httpx import HTTPXMock
from pathlib import Path
from cschwabpy.models import (
    OptionChain,
    OptionContract,
    OptionContractType,
    OptionContractStrategy,
)
from cschwabpy.models.token import Tokens, LocalTokenStore
from cschwabpy.SchwabAsyncClient import SchwabAsyncClient

from .test_token import mock_tokens

mock_file_name = "mock_schwab_api_resp.json"


def get_mock_response(
    mock_json_file_name: str = mock_file_name,
    mocked_token: typing.Optional[Tokens] = None,
) -> typing.Mapping[str, typing.Any]:
    mock_api_res_file_path = Path(
        Path(__file__).resolve().parent, "data", mock_json_file_name
    )

    with open(mock_api_res_file_path, "r") as json_file:
        json_dict = json.load(json_file)
        if mocked_token is not None:
            json_dict = {**json_dict, **(mocked_token.to_json())}
        return json_dict


def test_option_chain_parsing() -> None:
    opt_chain_api_resp = get_mock_response()["option_chain_resp"]
    opt_chain_result = OptionChain(**opt_chain_api_resp)
    assert opt_chain_result is not None
    assert opt_chain_result.status == "SUCCESS"

    opt_df_pairs = opt_chain_result.to_dataframe_pairs_by_expiration()
    assert opt_df_pairs is not None
    for df in opt_df_pairs:
        print(df.expiration)
        print(f"call dataframe size: {df.call_df.shape}. expiration: {df.expiration}")
        print(f"put dataframe size: {df.put_df.shape}. expiration: {df.expiration}")
        print(df.call_df.head(5))
        print(df.put_df.head(5))


@pytest.mark.asyncio
async def test_download_option_chain(httpx_mock: HTTPXMock):
    mock_option_chain_resp = get_mock_response()
    mocked_token = mock_tokens()
    token_store = LocalTokenStore()
    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    mock_response = {
        **mock_option_chain_resp["option_chain_resp"],
        **(mocked_token.to_json()),
    }
    symbol = "$SPX"
    httpx_mock.add_response(json=mock_response)
    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        opt_chain_result = await cschwab_client.download_option_chain(
            underlying_symbol=symbol, from_date="2025-01-03", to_date="2025-01-03"
        )
        assert opt_chain_result is not None
        assert opt_chain_result.status == "SUCCESS"

        opt_df_pairs = opt_chain_result.to_dataframe_pairs_by_expiration()
        assert opt_df_pairs is not None
        for df in opt_df_pairs:
            print(df.expiration)
            print(
                f"call dataframe size: {df.call_df.shape}. expiration: {df.expiration}"
            )
            print(f"put dataframe size: {df.put_df.shape}. expiration: {df.expiration}")
            print(df.call_df.head(5))
            print(df.put_df.head(5))
