"""models folder."""
from datetime import datetime, date
from dateutil import parser
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, Field
from typing import MutableMapping, Mapping, MutableSet, Any, List, Tuple, Optional
from enum import Enum
import cschwabpy.util as util
import pandas as pd
import pytz

us_eastern_timezone = pytz.timezone("US/Eastern")

OptionChain_Headers = [
    "underlying_price",
    "strike",
    "symbol",
    "lastPrice",
    "openInterest",
    "ask",
    "bid",
    "expiration_date",
    "bid_date",
    "volume",
    "updated_at",
    "gamma",
    "delta",
    "vega",
    "volatility",
]


class JSONSerializableBaseModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    def to_json(self, drop_null_value: bool = True) -> Mapping[str, Any]:
        """Converts the object to a JSON dictionary with options to drop null values from dictionary."""
        super_json = self.model_dump(by_alias=True)
        if not drop_null_value:
            return super_json

        result: MutableMapping[str, Any] = {}
        for k, v in list(super_json.items()):
            if v is not None:
                result[k] = self.__handle_item(v)

        return result

    def __handle_item(self, item: Any) -> Any:
        """Handle item in the dictionary, list or primitive values."""
        if isinstance(item, dict):
            return self.__del_none(item)
        elif isinstance(item, List):
            result = []
            for itm in list(item):
                result.append(self.__handle_item(itm))
            return result
        elif isinstance(item, set):
            result = set()
            for itm in set(item):
                result.add(self.__handle_item(itm))
            return result
        elif isinstance(item, Enum):
            return item.value
        elif isinstance(item, datetime) or isinstance(item, date):
            return str(item)  # because datetime/date object is not JSON serializable
        else:
            return item

    def __del_none(self, d: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """Recursively remove None values from a dictionary."""
        for key, value in list(d.items()):
            if value is None:
                del d[key]
            elif isinstance(value, MutableMapping):
                d[key] = self.__del_none(value)

        return d


class ErrorMessage(JSONSerializableBaseModel):
    message: str
    errors: List[str]


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


class ExpirationType(str, Enum):
    M = "M"
    Q = "Q"
    S = "S"
    W = "W"


class OptionExpiration(JSONSerializableBaseModel):
    expirationDate: str
    daysToExpiration: Optional[int] = None
    expirationType: Optional[ExpirationType] = None
    standard: Optional[bool] = None


class OptionExpirationChainResponse(JSONSerializableBaseModel):
    expirationList: List[OptionExpiration] = []


class OptionContractType(str, Enum):
    """Option contract type."""

    CALL = "CALL"
    PUT = "PUT"
    ALL = "ALL"
    UNKNOWN = "UNKNOWN"


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


class MarketType(str, Enum):
    Equity = "EQUITY"
    Option = "OPTION"
    Future = "FUTURE"
    Bond = "BOND"
    Forex = "FOREX"
    FutureOption = "FUTURE_OPTION"
    Index = "INDEX"
    MutualFund = "MUTUAL_FUND"


class MarketHours(JSONSerializableBaseModel):
    start: str
    end: str

    def open_window(
        self, timezone: pytz.BaseTzInfo = us_eastern_timezone
    ) -> Tuple[datetime, datetime]:
        """Returns the market open window (tuple) in datetime format, defaulted to US eastern timezone.."""
        start_time = parser.parse(self.start).astimezone(timezone)
        end_time = parser.parse(self.end).astimezone(timezone)
        return start_time, end_time


class SessionHours(JSONSerializableBaseModel):
    preMarket: Optional[List[MarketHours]] = None
    regularMarket: List[MarketHours]
    postMarket: Optional[List[MarketHours]] = None


class Market(JSONSerializableBaseModel):
    date: date
    marketType: MarketType
    exchange: Optional[str] = None
    category: Optional[str] = None
    product: str
    productName: str
    isOpen: bool
    sessionHours: Optional[SessionHours] = None


class EquityMarket(JSONSerializableBaseModel):
    EQ: Optional[Market] = None


class OptionMarket(JSONSerializableBaseModel):
    EQO: Optional[Market] = None
    IND: Optional[Market] = None


class MarketHourInfo(JSONSerializableBaseModel):
    equity: Optional[EquityMarket] = None
    option: Optional[OptionMarket] = None

    @property
    def is_equity_market_open(self) -> bool:
        if self.equity is None or self.equity.EQ is None:
            return False

        return self.equity.EQ.isOpen

    @property
    def is_option_market_open(self) -> bool:
        if self.option is None:
            return False

        return self.option.EQO.isOpen or self.option.IND.isOpen

    @property
    def equity_regular_market_hours(self) -> List[MarketHours]:
        if (
            self.equity is None
            or self.equity.EQ is None
            or self.equity.EQ.sessionHours is None
        ):
            return []

        return self.equity.EQ.sessionHours.regularMarket


class OptionChainQueryFilter(QueryFilterBase):
    symbol: str
    contractType: OptionContractType = OptionContractType.ALL
    strikeCount: int = (
        40  # the number of strikes to  return above or below the at-the-money price
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
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    mark: Optional[float] = None
    bidSize: Optional[int] = None
    askSize: Optional[int] = None
    lastSize: Optional[int] = None
    highPrice: Optional[float] = None
    lowPrice: Optional[float] = None
    openPrice: Optional[float] = None
    closePrice: Optional[float] = None
    totalVolume: Optional[int] = None
    tradeTimeInLong: Optional[int] = None
    quoteTimeInLong: Optional[int]
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
    expirationDate: str  # TODO: change to datetime
    daysToExpiration: int
    expirationType: str  # M for end of month, W for week, Q for quarter, S for third friday
    lastTradingDay: Optional[int] = None
    multiplier: Optional[float] = None
    settlementType: str  # AM, PM
    isIndex: Optional[bool] = None
    percentChange: Optional[float] = None
    markChange: Optional[float] = None
    markPercentChange: Optional[float] = None
    model_config = ConfigDict(
        validate_assignment=False, use_enum_values=True, populate_by_name=True
    )

    def to_dataframe_row(self, strip_space: bool = False) -> List[Any]:
        """Converts the object to a list of values for a dataframe row, strip_space: stripping space in option symbol."""
        symbol = self.symbol.strip().replace(" ", "") if strip_space else self.symbol
        result: List[Any] = [
            self.strikePrice,
            symbol,
            self.last,
            self.openInterest,
            self.ask,
            self.bid,
            self.expirationDate[: self.expirationDate.index("T")],
            util.ts_to_datetime(self.quoteTimeInLong),
            self.totalVolume,
            self.quoteTimeInLong,  # updated_at
            self.gamma,
            self.delta,
            self.vega,
            self.volatility,
        ]
        return result


class Underlying(JSONSerializableBaseModel):
    ask: Optional[float] = None
    askSize: Optional[int] = None
    bid: Optional[float] = None
    bidSize: Optional[int] = None
    close_: Optional[float] = Field(None, alias="close")
    description: Optional[str] = None
    exchangeName: Optional[str] = None
    highPrice: Optional[float] = None
    last: Optional[float] = None
    lowPrice: Optional[float] = None
    mark: Optional[float] = None
    markChange: Optional[float] = None
    markPercentChange: Optional[float] = None
    openPrice: Optional[float] = None
    percentChange: Optional[float] = None
    quoteTime: Optional[int] = None
    symbol: str
    totalVolume: Optional[int] = None
    tradeTime: Optional[int] = None

    @property
    def quote_time(self) -> Optional[datetime]:
        return util.ts_to_datetime(self.quoteTime)


@dataclass
class OptionChainDataFrames:
    expiration: str
    underlying_symbol: str
    call_df: pd.DataFrame
    put_df: pd.DataFrame


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

    def to_dataframe_pairs_by_expiration(
        self, strip_space: bool = False, use_compression: bool = False
    ) -> List[OptionChainDataFrames]:
        """
        List of OptionChainDataFrames by expiration.
        Each OptionChainDataFrames object contains call and put chain in dataframe format.
        @param strip_space: Whether strip spaces in option symbols.
        @param use_compress: Whether to compress the data frame to bare minimum data types.
        """
        results: List[OptionChainDataFrames] = []
        call_map = self.break_down_option_map(
            self.callExpDateMap,
            strip_space=strip_space,
            should_compress=use_compression,
        )
        put_map = self.break_down_option_map(
            self.putExpDateMap,
            strip_space=strip_space,
            should_compress=use_compression,
        )
        for expiration in call_map.keys():
            call_df = call_map[expiration]
            put_df = put_map[expiration]

            cur_df_pair = OptionChainDataFrames(
                expiration=expiration,
                underlying_symbol=self.symbol,
                call_df=call_df,
                put_df=put_df,
            )
            results.append(cur_df_pair)

        return results

    def break_down_option_map(
        self,
        optionExpMap: Mapping[str, Mapping[str, List[OptionContract]]],
        strip_space: bool = False,
        should_compress: bool = False,
    ) -> Mapping[str, pd.DataFrame]:
        """
        Whether strip spaces in option symbols.
        if should_compress is True, cast the data types
        to bare minimum to save memory usage.
        """
        now_unix_ts = int(util.now_unix_ts())
        result: MutableMapping[str, pd.DataFrame] = {}
        for exp_date, strike_map in optionExpMap.items():
            expiration = exp_date.split(":")[0]
            if expiration not in result:
                result[expiration] = {}

            all_rows = []
            strike_df = pd.DataFrame()
            for strike_str, option_contracts in strike_map.items():
                for option_contract in option_contracts:
                    row = option_contract.to_dataframe_row(strip_space=strip_space)
                    row.insert(0, self.underlying.mark)
                    all_rows.append(row)

                strike_df = pd.DataFrame(all_rows)
                strike_df.columns = OptionChain_Headers
                # change updated_at to now_unix_ts
                strike_df["updated_at"] = now_unix_ts

            if should_compress:
                strike_df = strike_df.astype(
                    {
                        "underlying_price": "float16",
                        "strike": "float16",
                        "lastPrice": "float16",
                        "openInterest": "int32",
                        "volume": "int32",
                        "ask": "float16",
                        "bid": "float16",
                        "lastPrice": "float16",
                        "gamma": "float16",
                        "delta": "float16",
                        "vega": "float16",
                        "volatility": "float16",
                    }
                )

            result[expiration] = strike_df

        return result
