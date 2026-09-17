from pydantic import EmailStr, Field

from app.schemas.base import Contract


class RegisterRequest(Contract):
    email: EmailStr
    password: str = Field(min_length=10, max_length=200)


class LoginRequest(Contract):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)
    totp_code: str | None = Field(default=None, min_length=6, max_length=6)


class RefreshRequest(Contract):
    refresh_token: str = Field(min_length=1)


class TokenPair(Contract):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class UserProfile(Contract):
    id: str
    email: str | None
    role: str
    totp_enabled: bool
    automation_enabled: bool
    trading_disabled: bool


class TotpSetup(Contract):
    secret: str
    otpauth_url: str


class TotpVerifyRequest(Contract):
    code: str = Field(min_length=6, max_length=6)


class MfaRequiredResponse(Contract):
    mfa_required: bool = True
