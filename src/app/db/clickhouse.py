from clickhouse_connect import get_client
from clickhouse_connect.driver.client import Client

from app.core.config import settings


def create_clickhouse_client(database: str | None = None) -> Client:
    resolved_db = settings.clickhouse_database if database is None else database
    client_kwargs = {
        "host": settings.clickhouse_host,
        "port": settings.clickhouse_port,
        "username": settings.clickhouse_user,
        "password": settings.clickhouse_password,
    }
    if resolved_db:
        client_kwargs["database"] = resolved_db
    return get_client(**client_kwargs)
