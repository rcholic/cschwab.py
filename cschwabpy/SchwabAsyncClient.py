from cschwabpy.models.token import Tokens, ITokenStore, LocalTokenStore
from cschwabpy.models import (
    OptionChainQueryFilter,
    OptionContractType,
    OptionChain,
    OptionExpiration,
    OptionExpirationChainResponse,
)
from cschwabpy.models.trade_models import AccountNumberModel
from typing import Optional, List, Mapping
from cschwabpy.costants import (
    SCHWAB_API_BASE_URL,
    SCHWAB_MARKET_DATA_API_BASE_URL,
    SCHWAB_TRADER_API_BASE_URL,
    SCHWAB_AUTH_PATH,
    SCHWAB_TOKEN_PATH,
)
import time
import httpx
import re
import base64


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
            "Authorization": f"{self.__tokens.token_type} {self.__tokens.access_token}",
            "Accept": "application/json",
        }

    async def get_account_numbers_async(self) -> List[AccountNumberModel]:
        await self._ensure_valid_access_token()
        import json

        target_url = f"{SCHWAB_TRADER_API_BASE_URL}/accounts/accountNumbers"
        client = httpx.AsyncClient() if self.__client is None else self.__client
        try:
            response = await client.get(
                url=target_url, params={}, headers=self.__auth_header()
            )
            json_res = response.json()
            print("json_res: ", json_res)
            account_numbers: List[AccountNumberModel] = []
            for account_json in json_res:
                account_numbers.append(AccountNumberModel(**account_json))
            return account_numbers
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
