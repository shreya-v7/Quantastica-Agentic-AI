from fastapi import APIRouter, Depends, Request

from app.core.dependencies import (
    auth_service,
    client_ip,
    current_user_id,
    rate_limit,
)
from app.core.envelope import success
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TotpVerifyRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")


@router.post("/register", dependencies=[Depends(rate_limit("auth", "auth"))])
async def register(
    body: RegisterRequest,
    request: Request,
    service: AuthService = Depends(auth_service),
) -> dict:
    profile = await service.register(body.email, body.password, client_ip(request))
    return success(profile)


@router.post("/login", dependencies=[Depends(rate_limit("auth", "auth"))])
async def login(
    body: LoginRequest,
    request: Request,
    service: AuthService = Depends(auth_service),
) -> dict:
    pair = await service.login(body.email, body.password, body.totp_code, client_ip(request))
    return success(pair)


@router.post("/refresh", dependencies=[Depends(rate_limit("auth", "auth"))])
async def refresh(
    body: RefreshRequest,
    request: Request,
    service: AuthService = Depends(auth_service),
) -> dict:
    pair = await service.refresh(body.refresh_token, client_ip(request))
    return success(pair)


@router.get("/me")
async def me(
    user_id: str = Depends(current_user_id),
    service: AuthService = Depends(auth_service),
) -> dict:
    return success(await service.profile(user_id))


@router.post("/totp/setup")
async def totp_setup(
    user_id: str = Depends(current_user_id),
    service: AuthService = Depends(auth_service),
) -> dict:
    return success(await service.start_totp(user_id))


@router.post("/totp/confirm")
async def totp_confirm(
    body: TotpVerifyRequest,
    user_id: str = Depends(current_user_id),
    service: AuthService = Depends(auth_service),
) -> dict:
    await service.confirm_totp(user_id, body.code)
    return success({"totpEnabled": True})
