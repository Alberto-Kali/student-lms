from fastapi import APIRouter

from app.schemas.lms import Course
from app.services.lms_service import list_courses

router = APIRouter(prefix="/lms", tags=["lms"])


@router.get("/courses", response_model=list[Course])
def get_courses() -> list[Course]:
    return list_courses()
