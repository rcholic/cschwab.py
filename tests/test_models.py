import json
import os
import typing
import httpx
import pytest
from datetime import datetime, timedelta
from pytest_httpx import HTTPXMock
from pathlib import Path
from cschwabpy.models import (
    OptionChain,
    OptionContract,
    OptionContractType,
    OptionContractStrategy,
    MarketHours,
    MarketHourInfo,
    OptionMarket,
    EquityMarket,
)
from cschwabpy.models.trade_models import (
    AccountNumberWithHashID,
    Order,
    ExecutionLeg,
    ExecutionType,
    OrderLeg,
    PositionEffect,
    OrderLegInstruction,
    AssetType,
    OrderLegCollection,
    AccountInstrument,
    OrderActivity,
    ComplexOrderStrategyType,
    Session,
    Duration,
    OrderType,
    OrderStatus,
    OrderStrategyType,
    InstrumentProjection,
    AccountType,
    SecuritiesAccount,
)
from cschwabpy.models.token import Tokens, LocalTokenStore
from cschwabpy.SchwabAsyncClient import SchwabAsyncClient
from cschwabpy.SchwabClient import SchwabClient

from .test_token import mock_tokens

mock_file_name = "mock_schwab_api_resp.json"
token_store = LocalTokenStore(json_file_name="test_tokens.json")


def mock_account() -> AccountNumberWithHashID:
    return AccountNumberWithHashID(accountNumber="123", hashValue="hash1")


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


@pytest.mark.asyncio
async def test_market_hours(httpx_mock: HTTPXMock) -> None:
    market_hours_json = {
        "start": "2022-04-14T09:30:00-04:00",
        "end": "2022-04-14T16:00:00-04:00",
    }
    market_hour = MarketHours(**market_hours_json)
    assert market_hour is not None
    assert market_hour.start.year == 2022
    assert market_hour.start.month == 4
    assert market_hour.start.day == 14

    all_market_json = get_mock_response()["all_market_resp"]

    all_market = MarketHourInfo(**all_market_json)
    assert all_market is not None
    assert all_market.equity is not None
    assert all_market.equity.EQ.sessionHours.regularMarket is not None
    assert all_market.equity.EQ.sessionHours.preMarket is not None

    mocked_token = mock_tokens()
    mock_response = {
        **all_market_json,
        **(mocked_token.to_json()),
    }
    httpx_mock.add_response(json=mock_response)
    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        market_info = await cschwab_client.get_market_hour_info_async()
        assert market_info is not None
        assert market_info.equity is not None
        assert market_info.equity.EQ.sessionHours.regularMarket is not None
        assert market_info.is_equity_market_open is True
        assert market_info.is_option_market_open is True

    with httpx.Client() as client2:
        cschwab_client2 = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client2,
        )
        market_info2 = cschwab_client2.get_market_hour_info()
        assert market_info2 is not None
        assert market_info2.equity is not None
        assert market_info2.equity.EQ.sessionHours.regularMarket is not None
        assert market_info2.is_equity_market_open is True
        assert market_info2.is_option_market_open is True


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


def test_parsing_securities_account():
    json_mock = get_mock_response()["securities_account"]
    accounts: typing.List[SecuritiesAccount] = []
    for sec_account in json_mock:
        securities_account = SecuritiesAccount(**sec_account).securitiesAccount
        accounts.append(securities_account)
        assert securities_account is not None
        assert securities_account.accountNumber == "123"
        # assert securities_account.accountType == "MARGIN"
        assert securities_account.isDayTrader == False
        assert securities_account.roundTrips == 0
        assert securities_account.positions is not None
        assert len(securities_account.positions) == 1
        assert securities_account.initialBalances is not None

    assert len(accounts) == 1


def test_parsing_order():
    single_order_json = get_mock_response()["single_order"]
    order_obj = Order(**single_order_json)
    assert order_obj is not None
    assert order_obj.orderId == 456
    assert order_obj.cancelable == False


@pytest.mark.asyncio
async def test_get_order(httpx_mock: HTTPXMock):
    json_mock = get_mock_response()["single_order"]
    mocked_token = mock_tokens()

    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    token_store.save_tokens(mocked_token)
    httpx_mock.add_response(json=[json_mock])  # make it array type
    from_entered_time = datetime.now() - timedelta(hours=3)
    to_entered_time = datetime.now()
    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        retrieved_orders = await cschwab_client.get_orders_async(
            account_number_hash=mock_account(),
            from_entered_time=from_entered_time,
            to_entered_time=to_entered_time,
            status=OrderStatus.FILLED,
        )
        assert retrieved_orders is not None
        assert len(retrieved_orders) == 1
        assert retrieved_orders[0].orderId == 456
        assert retrieved_orders[0].cancelable == False

    with httpx.Client() as client2:
        cschwab_client = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )

        retrieved_orders2 = cschwab_client.get_orders(
            account_number_hash=mock_account(),
            from_entered_time=from_entered_time,
            to_entered_time=to_entered_time,
            status=OrderStatus.FILLED,
        )
        assert retrieved_orders2 is not None
        assert len(retrieved_orders2) == 1
        assert retrieved_orders2[0].orderId == 456
        assert retrieved_orders2[0].cancelable == False


@pytest.mark.asyncio
async def test_place_order(httpx_mock: HTTPXMock):
    mocked_token = mock_tokens()
    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    opt_order1 = Order(
        session=Session.NORMAL,
        duration=Duration.GOOD_TILL_CANCEL,
        orderType=OrderType.NET_DEBIT,
        complexOrderStrategyType=ComplexOrderStrategyType.BUTTERFLY,
        price=0.9,
        orderLegCollection=[
            OrderLegCollection(
                orderLegType=AssetType.OPTION,
                instrument=AccountInstrument(
                    assetType=AssetType.OPTION, symbol="SPXW  240701C05530000"
                ),
                instruction=OrderLegInstruction.BUY_TO_OPEN,
                positionEffect=PositionEffect.OPENING,
                quantity=1,
            ),
            OrderLegCollection(
                orderLegType=AssetType.OPTION,
                instrument=AccountInstrument(
                    assetType=AssetType.OPTION, symbol="SPXW  240701C05540000"
                ),
                instruction=OrderLegInstruction.SELL_TO_OPEN,
                positionEffect=PositionEffect.OPENING,
                quantity=2,
            ),
            OrderLegCollection(
                orderLegType=AssetType.OPTION,
                instrument=AccountInstrument(
                    assetType=AssetType.OPTION, symbol="SPXW  240701C05550000"
                ),
                instruction=OrderLegInstruction.BUY_TO_OPEN,
                positionEffect=PositionEffect.OPENING,
                quantity=1,
            ),
        ],
    )

    order_id = 1000847830245
    token_store.save_tokens(mocked_token)
    location_url = (
        f"https://api.schwabapi.com/trader/v1/accounts/HASHHERE/orders/{order_id}"
    )
    headers = {"Location": location_url}
    httpx_mock.add_response(headers=headers, status_code=201)
    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        new_order_id = await cschwab_client.place_order_async(
            account_number_hash=mock_account(), order=opt_order1
        )
        assert new_order_id == order_id

    with httpx.Client() as client2:
        cschwab_client = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )

        new_order_id2 = cschwab_client.place_order(
            account_number_hash=mock_account(),
            order=opt_order1,
        )
        assert new_order_id2 == order_id


@pytest.mark.asyncio
async def test_cancel_order(httpx_mock: HTTPXMock):
    mocked_token = mock_tokens()
    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    order_id = 1000847830245
    token_store.save_tokens(mocked_token)
    httpx_mock.add_response(status_code=200)
    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        is_canceled = await cschwab_client.cancel_order_async(
            account_number_hash=mock_account(), order_id=order_id
        )
        assert is_canceled

    with httpx.Client() as client2:
        cschwab_client = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )

        is_canceled2 = cschwab_client.cancel_order(
            account_number_hash=mock_account(),
            order_id=order_id,
        )
        assert is_canceled2


@pytest.mark.asyncio
async def test_get_order_by_id(httpx_mock: HTTPXMock):
    json_mock = get_mock_response()["filled_order"]
    mocked_token = mock_tokens()

    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    token_store.save_tokens(mocked_token)
    httpx_mock.add_response(json=json_mock)  # make it array type
    order_id = 1000847830245

    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        retrieved_order = await cschwab_client.get_order_by_id_async(
            account_number_hash=mock_account(),
            order_id=order_id,
        )
        assert retrieved_order is not None
        assert retrieved_order.orderId == order_id

    with httpx.Client() as client2:
        cschwab_client = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )

        retrieved_order2 = cschwab_client.get_order_by_id(
            account_number_hash=mock_account(),
            order_id=order_id,
        )
        assert retrieved_order2 is not None
        assert retrieved_order2.orderId == order_id


@pytest.mark.asyncio
async def test_get_single_account(httpx_mock: HTTPXMock):
    json_mock = get_mock_response()["single_account"]
    mocked_token = mock_tokens()

    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    token_store.save_tokens(mocked_token)
    symbol = "$SPX"
    httpx_mock.add_response(json=json_mock)
    async with httpx.AsyncClient() as client:
        cschwab_client2 = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        single_account = await cschwab_client2.get_single_account_async(
            with_account_number_hash=mock_account(), include_positions=True
        )
        assert single_account is not None
        assert single_account.accountNumber == "123"
        assert single_account.type_ == AccountType.MARGIN
        assert len(single_account.positions) == 1
        assert single_account.is_margin

    with httpx.Client() as client2:
        cschwab_client2 = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )
        single_account2 = cschwab_client2.get_single_account(
            with_account_number_hash=mock_account(), include_positions=True
        )
        assert single_account2 is not None
        assert single_account2.accountNumber == "123"
        assert single_account2.type_ == AccountType.MARGIN
        assert len(single_account2.positions) == 1
        assert single_account2.is_margin


@pytest.mark.asyncio
async def test_get_securities_account(httpx_mock: HTTPXMock):
    json_mock = get_mock_response()["securities_account"]  # single_account
    mocked_token = mock_tokens()

    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    token_store.save_tokens(mocked_token)
    symbol = "$SPX"
    httpx_mock.add_response(json=json_mock)
    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )
        securities_accounts = await cschwab_client.get_accounts_async(
            include_positions=True
        )

        assert securities_accounts is not None
        assert len(securities_accounts) == 1
        assert securities_accounts[0].accountNumber == "123"
        assert securities_accounts[0].type_ == AccountType.MARGIN
        assert securities_accounts[0].type_ == AccountType.MARGIN
        assert len(securities_accounts[0].positions) == 1
        assert securities_accounts[0].is_margin

    with httpx.Client() as client2:
        cschwab_client2 = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )
        securities_accounts2 = cschwab_client2.get_accounts(include_positions=True)

        assert securities_accounts2 is not None
        assert len(securities_accounts2) == 1
        assert securities_accounts2[0].accountNumber == "123"
        assert securities_accounts2[0].type_ == AccountType.MARGIN
        assert securities_accounts2[0].type_ == AccountType.MARGIN
        assert len(securities_accounts2[0].positions) == 1
        assert securities_accounts2[0].is_margin


@pytest.mark.asyncio
async def test_download_option_chain(httpx_mock: HTTPXMock):
    mock_option_chain_resp = get_mock_response()
    mocked_token = mock_tokens()

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
        opt_chain_result = await cschwab_client.download_option_chain_async(
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

    print("----------" * 5)
    with httpx.Client() as client2:
        cschwab_client2 = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )
        opt_chain_result2 = cschwab_client2.download_option_chain(
            underlying_symbol=symbol, from_date="2025-01-03", to_date="2025-01-03"
        )
        assert opt_chain_result2 is not None
        assert opt_chain_result2.status == "SUCCESS"

        opt_df_pairs = opt_chain_result2.to_dataframe_pairs_by_expiration()
        assert opt_df_pairs is not None
        for df in opt_df_pairs:
            print(df.expiration)
            print(
                f"call dataframe size: {df.call_df.shape}. expiration: {df.expiration}"
            )
            print(f"put dataframe size: {df.put_df.shape}. expiration: {df.expiration}")
            print(df.call_df.head(5))
            print(df.put_df.head(5))


@pytest.mark.asyncio
async def test_get_option_expirations(httpx_mock: HTTPXMock):
    mock_option_chain_resp = get_mock_response()
    mocked_token = mock_tokens()

    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    mock_response = {
        **mock_option_chain_resp["option_expirations_list"],
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
        opt_expirations_list = await cschwab_client.get_option_expirations_async(
            underlying_symbol=symbol
        )
        assert opt_expirations_list is not None
        assert len(opt_expirations_list) > 0
        assert opt_expirations_list[0].expirationDate == "2022-01-07"
        assert opt_expirations_list[0].daysToExpiration == 2
        assert opt_expirations_list[0].expirationType == "W"
        assert opt_expirations_list[0].standard

    with httpx.Client() as client2:
        cschwab_client2 = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )
        opt_expirations_list2 = cschwab_client2.get_option_expirations(
            underlying_symbol=symbol
        )
        assert opt_expirations_list2 is not None
        assert len(opt_expirations_list2) > 0
        assert opt_expirations_list2[0].expirationDate == "2022-01-07"
        assert opt_expirations_list2[0].daysToExpiration == 2
        assert opt_expirations_list2[0].expirationType == "W"
        assert opt_expirations_list2[0].standard


@pytest.mark.asyncio
async def test_get_account_numbers(httpx_mock: HTTPXMock):
    # Mock response for account numbers API
    mock_data = get_mock_response()
    mocked_token = mock_tokens()

    token_store.save_tokens(mocked_token)
    if os.path.exists(Path(token_store.token_output_path)):
        os.remove(token_store.token_output_path)  # clean up before test

    mock_account_numbers_response = mock_data["account_numbers"]
    # Combine mock response with token JSON
    httpx_mock.add_response(json=mock_account_numbers_response)

    async with httpx.AsyncClient() as client:
        cschwab_client = SchwabAsyncClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            tokens=mocked_token,
            http_client=client,
        )

        account_numbers = await cschwab_client.get_account_numbers_async()
        # Assertions to verify the correctness of the API call
        assert account_numbers is not None
        assert (
            len(account_numbers) == 2
        )  # Expecting 2 account numbers in the mock response
        assert account_numbers[0].accountNumber == "123456789"
        assert account_numbers[0].hashValue == "hash1"
        assert account_numbers[1].accountNumber == "987654321"
        assert account_numbers[1].hashValue == "hash2"

    with httpx.Client() as client2:
        cschwab_client2 = SchwabClient(
            app_client_id="fake_id",
            app_secret="fake_secret",
            token_store=token_store,
            http_client=client2,
        )
        account_numbers2 = cschwab_client2.get_account_numbers()
        # Assertions to verify the correctness of the API call
        assert account_numbers2 is not None
        assert (
            len(account_numbers2) == 2
        )  # Expecting 2 account numbers in the mock response
        assert account_numbers2[0].accountNumber == "123456789"
        assert account_numbers2[0].hashValue == "hash1"
        assert account_numbers2[1].accountNumber == "987654321"
        assert account_numbers2[1].hashValue == "hash2"
