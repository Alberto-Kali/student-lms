from fastapi import APIRouter, status

from app.schemas.lms import VisitLeadIn, VisitLeadOut
from app.services.lms_service import create_visit_lead

router = APIRouter(prefix="/visit", tags=["visit"])


@router.post("/lead", response_model=VisitLeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(payload: VisitLeadIn) -> VisitLeadOut:
    return create_visit_lead(payload)


@router.get("/content")
def get_visit_content_stub() -> dict[str, str]:
    return {
        "status": "stub",
        "details": "Reserve this endpoint for visit-frontend CMS/public content.",
    }
