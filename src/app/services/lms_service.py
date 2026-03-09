from datetime import datetime, timezone
from uuid import uuid4

from app.db.clickhouse import create_clickhouse_client
from app.schemas.lms import Course, VisitLeadIn, VisitLeadOut


def list_courses() -> list[Course]:
    client = create_clickhouse_client()
    rows = client.query(
        """
        SELECT id, title, teacher, group_name, progress, modules, status, updated_at
        FROM courses
        ORDER BY id
        """
    ).result_rows

    return [
        Course(
            id=row[0],
            title=row[1],
            teacher=row[2],
            group_name=row[3],
            progress=row[4],
            modules=row[5],
            status=row[6],
            updated_at=row[7],
        )
        for row in rows
    ]


def create_visit_lead(payload: VisitLeadIn) -> VisitLeadOut:
    client = create_clickhouse_client()
    lead_id = str(uuid4())

    client.insert(
        table="visit_leads",
        data=[[lead_id, payload.name, payload.email, payload.phone, payload.message]],
        column_names=["id", "name", "email", "phone", "message"],
    )

    return VisitLeadOut(id=lead_id, created_at=datetime.now(timezone.utc))
