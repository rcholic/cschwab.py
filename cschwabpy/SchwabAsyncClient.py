from cschwabpy.models.token import Tokens, ITokenStore, LocalTokenStore
from typing import Optional, List, Mapping
from cschwabpy.costants import SCHWAB_API_BASE_URL, SCHWAB_AUTH_PATH, SCHWAB_TOKEN_PATH
import time
import httpx
import re
import base64


class SchwabAsyncClient(object):
    def __init__(
        self, token_store: ITokenStore, tokens: Optional[Tokens] = None
    ) -> None:
        self.token_store = token_store

        if (
            tokens is not None
            and tokens.is_access_token_valid
            and tokens.is_refresh_token_valid
        ):
            token_store.save_tokens(tokens)
        else:
            tokens = token_store.get_tokens()

    @staticmethod
    def get_tokens_manually(
        token_store: ITokenStore = LocalTokenStore(),
    ) -> None:
        """Manual steps to get tokens from Charles Schwab API."""
        from prompt_toolkit import prompt
        import urllib.parse as url_parser

        app_client_id = prompt("Enter your app key> ").strip()
        app_secret = prompt("Enter your app secret> ").strip()

        redirect_uri = prompt("Enter your redirect uri> ").strip()
        complete_auth_url = f"{SCHWAB_API_BASE_URL}/{SCHWAB_AUTH_PATH}?response_type=code&client_id={app_client_id}&redirect_uri={redirect_uri}"
        print(
            f"Copy and open the following URL in browser. Complete Login & Authorization:\n {complete_auth_url}"
        )
        auth_code_response_url = prompt(
            "Enter the entire authorization callback URL> "
        ).strip()

        auth_code = ""
        try:
            auth_code_pattern = re.compile(r"code=(.+)&?")
            # redirect_pattern = re.compile(r"redirect_uri=(http[s]*://\S+)&")
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

        key_sec = f"{app_client_id}:{app_secret}"
        key_sec_encoded = base64.b64encode(key_sec.encode("utf-8")).decode("utf-8")
        token_url = f"{SCHWAB_API_BASE_URL}/{SCHWAB_TOKEN_PATH}"

        with httpx.Client() as client:
            response = client.post(
                url=token_url,
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
                json_res["created_timestamp"] = time.time()
                tokens = Tokens(**json_res)
                token_store.save_tokens(tokens)
                print(
                    f"Tokens saved successfully at path: {token_store.token_file_path}"
                )
            else:
                print("Failed to get tokens. Please try again.")
