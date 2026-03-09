from fastapi import APIRouter

from app.db.clickhouse import create_clickhouse_client

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    client = create_clickhouse_client()
    client.command("SELECT 1")
    return {"status": "ok", "backend": "python-fastapi", "db": "clickhouse"}
