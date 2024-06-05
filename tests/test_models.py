import json
import typing
from pathlib import Path
from cschwabpy.models import (
    OptionChain,
    OptionContract,
    OptionContractType,
    OptionContractStrategy,
)

mock_file_name = "mock_schwab_api_resp.json"


def get_mock_response(
    mock_json_file_name: str = mock_file_name,
) -> typing.Mapping[str, typing.Any]:
    mock_api_res_file_path = Path(
        Path(__file__).resolve().parent, "data", mock_json_file_name
    )
    with open(mock_api_res_file_path, "r") as json_file:
        return json.load(json_file)


def test_option_chain_parsing() -> None:
    opt_chain_api_resp = get_mock_response()["option_chain_resp"]
    opt_chain_result = OptionChain(**opt_chain_api_resp)
    assert opt_chain_result is not None
    assert opt_chain_result.status == "SUCCESS"

    # for key, value in opt_chain_result.callExpDateMap.items():
    #     # Do something with key and value
    #     print(key[:10])
    #     print(value)#
    #     print("----------------")
