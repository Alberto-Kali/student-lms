from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_user
from app.schemas.lms import (
    CourseDetail,
    CourseSummary,
    DashboardPayload,
    ExternalUserLink,
    NotificationItem,
    ReviewQueueItem,
    ScheduleSlot,
    TestAttemptResult,
    TestAttemptStart,
    TestAttemptSubmission,
    UserProfile,
)
from app.services.auth_service import list_demo_accounts
from app.services.lms_service import (
    complete_module,
    get_course_detail,
    get_dashboard,
    list_courses,
    list_external_links,
    list_notifications,
    list_review_queue,
    list_schedule,
    start_test_attempt,
    submit_test_attempt,
)

router = APIRouter(prefix="/lms", tags=["lms"])


@router.get("/dashboard", response_model=DashboardPayload)
def dashboard(user: UserProfile = Depends(get_current_user)) -> DashboardPayload:
    return get_dashboard(user, list_demo_accounts())


@router.get("/courses", response_model=list[CourseSummary])
def get_courses(user: UserProfile = Depends(get_current_user)) -> list[CourseSummary]:
    return list_courses(user)


@router.get("/courses/{course_id}", response_model=CourseDetail)
def course_detail(course_id: str, user: UserProfile = Depends(get_current_user)) -> CourseDetail:
    return get_course_detail(user, course_id)


@router.post("/courses/{course_id}/modules/{module_id}/complete", response_model=CourseDetail)
def course_complete_module(course_id: str, module_id: str, user: UserProfile = Depends(get_current_user)) -> CourseDetail:
    return complete_module(user, course_id, module_id)


@router.post("/tests/{test_id}/attempts", response_model=TestAttemptStart)
def create_attempt(test_id: str, user: UserProfile = Depends(get_current_user)) -> TestAttemptStart:
    return start_test_attempt(user, test_id)


@router.post("/tests/{test_id}/attempts/{attempt_id}/submit", response_model=TestAttemptResult)
def submit_attempt(
    test_id: str,
    attempt_id: str,
    payload: TestAttemptSubmission,
    user: UserProfile = Depends(get_current_user),
) -> TestAttemptResult:
    return submit_test_attempt(user, test_id, attempt_id, payload)


@router.get("/schedule", response_model=list[ScheduleSlot])
def schedule(user: UserProfile = Depends(get_current_user)) -> list[ScheduleSlot]:
    return list_schedule(user)


@router.get("/notifications", response_model=list[NotificationItem])
def notifications(user: UserProfile = Depends(get_current_user)) -> list[NotificationItem]:
    return list_notifications(user)


@router.get("/external-links", response_model=list[ExternalUserLink])
def external_links(user: UserProfile = Depends(get_current_user)) -> list[ExternalUserLink]:
    return list_external_links(user)


@router.get("/review-queue", response_model=list[ReviewQueueItem])
def review_queue(user: UserProfile = Depends(get_current_user)) -> list[ReviewQueueItem]:
    return list_review_queue(user)
