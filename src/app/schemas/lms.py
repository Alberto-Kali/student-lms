from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    status: str
    email: EmailStr
    group_name: str = ""
    department: str = ""


class DemoAccount(BaseModel):
    username: str
    password: str
    full_name: str
    role: str
    status: str


class AuthLoginRequest(BaseModel):
    username: str
    password: str


class AuthSession(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserProfile


class VisitLeadIn(BaseModel):
    name: str
    email: EmailStr
    phone: str
    message: str


class VisitLeadOut(BaseModel):
    id: str
    created_at: datetime


class ExternalUserLink(BaseModel):
    id: str
    external_system: str
    external_user_id: str
    external_username: str
    linked_at: datetime


class ScheduleSlot(BaseModel):
    id: str
    course_id: str
    subject: str
    room: str
    group_name: str
    day_of_week: int
    starts_at: str
    ends_at: str
    teacher_name: str


class NotificationItem(BaseModel):
    id: str
    kind: str
    title: str
    body: str
    entity_type: str
    entity_id: str
    created_at: datetime
    is_read: bool = False


class CourseSummary(BaseModel):
    id: str
    title: str
    description: str
    teacher_name: str
    audience: str
    status: str
    progress: int = 0


class CourseModule(BaseModel):
    id: str
    title: str
    content: str
    position: int
    estimated_minutes: int
    completed: bool = False
    completed_at: datetime | None = None


class TestSummary(BaseModel):
    id: str
    course_id: str
    title: str
    description: str
    duration_minutes: int
    max_attempts: int
    passing_score: int
    latest_status: str = "new"
    latest_score: int | None = None


class CourseDetail(BaseModel):
    course: CourseSummary
    modules: list[CourseModule]
    tests: list[TestSummary]


class TestQuestion(BaseModel):
    id: str
    prompt: str
    options: list[str]
    question_type: str
    position: int
    points: int


class TestAttemptStart(BaseModel):
    attempt_id: str
    test: TestSummary
    questions: list[TestQuestion]
    started_at: datetime


class TestAnswerSubmission(BaseModel):
    question_id: str
    selected_option_ids: list[int] = Field(default_factory=list)


class TestAttemptSubmission(BaseModel):
    answers: list[TestAnswerSubmission]


class TestAttemptResult(BaseModel):
    attempt_id: str
    status: str
    score: int
    passing_score: int
    earned_points: int
    total_points: int
    submitted_at: datetime


class ReviewQueueItem(BaseModel):
    attempt_id: str
    student_name: str
    course_title: str
    test_title: str
    score: int
    submitted_at: datetime
    teacher_name: str


class DashboardPayload(BaseModel):
    user: UserProfile
    courses: list[CourseSummary]
    schedule: list[ScheduleSlot]
    notifications: list[NotificationItem]
    external_links: list[ExternalUserLink]
    review_queue: list[ReviewQueueItem]
    demo_accounts: list[DemoAccount]
