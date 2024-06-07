from cschwabpy.models import JSONSerializableBaseModel
from typing import Optional, List, Any
from pydantic import Field
from enum import Enum


class AccountType(str, Enum):
    MARGIN = "MARGIN"
    CASH = "CASH"
    IRA = "IRA"


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


class MarginAccount(Account):
    type_: AccountType = Field(AccountType.MARGIN, alias="type")


class CashAccount(Account):
    type_: AccountType = Field(AccountType.CASH, alias="type")


class SecuritiesAccount(JSONSerializableBaseModel):
    securitiesAccount: Account
