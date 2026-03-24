from typing import Literal

from pydantic import BaseModel, Field


LiabilityType = Literal["loan", "credit_card", "mortgage", "other"]


class Investment(BaseModel):
    symbol: str
    value: float = Field(ge=0)


class Liability(BaseModel):
    type: LiabilityType
    amount: float = Field(ge=0)
    rate: float = Field(ge=0)


class FinancialSnapshot(BaseModel):
    user_id: str
    balance: float
    investments: list[Investment] = []
    liabilities: list[Liability] = []
