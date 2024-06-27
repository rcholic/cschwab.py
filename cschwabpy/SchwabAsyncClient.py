from cschwabpy.models.token import Tokens, ITokenStore, LocalTokenStore
from cschwabpy.models import (
    OptionChainQueryFilter,
    OptionContractType,
    OptionChain,
    OptionExpiration,
    OptionExpirationChainResponse,
)
from cschwabpy.models.trade_models import (
    AccountNumberWithHashID,
    AccountInstrument,
    SecuritiesAccount,
    Account,
    OrderStatus,
    Order,
    InstrumentProjection,
)
import cschwabpy.util as util

from datetime import datetime, timedelta
from typing import Optional, List, Mapping
from cschwabpy.costants import (
    SCHWAB_API_BASE_URL,
    SCHWAB_MARKET_DATA_API_BASE_URL,
    SCHWAB_TRADER_API_BASE_URL,
    SCHWAB_AUTH_PATH,
    SCHWAB_TOKEN_PATH,
)

import httpx
import re
import base64
import json


class SchwabAsyncClient(object):
    def __init__(
        self,
        app_client_id: str,
        app_secret: str,
        token_store: ITokenStore = LocalTokenStore(),
        tokens: Optional[Tokens] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.__client_id = app_client_id
        self.__client_secret = app_secret
        self.__token_store = token_store
        self.__client = http_client
        self.__keep_client_alive = http_client is not None
        if (
            tokens is not None
            and tokens.is_access_token_valid
            and tokens.is_refresh_token_valid
        ):
            token_store.save_tokens(tokens)

        self.__tokens = token_store.get_tokens()

    @property
    def token_url(self) -> str:
        return f"{SCHWAB_API_BASE_URL}/{SCHWAB_TOKEN_PATH}"

    async def _ensure_valid_access_token(self, force_refresh: bool = False) -> bool:
        if self.__tokens is None:
            raise Exception(
                "Tokens are not available. Please use get_tokens_manually() to get tokens first."
            )

        if self.__tokens.is_access_token_valid and not force_refresh:
            return True

        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            key_sec_encoded = self.__encode_app_key_secret()
            response = await client.post(
                url=self.token_url,
                headers={
                    "Authorization": f"Basic {key_sec_encoded}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.__tokens.refresh_token,
                },
            )

            if response.status_code == 200:
                json_res = response.json()
                tokens = Tokens(**json_res)
                self.__token_store.save_tokens(tokens)
                return True
            else:
                raise Exception(
                    "Status for refreshing access token is not successful. Status: ",
                    response.status_code,
                )
        except Exception as ex:
            print("Failed to refresh access token. Please try again. exception: ", ex)
            return False
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    def __encode_app_key_secret(self) -> str:
        key_sec = f"{self.__client_id}:{self.__client_secret}"
        return base64.b64encode(key_sec.encode("utf-8")).decode("utf-8")

        # refresh access token
        # doc: https://developer.schwab.com/products/trader-api--individual/details/documentation/Retail%20Trader%20API%20Production

    def __auth_header(self) -> Mapping[str, str]:
        return {
            # "Content-Type": "application/json",
            "Authorization": f"{self.__tokens.token_type} {self.__tokens.access_token}",
            "Accept": "application/json",
        }

    async def get_account_numbers_async(self) -> List[AccountNumberWithHashID]:
        await self._ensure_valid_access_token()

        target_url = f"{SCHWAB_TRADER_API_BASE_URL}/accounts/accountNumbers"
        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            json_res = response.json()
            account_numbers: List[AccountNumberWithHashID] = []
            for account_json in json_res:
                account_numbers.append(AccountNumberWithHashID(**account_json))
            return account_numbers
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    async def get_accounts_async(
        self,
        include_positions: bool = True,
        with_account_number_hash: Optional[AccountNumberWithHashID] = None,
    ) -> List[Account]:
        """get all accounts except a specific account_number is provided."""
        await self._ensure_valid_access_token()
        target_url = f"{SCHWAB_TRADER_API_BASE_URL}/accounts"
        if with_account_number_hash is not None:
            target_url = f"{target_url}/{with_account_number_hash.hashValue}"

        if include_positions:
            target_url = f"{target_url}?fields=positions"

        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            if response.status_code == 200:
                json_res = response.json()
                if with_account_number_hash is None:
                    accounts: List[SecuritiesAccount] = []
                    for account_json in json_res:
                        securities_account = SecuritiesAccount(
                            **account_json
                        ).securitiesAccount
                        accounts.append(securities_account)
                    return accounts
                else:
                    securities_account = SecuritiesAccount(**json_res).securitiesAccount
                    return [securities_account]
            else:
                raise Exception(
                    "Failed to get accounts. Status: ", response.status_code
                )
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    async def get_single_account_async(
        self,
        with_account_number_hash: AccountNumberWithHashID,
        include_positions: bool = True,
    ) -> Optional[Account]:
        """Convenience method to get a single account by account number's encrypted ID."""
        account = await self.get_accounts_async(
            include_positions=include_positions,
            with_account_number_hash=with_account_number_hash,
        )
        if account is None or len(account) == 0:
            return None

        return account[0]

    async def get_instruments_async(
        self,
        symbol: str,
        projection: InstrumentProjection = InstrumentProjection.Fundamental,
    ) -> List[AccountInstrument]:
        await self._ensure_valid_access_token()
        target_url = f"{SCHWAB_MARKET_DATA_API_BASE_URL}/instruments?symbol={symbol}&projection={projection.value}"
        client = httpx.AsyncClient() if self.__client is None else self.__client

        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            json_res = response.json()
            instruments: List[AccountInstrument] = []
            if "instruments" in json_res:
                for instrument in json_res["instruments"]:
                    instruments.append(AccountInstrument(**instrument))
            return instruments
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    async def place_order_async(
        self, account_number_hash: AccountNumberWithHashID, order: Order
    ) -> bool:
        await self._ensure_valid_access_token()
        target_url = f"{SCHWAB_TRADER_API_BASE_URL}/accounts/{account_number_hash.hashValue}/orders"
        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            _header = self.__auth_header()
            _header["Content-Type"] = "application/json"
            response = await client.post(
                url=target_url,
                data=json.dumps(order.to_json()),
                headers=_header,
            )
            if response.status_code == 201:
                return True
            else:
                raise Exception("Failed to place order. Status: ", response.status_code)
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    async def get_order_by_id_async(
        self,
        account_number_hash: AccountNumberWithHashID,
        order_id: int,
    ) -> Optional[Order]:
        """Get a specific order by order ID."""
        await self._ensure_valid_access_token()
        target_url = f"{SCHWAB_TRADER_API_BASE_URL}/accounts/{account_number_hash.hashValue}/orders/{order_id}"
        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            if response.status_code == 200:
                order_json = response.json()
                return Order(**order_json)
            elif response.status_code == 404:
                # order not found
                return None
            else:
                raise Exception("Failed to get order. Status: ", response.status_code)
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    async def get_orders_async(
        self,
        account_number_hash: AccountNumberWithHashID,
        from_entered_time: datetime,
        to_entered_time: datetime,
        max_count: int = 1000,
        status: Optional[OrderStatus] = None,
    ) -> List[Order]:
        """Get orders for a specific account within a time range."""
        await self._ensure_valid_access_token()
        target_url = f"{SCHWAB_TRADER_API_BASE_URL}/accounts/{account_number_hash.hashValue}/orders"
        target_url += f"?fromEnteredTime={util.to_iso8601_str(from_entered_time)}&toEnteredTime={util.to_iso8601_str(to_entered_time)}&maxResults={max_count}"
        if status is not None:
            target_url += f"&status={status.value}"

        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            if response.status_code == 200:
                json_res = response.json()
                orders: List[Order] = []
                for order_json in json_res:
                    order = Order(**order_json)
                    orders.append(order)
                return orders
            else:
                raise Exception("Failed to get orders. Status: ", response.status_code)
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    async def get_option_expirations_async(
        self, underlying_symbol: str
    ) -> List[OptionExpiration]:
        await self._ensure_valid_access_token()
        target_url = f"{SCHWAB_MARKET_DATA_API_BASE_URL}/expirationchain?symbol={underlying_symbol}"
        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            json_res = response.json()
            expiration_resp = OptionExpirationChainResponse(**json_res)
            return expiration_resp.expirationList
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    async def download_option_chain_async(
        self,
        underlying_symbol: str,
        from_date: str,
        to_date: str,
        contract_type: str = "ALL",
    ) -> OptionChain:
        await self._ensure_valid_access_token()

        query_filter = OptionChainQueryFilter(
            symbol=underlying_symbol,
            contractType=OptionContractType(contract_type),
            fromDate=from_date,
            toDate=to_date,
        )
        target_url = (
            f"{SCHWAB_MARKET_DATA_API_BASE_URL}/chains?{query_filter.to_query_params()}"
        )

        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            json_res = response.json()
            return OptionChain(**json_res)
        finally:
            if not self.__keep_client_alive:
                await client.aclose()

    def get_tokens_manually(
        self,
    ) -> None:
        """Manual steps to get tokens from Charles Schwab API."""
        from prompt_toolkit import prompt
        import urllib.parse as url_parser

        redirect_uri = prompt("Enter your redirect uri> ").strip()
        complete_auth_url = f"{SCHWAB_API_BASE_URL}/{SCHWAB_AUTH_PATH}?response_type=code&client_id={self.__client_id}&redirect_uri={redirect_uri}"
        print(
            f"Copy and open the following URL in browser. Complete Login & Authorization:\n {complete_auth_url}"
        )
        auth_code_response_url = prompt(
            "Paste the entire authorization response URL here> "
        ).strip()

        auth_code = ""
        try:
            auth_code_pattern = re.compile(r"code=(.+)&?")
            d = re.search(auth_code_pattern, auth_code_response_url)
            if d:
                auth_code = d.group(1)
                auth_code = url_parser.unquote(auth_code.split("&")[0])
            else:
                raise Exception(
                    "authorization response url does not contain authorization code"
                )

            if len(auth_code) == 0:
                raise Exception("authorization code is empty")
        except Exception as ex:
            raise Exception(
                "Failed to get authorization code. Please try again. Exception: ", ex
            )

        key_sec_encoded = self.__encode_app_key_secret()
        with httpx.Client() as client:
            response = client.post(
                url=self.token_url,
                headers={
                    "Authorization": f"Basic {key_sec_encoded}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": redirect_uri,
                },
            )

            if response.status_code == 200:
                json_res = response.json()
                tokens = Tokens(**json_res)
                self.__token_store.save_tokens(tokens)
                print(
                    f"Tokens saved successfully at path: {self.__token_store.token_file_path}"
                )
            else:
                print("Failed to get tokens. Please try again.")
