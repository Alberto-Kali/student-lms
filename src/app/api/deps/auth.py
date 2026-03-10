from fastapi import Header, HTTPException, status

from app.schemas.lms import UserProfile
from app.services.auth_service import get_user_by_access_token


def get_current_user(authorization: str = Header(default="")) -> UserProfile:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    user = get_user_by_access_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return user
