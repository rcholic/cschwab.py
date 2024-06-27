from cschwabpy.models import JSONSerializableBaseModel, OptionContractType
from typing import Optional, List, Any, Mapping, MutableMapping
from pydantic import Field
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


class Destination(str, Enum):
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
    ETF = "ETF"
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


class SpecialInstruction(str, Enum):
    ALL_OR_NONE = "ALL_OR_NONE"
    DO_NOT_REDUCE = "DO_NOT_REDUCE"
    ALL_OR_NONE_DO_NOT_REDUCE = "ALL_OR_NONE_DO_NOT_REDUCE"


class OrderStrategyType(str, Enum):
    SINGLE = "SINGLE"
    CANCEL = "CANCEL"
    RECALL = "RECALL"
    PAIR = "PAIR"
    FLATTEN = "FLATTEN"
    TWO_DAY_SWAP = "TWO_DAY_SWAP"
    BLAST_ALL = "BLAST_ALL"
    OCO = "OCO"
    TRIGGER = "TRIGGER"


class TaxLotMethod(str, Enum):
    FIFO = "FIFO"
    LIFO = "LIFO"
    HIGH_COST = "HIGH_COST"
    LOW_COST = "LOW_COST"
    AVERAGE_COST = "AVERAGE_COST"
    SPECIFIC_LOT = "SPECIFIC_LOT"
    LOSS_HARVESTER = "LOSS_HARVESTER"


class PriceLinkType(str, Enum):
    VALUE = "VALUE"
    PERCENT = "PERCENT"
    TICK = "TICK"


class StopType(str, Enum):
    STANDARD = "STANDARD"
    BID = "BID"
    ASK = "ASK"
    LAST = "LAST"
    MARK = "MARK"


class PriceLinkBasis(str, Enum):
    MANUAL = "MANUAL"
    BASE = "BASE"
    TRIGGER = "TRIGGER"
    LAST = "LAST"
    BID = "BID"
    ASK = "ASK"
    ASK_BID = "ASK_BID"
    MARK = "MARK"
    AVERAGE = "AVERAGE"


class OrderActivityType(str, Enum):
    EXECUTION = "EXECUTION"
    ORDER_ACTION = "ORDER_ACTION"


class ExecutionType(str, Enum):
    FILL = "FILL"
    CANCELED = "CANCELED"


class QuantityType(str, Enum):
    ALL_SHARES = "ALL_SHARES"
    DOLLARS = "DOLLARS"
    SHARES = "SHARES"


class InstrumentProjection(str, Enum):
    SymbolSearch = "symbol-search"
    SymbolRegex = "symbol-regex"
    DescSearch = "desc-search"
    DescRegex = "desc-regex"
    Search = "search"
    Fundamental = "fundamental"


# --------------------------------------------------


class AccountNumberWithHashID(JSONSerializableBaseModel):
    """accountNumber and hashValue pair.

    Args:
        accountNumber is a numerical string such as 12345678
        hashValue is secret/encrypted ID such as EECD2E7A0B9C1935
        hashValue is used to get resources under the account such as retrieving orders.
    """

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


class OrderLeg(JSONSerializableBaseModel):
    askPrice: Optional[float] = None
    bidPrice: Optional[float] = None
    lastPrice: Optional[float] = None
    marketPrice: Optional[float] = None
    projectedCommission: Optional[float] = None
    quantity: Optional[float] = None
    finalSymbol: Optional[str] = None
    legId: Optional[int] = None
    assetType: Optional[AssetType] = None
    instruction: Optional[OrderLegInstruction] = None


class OrderLegCollection(JSONSerializableBaseModel):
    orderLegType: Optional[AssetType] = None
    legId: Optional[int] = None
    instrument: Optional[AccountInstrument] = None  # e.g. AccountOption
    instruction: Optional[OrderLegInstruction] = None
    positionEffect: Optional[PositionEffect] = None
    quantity: Optional[float] = None
    quantityType: Optional[QuantityType] = None  # QuantityType.SHARES
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
    roundTrips: Optional[int] = None
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
class ExecutionLeg(JSONSerializableBaseModel):
    legId: Optional[int] = 0
    price: Optional[float] = 0
    quantity: Optional[float] = 0
    mismarkedQuantity: Optional[float] = 0
    instrumentId: Optional[int] = 0
    time: Optional[str] = None


class OrderActivity(JSONSerializableBaseModel):
    activityType: Optional[OrderActivityType] = OrderActivityType.ORDER_ACTION
    executionType: Optional[ExecutionType] = ExecutionType.FILL
    quanity: Optional[float] = 0
    orderRemainingQuantity: Optional[float] = 0
    executionLegs: List[ExecutionLeg] = []


class Order(JSONSerializableBaseModel):
    session: Session
    duration: Duration = Duration.DAY
    orderType: OrderType = OrderType.LIMIT
    cancelTime: Optional[str] = None
    complexOrderStrategyType: Optional[ComplexOrderStrategyType] = None
    quantity: Optional[float] = None
    filledQuantity: Optional[float] = None
    remainingQuantity: Optional[float] = None
    requestedDestination: Optional[Destination] = None
    destinationLinkName: Optional[str] = "AUTO"
    releaseTime: Optional[str] = None
    stopPrice: Optional[float] = None
    stopPriceLinkBasis: Optional[PriceLinkBasis] = None
    stopPriceLinkType: Optional[PriceLinkType] = None
    stopPriceOffset: Optional[float] = None
    stopType: Optional[StopType] = None
    priceLinkBasis: Optional[PriceLinkBasis] = None
    priceLinkType: Optional[PriceLinkType] = None
    price: float
    taxLotMethod: Optional[TaxLotMethod] = None
    orderLegCollection: List[OrderLegCollection] = []
    activationPrice: Optional[float] = None
    specialInstruction: Optional[SpecialInstruction] = None
    orderStrategyType: Optional[OrderStrategyType] = OrderStrategyType.SINGLE
    orderId: Optional[int] = None
    cancelable: Optional[bool] = None
    editable: Optional[bool] = None
    status: Optional[OrderStatus] = None
    enteredTime: Optional[str] = None
    closeTime: Optional[str] = None
    tag: Optional[str] = None
    accountNumber: Optional[int] = None
    orderActivityCollection: List[OrderActivity] = []
    replacingOrderCollection: List[str] = []
    childOrderStrategies: List[str] = []
    statusDescription: Optional[str] = None


class EquityOrder(Order):
    quanity: float


class OptionOrder(Order):
    quantity: Optional[float] = None
    complexOrderStrategyType: ComplexOrderStrategyType
