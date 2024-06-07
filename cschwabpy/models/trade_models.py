from cschwabpy.models import JSONSerializableBaseModel


class AccountNumberModel(JSONSerializableBaseModel):
    accountNumber: str
    hashValue: str
