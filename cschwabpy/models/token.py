from cschwabpy.models import CharlieModelBase
from typing import Mapping, Any, Protocol, Optional
import os
import json
from pathlib import Path


class Tokens(CharlieModelBase):
    expires_in: int
    token_type: str = "Bearer"
    scope: str
    refresh_token: str
    access_token: str
    id_token: Optional[str] = None


class ITokenStore(Protocol):
    def get_tokens(self) -> Optional[Tokens]:
        pass

    def save_tokens(self, tokens: Tokens) -> None:
        pass


class LocalTokenStore(ITokenStore):
    def __init__(
        self, json_file_name: str = "tokens.json", file_path: Optional[str] = None
    ):
        self.file_name = json_file_name
        self.token_file_path = file_path
        if file_path is None:
            self.token_file_path = Path(Path(__file__).parent, json_file_name)
        else:
            self.token_file_path = Path(file_path)

        if not os.path.exists(self.token_file_path.parent):
            os.makedirs(self.token_file_path.parent)

    def get_tokens(self) -> Optional[Tokens]:
        try:
            with open(self.token_file_path, "r") as token_file:
                tokens_json = json.loads(token_file.read())
                return Tokens(**tokens_json)
        except:
            return None

    def save_tokens(self, tokens: Tokens) -> None:
        with open(self.token_file_path, "w") as token_file:
            token_file.write(json.dumps(tokens.to_json(), indent=4))
