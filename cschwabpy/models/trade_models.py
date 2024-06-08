from cschwabpy.models import JSONSerializableBaseModel, OptionContractType
from typing import Optional, List, Any
from pydantic import Field
from enum import Enum
from enum import Enum


class AccountType(str, Enum):
    MARGIN = "MARGIN"
    CASH = "CASH"
    IRA = "IRA"


class OrderStatus(str, Enum):
    AWAITING_PARENT_ORDER = "AWAITING_PARENT_ORDER"
    AWAITING_CONDITION = "AWAITING_CONDITION"
    AWAITING_STOP_CONDITION = "AWAITING_STOP_CONDITION"
    AWAITING_MANUAL_REVIEW = "AWAITING_MANUAL_REVIEW"
    ACCEPTED = "ACCEPTED"
    AWAITING_UR_OUT = "AWAITING_UR_OUT"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"
    QUEUED = "QUEUED"
    WORKING = "WORKING"
    REJECTED = "REJECTED"
    PENDING_CANCEL = "PENDING_CANCEL"
    CANCELED = "CANCELED"
    PENDING_REPLACE = "PENDING_REPLACE"
    REPLACED = "REPLACED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"
    NEW = "NEW"
    AWAITING_RELEASE_TIME = "AWAITING_RELEASE_TIME"
    PENDING_ACKNOWLEDGEMENT = "PENDING_ACKNOWLEDGEMENT"
    PENDING_RECALL = "PENDING_RECALL"
    UNKNOWN = "UNKNOWN"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    CABINET = "CABINET"
    NON_MARKETABLE = "NON_MARKETABLE"
    MARKET_ON_CLOSE = "MARKET_ON_CLOSE"
    EXERCISE = "EXERCISE"
    TRAILING_STOP_LIMIT = "TRAILING_STOP_LIMIT"
    NET_DEBIT = "NET_DEBIT"
    NET_CREDIT = "NET_CREDIT"
    NET_ZERO = "NET_ZERO"
    LIMIT_ON_CLOSE = "LIMIT_ON_CLOSE"
    UNKNOWN = "UNKNOWN"


class ComplexOrderStrategyType(str, Enum):
    NONE = "NONE"
    COVERED = "COVERED"
    VERTICAL = "VERTICAL"
    BACK_RATIO = "BACK_RATIO"
    CALENDAR = "CALENDAR"
    DIAGONAL = "DIAGONAL"
    STRADDLE = "STRADDLE"
    STRANGLE = "STRANGLE"
    COLLAR_SYNTHETIC = "COLLAR_SYNTHETIC"
    BUTTERFLY = "BUTTERFLY"
    CONDOR = "CONDOR"
    IRON_CONDOR = "IRON_CONDOR"
    VERTICAL_ROLL = "VERTICAL_ROLL"
    COLLAR_WITH_STOCK = "COLLAR_WITH_STOCK"
    DOUBLE_DIAGONAL = "DOUBLE_DIAGONAL"
    UNBALANCED_BUTTERFLY = "UNBALANCED_BUTTERFLY"
    UNBALANCED_CONDOR = "UNBALANCED_CONDOR"
    UNBALANCED_IRON_CONDOR = "UNBALANCED_IRON_CONDOR"
    UNBALANCED_VERTICAL_ROLL = "UNBALANCED_VERTICAL_ROLL"
    MUTUAL_FUND_SWAP = "MUTUAL_FUND_SWAP"
    CUSTOM = "CUSTOM"


class Session(str, Enum):
    NORMAL = "NORMAL"
    AM = "AM"
    PM = "PM"
    SEAMLESS = "SEAMLESS"


class Duration(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"
    FILL_OR_KILL = "FILL_OR_KILL"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"
    END_OF_WEEK = "END_OF_WEEK"
    END_OF_MONTH = "END_OF_MONTH"
    NEXT_END_OF_MONTH = "NEXT_END_OF_MONTH"
    UNKNOWN = "UNKNOWN"


class Destination(Enum):
    INET = "INET"
    ECN_ARCA = "ECN_ARCA"
    CBOE = "CBOE"
    AMEX = "AMEX"
    PHLX = "PHLX"
    ISE = "ISE"
    BOX = "BOX"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    BATS = "BATS"
    C2 = "C2"
    AUTO = "AUTO"


# class OrderLegType(str, Enum):
class AssetType(str, Enum):  # same as OrderLegType
    EQUITY = "EQUITY"
    OPTION = "OPTION"
    INDEX = "INDEX"
    MUTUAL_FUND = "MUTUAL_FUND"
    CASH_EQUIVALENT = "CASH_EQUIVALENT"
    FIXED_INCOME = "FIXED_INCOME"
    CURRENCY = "CURRENCY"
    COLLECTIVE_INVESTMENT = "COLLECTIVE_INVESTMENT"


class OptionType(str, Enum):
    VANILLA = "VANILLA"
    BINARY = "BINARY"
    BARRIER = "BARRIER"
    UNKNOWN = "UNKNOWN"


class OrderLegInstruction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_TO_COVER = "BUY_TO_COVER"
    SELL_SHORT = "SELL_SHORT"
    BUY_TO_OPEN = "BUY_TO_OPEN"
    BUY_TO_CLOSE = "BUY_TO_CLOSE"
    SELL_TO_OPEN = "SELL_TO_OPEN"
    SELL_TO_CLOSE = "SELL_TO_CLOSE"
    EXCHANGE = "EXCHANGE"
    SELL_SHORT_EXEMPT = "SELL_SHORT_EXEMPT"


class PositionEffect(str, Enum):
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    AUTOMATIC = "AUTOMATIC"


class AccountNumberModel(JSONSerializableBaseModel):
    accountNumber: str
    hashValue: str


class MarginBalance(JSONSerializableBaseModel):
    availableFunds: Optional[float] = None
    availableFundsNonMarginableTrade: Optional[float] = None
    buyingPower: Optional[float] = None
    buyingPowerNonMarginableTrade: Optional[float] = None
    dayTradingBuyingPower: Optional[float] = None
    dayTradingBuyingPowerCall: Optional[float] = None
    dayTradingEquityCall: Optional[float] = None
    equity: Optional[float] = None
    equityPercentage: Optional[float] = None
    longMarginValue: Optional[float] = None
    longOptionMarketValue: Optional[float] = None
    longStockValue: Optional[float] = None
    maintenanceCall: Optional[float] = None
    maintenanceRequirement: Optional[float] = None
    margin: Optional[float] = None
    marginEquity: Optional[float] = None
    moneyMarketFund: Optional[float] = None
    mutualFundValue: Optional[float] = None
    sma: Optional[float] = None
    stockBuyingPower: Optional[float] = None
    optionBuyingPower: Optional[float] = None
    regTCall: Optional[float] = None
    shortMarginValue: Optional[float] = None
    shortOptionMarketValue: Optional[float] = None
    shortStockValue: Optional[float] = None
    totalCash: Optional[float] = None
    isInCall: Optional[bool] = None
    unsettledCash: Optional[float] = None
    pendingDeposits: Optional[float] = None
    marginBalance: Optional[float] = None
    shortBalance: Optional[float] = None
    accountValue: Optional[float] = None


class MarginInitialBalance(MarginBalance):
    accruedInterest: Optional[float] = None
    availableFundsNonMarginableTrade: Optional[float] = None
    bondValue: Optional[float] = None
    cashBalance: Optional[float] = None
    cashAvailableForTrading: Optional[float] = None
    cashReceipts: Optional[float] = None
    liquidationValue: Optional[float] = None


class AccountInstrument(JSONSerializableBaseModel):
    assetType: Optional[AssetType] = None
    cusip: Optional[str] = None
    description: Optional[str] = None
    instrumentId: Optional[int] = None
    symbol: Optional[str] = None
    netChange: Optional[float] = None


class AccountEquity(AccountInstrument):
    assetType: AssetType = AssetType.EQUITY


class AccountFixedIncome(AccountInstrument):
    assetType: AssetType = AssetType.FIXED_INCOME
    maturityDate: Optional[str] = None
    factor: Optional[float] = None
    variableRate: Optional[float] = None


class AccountOption(AccountInstrument):
    assetType: AssetType = AssetType.OPTION
    optionDeliverables: Optional[Any] = None  # TODO
    putCall: Optional[OptionContractType] = None
    optionMultiplier: Optional[int] = None
    type_: Optional[OptionType] = Field(None, alias="type")
    underlyingSymbol: Optional[str] = None


class OrderLegCollection(JSONSerializableBaseModel):
    orderLegType: Optional[AssetType] = None
    legId: Optional[int] = None
    instrument: Optional[AccountInstrument] = None  # e.g. AccountOption
    instruction: Optional[OrderLegInstruction] = None
    positionEffect: Optional[PositionEffect] = None
    quantity: Optional[float] = None
    # quantityType: Optional[str] = None #TODO
    # toSymbol: Optional[str] = None #TODO


class Position(JSONSerializableBaseModel):
    shortQuantity: Optional[float] = None
    averagePrice: Optional[float] = None
    currentDayProfitLoss: Optional[float] = None
    currentDayProfitLossPercentage: Optional[float] = None
    longQuantity: Optional[float] = None
    settledLongQuantity: Optional[float] = None
    settledShortQuantity: Optional[float] = None
    agedQuantity: Optional[float] = None
    instrument: Optional[Any] = None  # TODO: AccountInstrument type
    marketValue: Optional[float] = None
    maintenanceRequirement: Optional[float] = None
    averageLongPrice: Optional[float] = None
    averageShortPrice: Optional[float] = None
    taxLotAverageLongPrice: Optional[float] = None
    taxLotAverageShortPrice: Optional[float] = None
    longOpenProfitLoss: Optional[float] = None
    shortOpenProfitLoss: Optional[float] = None
    previousSessionLongQuantity: Optional[float] = None
    previousSessionShortQuantity: Optional[float] = None
    currentDayCost: Optional[float] = None


class Account(JSONSerializableBaseModel):
    type_: Optional[AccountType] = Field(None, alias="type")
    accountNumber: str
    roundTrips: Optional[int] = 0
    isDayTrader: Optional[bool] = False
    isClosingOnlyRestricted: Optional[bool] = False
    pfcbFlag: Optional[bool] = False
    positions: List[Position] = []
    initialBalances: Optional[MarginInitialBalance] = None
    currentBalances: Optional[MarginBalance] = None
    projectedBalances: Optional[MarginBalance] = None

    @property
    def is_margin(self) -> bool:
        return self.type_ == AccountType.MARGIN

    @property
    def is_cash(self) -> bool:
        return self.type_ == AccountType.CASH


class MarginAccount(Account):
    type_: AccountType = Field(AccountType.MARGIN, alias="type")


class CashAccount(Account):
    type_: AccountType = Field(AccountType.CASH, alias="type")


class SecuritiesAccount(JSONSerializableBaseModel):
    securitiesAccount: Account


# Order models


class Order(JSONSerializableBaseModel):
    session: Optional[Session] = None  # TODO: make this Enum type
    duration: Optional[Duration] = None  # TODO: make this Enum type
    orderType: Optional[OrderType] = None  # TODO: make this Enum type
    cancelTime: Optional[str] = None
    complexOrderStrategyType: Optional[ComplexOrderStrategyType] = None
    quantity: Optional[float] = 0
    filledQuantity: Optional[float] = 0
    remainingQuantity: Optional[float] = 0
    requestedDestination: Optional[Destination] = None
    destinationLinkName: Optional[str] = None
    releaseTime: Optional[str] = None
    stopPrice: Optional[float] = None
    stopPriceLinkBasis: Optional[str] = None
    stopPriceLinkType: Optional[str] = None
    stopPriceOffset: Optional[float] = None
    stopType: Optional[str] = None  # TODO: enum this
    priceLinkBasis: Optional[str] = None
    priceLinkType: Optional[str] = None
    price: Optional[float] = None
    taxLotMethod: Optional[str] = None
    orderLegCollection: List[OrderLegCollection] = []  # TODO: OrderLeg type
    activationPrice: Optional[float] = None
    specialInstruction: Optional[str] = None  # TODO: enum this
    orderStrategyType: Optional[str] = None
    orderId: Optional[int] = None
    cancelable: Optional[bool] = False
    editable: Optional[bool] = False
    status: Optional[OrderStatus] = None
    enteredTime: Optional[str] = None
    closeTime: Optional[str] = None
    tag: Optional[str] = None
    accountNumber: Optional[int] = None  # or str ?
    orderActivityCollection: List[Any] = []  # TODO: OrderActivity type
    replacingOrderCollection: List[str] = []
    childOrderStrategies: List[str] = []
    statusDescription: Optional[str] = None
