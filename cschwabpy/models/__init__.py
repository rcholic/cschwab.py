"""models folder."""
from pydantic import BaseModel, ConfigDict, Field
from typing import MutableMapping, Mapping, MutableSet, Any, List, Optional
from enum import Enum
import pandas as pd


class JSONSerializableBaseModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    def to_json(self) -> Mapping[str, Any]:
        return self.model_dump(by_alias=True)


class QueryFilterBase(JSONSerializableBaseModel):
    """Base class for query parameters filters."""

    ...

    def to_query_dict(self, ignore_fields: List[str] = []) -> Mapping[str, Any]:
        """Converts the object to a dictionary of query parameters."""
        dump_dict = self.to_json()
        result: MutableMapping[str, Any] = {}
        self_ignore_fields: MutableSet[str] = {}
        for field_key in ignore_fields:
            self_ignore_fields.add(field_key.lower())

        for key, val in dump_dict.items():
            if key.lower() in self_ignore_fields:
                continue
            if val is not None:
                if isinstance(val, Enum):
                    result[key] = val.value
                else:
                    result[key] = val

        return result

    def to_query_params(self, ignore_fields: List[str] = []) -> str:
        """Converts the object to query parameters."""
        query_dict = self.to_query_dict(ignore_fields)
        return "&".join([f"{k}={v}" for k, v in query_dict.items() if v is not None])


class OptionContractType(str, Enum):
    """Option contract type."""

    CALL = "CALL"
    PUT = "PUT"
    ALL = "ALL"


class OptionContractStrategy(str, Enum):
    SINGLE = "SINGLE"
    ANALYTICAL = "ANALYTICAL"
    COVERED = "COVERED"
    VERTICAL = "VERTICAL"
    CALENDAR = "CALENDAR"
    STRANGLE = "STRANGLE"
    STRADDLE = "STRADDLE"
    BUTTERFLY = "BUTTERFLY"
    CONDOR = "CONDOR"
    DIAGONAL = "DIAGONAL"
    COLLAR = "COLLAR"
    ROLL = "ROLL"


class OptionContractRange(str, Enum):
    ITM = "ITM"
    NTM = "NTM"
    OTM = "OTM"
    SAK = "SAK"
    SBK = "SBK"
    SNK = "SNK"
    ALL = "ALL"


class OptionChainQueryFilter(QueryFilterBase):
    symbol: str
    contractType: OptionContractType = OptionContractType.ALL
    strikeCount: int = (
        25  # the number of strikes to  return above or below the at-the-money price
    )
    includeUnderlyingQuote: bool = True
    strategy: OptionContractStrategy = OptionContractStrategy.ANALYTICAL
    interval: Optional[float] = None  # strike interval for spread strategy
    strike: Optional[float] = None  # strike price for spread strategy
    range: Optional[OptionContractRange] = None
    fromDate: str
    toDate: str


class OptionContract(JSONSerializableBaseModel):
    putCall: OptionContractType
    symbol: str
    description: str
    exchangeName: str
    bidPrice: Optional[float] = None
    askPrice: Optional[float] = None
    lastPrice: Optional[float] = None
    markPrice: Optional[float] = None
    bidSize: Optional[int] = None
    askSize: Optional[int] = None
    lastSize: Optional[int] = None
    highPrice: Optional[float] = None
    lowPrice: Optional[float] = None
    openPrice: Optional[float] = None
    closePrice: Optional[float] = None
    totalVolume: Optional[int] = None
    tradeDate: Optional[int] = None
    quoteTimeInLong: Optional[int]
    tradeTimeInLong: Optional[int] = None
    netChange: Optional[float] = None
    volatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None
    openInterest: Optional[int] = None
    timeValue: Optional[float] = None
    theoreticalOptionValue: Optional[float] = None
    theoreticalVolatility: Optional[float] = None
    strikePrice: float
    expirationDate: str
    daysToExpiration: int
    expirationType: str  # M for end of month, W for week, Q for quarter, S for third friday
    lastTradingDay: Optional[int] = None
    multiplier: Optional[float] = None
    settlementType: str  # AM, PM
    isIndex: bool
    percentChange: Optional[float] = None
    markChange: Optional[float] = None
    markPercentChange: Optional[float] = None
    model_config = ConfigDict(
        validate_assignment=False, use_enum_values=True, populate_by_name=True
    )


class Underlying(JSONSerializableBaseModel):
    ask: float
    askSize: int
    bid: float
    bidSize: int
    close_: float = Field(..., alias="close")
    description: Optional[str] = None
    exchangeName: str
    highPrice: Optional[float] = None
    lastPrice: Optional[float] = None
    lowPrice: Optional[float] = None
    mark: Optional[float] = None
    markChange: Optional[float] = None
    markPercentChange: Optional[float] = None
    openPrice: Optional[float] = None
    percentChange: float
    quoteTime: int
    symbol: str
    totalVolume: Optional[int] = None
    tradeTime: Optional[int] = None


class OptionChain(JSONSerializableBaseModel):
    symbol: str
    status: str
    underlying: Optional[Underlying]
    strategy: str
    interval: Optional[float]
    isDelayed: bool
    isIndex: bool
    interestRate: float
    underlyingPrice: float
    volatility: float
    daysToExpiration: int
    numberOfContracts: int
    putExpDateMap: Mapping[
        str, Mapping[str, List[OptionContract]]
    ]  # key: expiration:27 value:[strike: OptionContract]
    callExpDateMap: Mapping[
        str, Mapping[str, List[OptionContract]]
    ]  # key: expiration:27 value:[strike: OptionContract]
