from fastapi import APIRouter, Depends, Header

from app.api.deps.auth import get_current_user
from app.schemas.lms import AuthLoginRequest, AuthSession, DemoAccount, UserProfile
from app.services.auth_service import authenticate_user, list_demo_accounts, logout_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthSession)
def login(payload: AuthLoginRequest) -> AuthSession:
    return authenticate_user(payload.username.strip(), payload.password)


@router.post("/logout")
def logout(authorization: str = Header(default="")) -> dict[str, str]:
    token = authorization.removeprefix("Bearer ").strip()
    if token:
        logout_session(token)
    return {"status": "ok"}


@router.get("/demo-accounts", response_model=list[DemoAccount])
def demo_accounts() -> list[DemoAccount]:
    return list_demo_accounts()


@router.get("/me", response_model=UserProfile)
def me(user: UserProfile = Depends(get_current_user)) -> UserProfile:
    return user
