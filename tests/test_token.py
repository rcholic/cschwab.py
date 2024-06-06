# to run: python -m pytest -s tests/test_token.py

import pytest
import os
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
from cschwabpy.models.token import Tokens, LocalTokenStore, ITokenStore


def mock_tokens(created_at: Optional[datetime] = None) -> Tokens:
    if created_at is None:
        return Tokens(
            expires_in=1800,
            token_type="Bearer",
            scope="scope",
            refresh_token="refresh_token",
            access_token="access_token",
            id_token="id_token",
        )
    else:
        return Tokens(
            expires_in=1800,
            token_type="Bearer",
            scope="scope",
            refresh_token="refresh_token",
            access_token="access_token",
            id_token="id_token",
            created_timestamp=created_at.timestamp(),
        )


def test_tokens_serialization() -> None:
    tokens1 = mock_tokens()
    tokens_json = tokens1.to_json()
    assert tokens_json is not None
    assert "token_type" in tokens_json

    restored_tokens = Tokens(**tokens_json)
    assert restored_tokens is not None
    assert restored_tokens.access_token == tokens1.access_token
    assert restored_tokens.refresh_token == tokens1.refresh_token
    assert restored_tokens.id_token == tokens1.id_token
    assert restored_tokens.is_access_token_valid
    assert restored_tokens.is_refresh_token_valid

    now = datetime.now()
    tokens2 = mock_tokens(created_at=now - timedelta(seconds=3600))
    assert not tokens2.is_access_token_valid


def test_token_store() -> None:
    local_store = LocalTokenStore()
    if os.path.exists(Path(local_store.token_output_path)):
        os.remove(local_store.token_output_path)  # clean up before test

    null_token = local_store.get_tokens()
    assert null_token is None

    mocked_token1 = mock_tokens()
    local_store.save_tokens(mocked_token1)
    assert local_store.token_output_path is not None
    assert os.path.exists(local_store.token_output_path)

    retrieved_token = local_store.get_tokens()
    assert retrieved_token is not None
    assert retrieved_token.access_token == mocked_token1.access_token
    assert retrieved_token.refresh_token == mocked_token1.refresh_token
    assert retrieved_token.id_token == mocked_token1.id_token
    assert retrieved_token.scope == mocked_token1.scope
    os.remove(local_store.token_output_path)  # clean up after tests
