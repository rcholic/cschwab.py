from cschwabpy.models import JSONSerializableBaseModel
from typing import Optional, List, Any
from pydantic import Field
from enum import Enum


class AccountType(str, Enum):
    MARGIN = "MARGIN"
    CASH = "CASH"
    IRA = "IRA"


class OrderStatus(int, Enum):
    AWAITING_PARENT_ORDER = 1
    AWAITING_CONDITION = 2
    AWAITING_STOP_CONDITION = 3
    AWAITING_MANUAL_REVIEW = 4
    ACCEPTED = 5
    AWAITING_UR_OUT = 6
    PENDING_ACTIVATION = 7
    QUEUED = 8
    WORKING = 9
    REJECTED = 10
    PENDING_CANCEL = 11
    CANCELED = 12
    PENDING_REPLACE = 13
    REPLACED = 14
    FILLED = 15
    EXPIRED = 16
    NEW = 17
    AWAITING_RELEASE_TIME = 18
    PENDING_ACKNOWLEDGEMENT = 19
    PENDING_RECALL = 20
    UNKNOWN = 21


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
    session: Optional[str] = None  # TODO: make this Enum type
    duration: Optional[str] = None  # TODO: make this Enum type
    orderType: Optional[str] = None  # TODO: make this Enum type
    cancelTime: Optional[str] = None
    complexOrderStrategyType: Optional[str] = None
    quantity: Optional[float] = 0
    filledQuantity: Optional[float] = 0
    remainingQuantity: Optional[float] = 0
    requestedDestination: Optional[str] = None
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
    orderLegCollection: List[Any] = []  # TODO: OrderLeg type
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
    accountNumber: Optional[str] = None  # or int ?
    orderActivityCollection: List[Any] = []  # TODO: OrderActivity type
    replacingOrderCollection: List[str] = []
    childOrderStrategies: List[str] = []
    statusDescription: Optional[str] = None
