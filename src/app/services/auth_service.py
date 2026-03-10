from fastapi import HTTPException, status

from app.core.security import create_session_token, hash_token, session_expiry, utc_now, verify_password
from app.db.clickhouse import create_clickhouse_client
from app.schemas.lms import AuthSession, DemoAccount, UserProfile


def _row_to_user(row: tuple) -> UserProfile:
    return UserProfile(
        id=row[0],
        username=row[1],
        full_name=row[2],
        role=row[3],
        status=row[4],
        email=row[5],
        group_name=row[6] or "",
        department=row[7] or "",
    )


def list_demo_accounts() -> list[DemoAccount]:
    return [
        DemoAccount(username="admin", password="admin123", full_name="Наталья Рощина", role="admin", status="approved"),
        DemoAccount(username="teacher", password="teacher123", full_name="Ольга Савельева", role="teacher", status="approved"),
        DemoAccount(username="student", password="student123", full_name="Альберто Дженуарди", role="student", status="approved"),
        DemoAccount(username="pending.student", password="student123", full_name="Ирина Логинова", role="student", status="pending"),
        DemoAccount(username="blocked.teacher", password="teacher123", full_name="Кирилл Денисов", role="teacher", status="blocked"),
    ]


def authenticate_user(username: str, password: str) -> AuthSession:
    client = create_clickhouse_client()
    row = client.query(
        """
        SELECT id, username, full_name, role, status, email, group_name, department, password_hash
        FROM users FINAL
        WHERE username = %(username)s
        LIMIT 1
        """,
        parameters={"username": username},
    ).first_row

    if row is None or not verify_password(password, row[8]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    user = _row_to_user(row[:8])
    if user.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт ещё не активирован или заблокирован",
        )

    token = create_session_token()
    expires_at = session_expiry()
    now = utc_now()
    session_id = f"session-{create_session_token()}"

    client.insert(
        table="auth_sessions",
        data=[[session_id, user.id, hash_token(token), now, expires_at, 0, now]],
        column_names=["id", "user_id", "token_hash", "created_at", "expires_at", "revoked", "updated_at"],
    )

    return AuthSession(access_token=token, expires_at=expires_at, user=user)


def get_user_by_access_token(token: str) -> UserProfile | None:
    client = create_clickhouse_client()
    session_row = client.query(
        """
        SELECT id, user_id, expires_at, revoked
        FROM auth_sessions FINAL
        WHERE token_hash = %(token_hash)s
        LIMIT 1
        """,
        parameters={"token_hash": hash_token(token)},
    ).first_row

    if session_row is None:
        return None

    _, user_id, expires_at, revoked = session_row
    if revoked or expires_at <= utc_now():
        return None

    user_row = client.query(
        """
        SELECT id, username, full_name, role, status, email, group_name, department
        FROM users FINAL
        WHERE id = %(user_id)s
        LIMIT 1
        """,
        parameters={"user_id": user_id},
    ).first_row

    if user_row is None:
        return None
    return _row_to_user(user_row)


def logout_session(token: str) -> None:
    client = create_clickhouse_client()
    session_row = client.query(
        """
        SELECT id, user_id, token_hash, created_at, expires_at
        FROM auth_sessions FINAL
        WHERE token_hash = %(token_hash)s
        LIMIT 1
        """,
        parameters={"token_hash": hash_token(token)},
    ).first_row
    if session_row is None:
        return

    now = utc_now()
    client.insert(
        table="auth_sessions",
        data=[[session_row[0], session_row[1], session_row[2], session_row[3], session_row[4], 1, now]],
        column_names=["id", "user_id", "token_hash", "created_at", "expires_at", "revoked", "updated_at"],
    )
