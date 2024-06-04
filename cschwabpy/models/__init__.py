"""models folder."""
from pydantic import BaseModel, ConfigDict
from typing import Mapping, Any


class CharlieModelBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    def to_json(self) -> Mapping[str, Any]:
        return self.model_dump(by_alias=True)
