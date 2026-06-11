"""Dev-only session route. Mounted only when APP_ENV=dev. Mints a short-lived token
so the frontend can exercise the auth path locally. Never mounted in prod."""

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.dependencies import get_settings
from app.core.envelope import success
from app.core.security import mint_token

router = APIRouter(prefix="/dev")


@router.post("/session")
def create_session(settings: Settings = Depends(get_settings)) -> dict:
    token = mint_token(settings, subject="dev-user")
    return success({"token": token, "tokenType": "Bearer"})
