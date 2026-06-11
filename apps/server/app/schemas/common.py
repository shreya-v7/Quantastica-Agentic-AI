from enum import Enum


class AssetClass(str, Enum):
    equity = "equity"
    etf = "etf"
    crypto = "crypto"
    bond = "bond"
    cash = "cash"


class Severity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"


class Rating(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class StepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"


class Platform(str, Enum):
    local = "local"
    gcp = "gcp"
    aws = "aws"
