from cschwabpy.models import JSONSerializableBaseModel
from pydantic import ConfigDict, Field
from typing import Mapping, Any, Protocol, Optional
import os
import json
import time
from pathlib import Path

REFRESH_TOKEN_VALIDITY_SECONDS = 7 * 24 * 60 * 60  # 7 days

UNIXTIME_FACTORY = time.time


class Tokens(JSONSerializableBaseModel):
    expires_in: int  # seconds till access__token expires
    token_type: str = "Bearer"
    scope: str
    refresh_token: str
    access_token: str
    id_token: Optional[str] = None
    # rt_created_timestamp: float = Field(default_factory=UNIXTIME_FACTORY)
    created_timestamp: float = Field(default_factory=UNIXTIME_FACTORY)

    @property
    def is_access_token_valid(self) -> bool:
        return time.time() - self.created_timestamp < self.expires_in

    @property
    def is_refresh_token_valid(self) -> bool:
        return time.time() - self.created_timestamp < REFRESH_TOKEN_VALIDITY_SECONDS

    @property
    def all_tokens_invalid(self) -> bool:
        """Whether both RT and AT are invalid."""
        return not self.is_access_token_valid and not self.is_refresh_token_valid


class ITokenStore(Protocol):
    @property
    def token_output_path(self) -> str:
        """Path for outputting tokens."""
        return ""

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

    @property
    def token_output_path(self) -> str:
        return str(self.token_file_path)

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
