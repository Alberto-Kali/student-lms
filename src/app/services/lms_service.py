import json
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.security import utc_now
from app.db.clickhouse import create_clickhouse_client
from app.schemas.lms import (
    CourseDetail,
    CourseModule,
    CourseSummary,
    DashboardPayload,
    ExternalUserLink,
    NotificationItem,
    ReviewQueueItem,
    ScheduleSlot,
    TestAttemptResult,
    TestAttemptStart,
    TestAttemptSubmission,
    TestQuestion,
    TestSummary,
    UserProfile,
    VisitLeadIn,
    VisitLeadOut,
)


def create_visit_lead(payload: VisitLeadIn) -> VisitLeadOut:
    client = create_clickhouse_client()
    lead_id = f"lead-{uuid4()}"
    now = utc_now()
    client.insert(
        table="visit_leads",
        data=[[lead_id, payload.name, payload.email, payload.phone, payload.message, now]],
        column_names=["id", "name", "email", "phone", "message", "created_at"],
    )
    return VisitLeadOut(id=lead_id, created_at=now)


def get_dashboard(user: UserProfile, demo_accounts) -> DashboardPayload:
    return DashboardPayload(
        user=user,
        courses=list_courses(user),
        schedule=list_schedule(user),
        notifications=list_notifications(user),
        external_links=list_external_links(user),
        review_queue=list_review_queue(user),
        demo_accounts=demo_accounts,
    )


def list_courses(user: UserProfile) -> list[CourseSummary]:
    client = create_clickhouse_client()
    if user.role == "student":
        rows = client.query(
            """
            SELECT c.id, c.title, c.description, c.teacher_name, c.audience, c.status, e.progress
            FROM courses FINAL AS c
            INNER JOIN course_enrollments FINAL AS e ON c.id = e.course_id
            WHERE e.user_id = %(user_id)s AND e.status = 'active'
            ORDER BY c.title
            """,
            parameters={"user_id": user.id},
        ).result_rows
    elif user.role == "teacher":
        rows = client.query(
            """
            SELECT id, title, description, teacher_name, audience, status, 100
            FROM courses FINAL
            WHERE teacher_id = %(user_id)s
            ORDER BY title
            """,
            parameters={"user_id": user.id},
        ).result_rows
    else:
        rows = client.query(
            """
            SELECT id, title, description, teacher_name, audience, status, 100
            FROM courses FINAL
            ORDER BY title
            """
        ).result_rows

    return [
        CourseSummary(
            id=row[0],
            title=row[1],
            description=row[2],
            teacher_name=row[3],
            audience=row[4],
            status=row[5],
            progress=int(row[6]),
        )
        for row in rows
    ]


def get_course_detail(user: UserProfile, course_id: str) -> CourseDetail:
    _ensure_course_access(user, course_id)
    client = create_clickhouse_client()
    course_row = client.query(
        """
        SELECT id, title, description, teacher_name, audience, status
        FROM courses FINAL
        WHERE id = %(course_id)s
        LIMIT 1
        """,
        parameters={"course_id": course_id},
    ).first_row
    if course_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")

    progress = _get_course_progress(user.id, course_id) if user.role == "student" else 100
    course = CourseSummary(
        id=course_row[0],
        title=course_row[1],
        description=course_row[2],
        teacher_name=course_row[3],
        audience=course_row[4],
        status=course_row[5],
        progress=progress,
    )

    progress_rows = client.query(
        """
        SELECT module_id, completed_at
        FROM course_module_progress FINAL
        WHERE user_id = %(user_id)s AND course_id = %(course_id)s AND status = 'completed'
        """,
        parameters={"user_id": user.id, "course_id": course_id},
    ).result_rows
    progress_map = {row[0]: row[1] for row in progress_rows}

    module_rows = client.query(
        """
        SELECT id, title, content, position, estimated_minutes
        FROM course_modules FINAL
        WHERE course_id = %(course_id)s
        ORDER BY position
        """,
        parameters={"course_id": course_id},
    ).result_rows
    modules = [
        CourseModule(
            id=row[0],
            title=row[1],
            content=row[2],
            position=row[3],
            estimated_minutes=row[4],
            completed=row[0] in progress_map,
            completed_at=progress_map.get(row[0]),
        )
        for row in module_rows
    ]

    tests = _list_course_tests(user, course_id)
    return CourseDetail(course=course, modules=modules, tests=tests)


def complete_module(user: UserProfile, course_id: str, module_id: str) -> CourseDetail:
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только студент может закрывать модули")
    _ensure_course_access(user, course_id)
    client = create_clickhouse_client()
    enrollment_id = _get_enrollment_id(user.id, course_id)
    if enrollment_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись на курс не найдена")

    progress_id = f"{enrollment_id}:{module_id}"
    now = utc_now()
    client.insert(
        "course_module_progress",
        [[progress_id, enrollment_id, course_id, module_id, user.id, "completed", now, now]],
        column_names=["id", "enrollment_id", "course_id", "module_id", "user_id", "status", "completed_at", "updated_at"],
    )
    _refresh_course_progress(user.id, course_id)
    return get_course_detail(user, course_id)


def start_test_attempt(user: UserProfile, test_id: str) -> TestAttemptStart:
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Тесты запускаются из студенческого кабинета")
    client = create_clickhouse_client()
    test_row = client.query(
        """
        SELECT id, course_id, title, description, duration_minutes, max_attempts, passing_score
        FROM tests FINAL
        WHERE id = %(test_id)s
        LIMIT 1
        """,
        parameters={"test_id": test_id},
    ).first_row
    if test_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")

    course_id = test_row[1]
    _ensure_course_access(user, course_id)
    attempts_count = client.query(
        """
        SELECT count()
        FROM test_attempts FINAL
        WHERE test_id = %(test_id)s AND user_id = %(user_id)s AND status = 'submitted'
        """,
        parameters={"test_id": test_id, "user_id": user.id},
    ).first_row[0]
    if attempts_count >= test_row[5]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Достигнут лимит попыток")

    active_attempt = client.query(
        """
        SELECT id, started_at
        FROM test_attempts FINAL
        WHERE test_id = %(test_id)s AND user_id = %(user_id)s AND status = 'in_progress'
        LIMIT 1
        """,
        parameters={"test_id": test_id, "user_id": user.id},
    ).first_row

    now = utc_now()
    attempt_id = active_attempt[0] if active_attempt is not None else f"attempt-{test_id}-{user.id}-{int(now.timestamp())}"
    started_at = active_attempt[1] if active_attempt is not None else now

    if active_attempt is None:
        teacher_id = _get_course_teacher_id(course_id)
        client.insert(
            "test_attempts",
            [[attempt_id, test_id, course_id, user.id, teacher_id, started_at, started_at, "in_progress", 0, 0, 0, "[]", "", "", now]],
            column_names=[
                "id",
                "test_id",
                "course_id",
                "user_id",
                "teacher_id",
                "started_at",
                "submitted_at",
                "status",
                "score",
                "total_points",
                "earned_points",
                "answers_json",
                "feedback",
                "reviewed_by",
                "updated_at",
            ],
        )

    questions = _get_test_questions(test_id)
    test = _test_row_to_summary(test_row, latest_status="in_progress", latest_score=None)
    return TestAttemptStart(attempt_id=attempt_id, test=test, questions=questions, started_at=started_at)


def submit_test_attempt(user: UserProfile, test_id: str, attempt_id: str, payload: TestAttemptSubmission) -> TestAttemptResult:
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    client = create_clickhouse_client()
    attempt_row = client.query(
        """
        SELECT id, course_id, teacher_id, started_at, status
        FROM test_attempts FINAL
        WHERE id = %(attempt_id)s AND test_id = %(test_id)s AND user_id = %(user_id)s
        LIMIT 1
        """,
        parameters={"attempt_id": attempt_id, "test_id": test_id, "user_id": user.id},
    ).first_row
    if attempt_row is None or attempt_row[4] != "in_progress":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Активная попытка не найдена")

    questions = _get_test_questions(test_id, include_correct=True)
    answers_map = {item.question_id: sorted(item.selected_option_ids) for item in payload.answers}
    total_points = sum(question["points"] for question in questions)
    earned_points = 0

    for question in questions:
        expected = sorted(question["correct_option_ids"])
        actual = answers_map.get(question["id"], [])
        if actual == expected:
            earned_points += question["points"]

    test_row = client.query(
        "SELECT passing_score FROM tests FINAL WHERE id = %(test_id)s LIMIT 1",
        parameters={"test_id": test_id},
    ).first_row
    passing_score = test_row[0]
    score = int(round((earned_points / total_points) * 100)) if total_points else 0
    now = utc_now()

    client.insert(
        "test_attempts",
        [[attempt_id, test_id, attempt_row[1], user.id, attempt_row[2], attempt_row[3], now, "submitted", score, total_points, earned_points, json.dumps([item.model_dump() for item in payload.answers]), "", "", now]],
        column_names=[
            "id",
            "test_id",
            "course_id",
            "user_id",
            "teacher_id",
            "started_at",
            "submitted_at",
            "status",
            "score",
            "total_points",
            "earned_points",
            "answers_json",
            "feedback",
            "reviewed_by",
            "updated_at",
        ],
    )

    _refresh_course_progress(user.id, attempt_row[1])
    _create_result_notifications(user.id, attempt_id, test_id, attempt_row[1], attempt_row[2], score)

    return TestAttemptResult(
        attempt_id=attempt_id,
        status="passed" if score >= passing_score else "failed",
        score=score,
        passing_score=passing_score,
        earned_points=earned_points,
        total_points=total_points,
        submitted_at=now,
    )


def list_schedule(user: UserProfile) -> list[ScheduleSlot]:
    client = create_clickhouse_client()
    if user.role == "student":
        rows = client.query(
            """
            SELECT id, course_id, subject, room, group_name, day_of_week, starts_at, ends_at, teacher_name
            FROM schedule_slots FINAL
            WHERE group_name = %(group_name)s
            ORDER BY day_of_week, starts_at
            """,
            parameters={"group_name": user.group_name},
        ).result_rows
    elif user.role == "teacher":
        rows = client.query(
            """
            SELECT id, course_id, subject, room, group_name, day_of_week, starts_at, ends_at, teacher_name
            FROM schedule_slots FINAL
            WHERE teacher_id = %(user_id)s
            ORDER BY day_of_week, starts_at
            """,
            parameters={"user_id": user.id},
        ).result_rows
    else:
        rows = client.query(
            """
            SELECT id, course_id, subject, room, group_name, day_of_week, starts_at, ends_at, teacher_name
            FROM schedule_slots FINAL
            ORDER BY day_of_week, starts_at
            """
        ).result_rows

    return [
        ScheduleSlot(
            id=row[0],
            course_id=row[1],
            subject=row[2],
            room=row[3],
            group_name=row[4],
            day_of_week=row[5],
            starts_at=row[6],
            ends_at=row[7],
            teacher_name=row[8],
        )
        for row in rows
    ]


def list_notifications(user: UserProfile) -> list[NotificationItem]:
    client = create_clickhouse_client()
    rows = client.query(
        """
        SELECT id, kind, title, body, entity_type, entity_id, created_at, is_read
        FROM notifications FINAL
        WHERE recipient_user_id = %(user_id)s
        ORDER BY created_at DESC
        LIMIT 10
        """,
        parameters={"user_id": user.id},
    ).result_rows
    return [
        NotificationItem(
            id=row[0],
            kind=row[1],
            title=row[2],
            body=row[3],
            entity_type=row[4],
            entity_id=row[5],
            created_at=row[6],
            is_read=bool(row[7]),
        )
        for row in rows
    ]


def list_external_links(user: UserProfile) -> list[ExternalUserLink]:
    client = create_clickhouse_client()
    rows = client.query(
        """
        SELECT id, external_system, external_user_id, external_username, linked_at
        FROM external_user_links FINAL
        WHERE local_user_id = %(user_id)s
        ORDER BY linked_at DESC
        """,
        parameters={"user_id": user.id},
    ).result_rows
    return [
        ExternalUserLink(
            id=row[0],
            external_system=row[1],
            external_user_id=row[2],
            external_username=row[3],
            linked_at=row[4],
        )
        for row in rows
    ]


def list_review_queue(user: UserProfile) -> list[ReviewQueueItem]:
    if user.role not in {"teacher", "admin"}:
        return []

    client = create_clickhouse_client()
    if user.role == "teacher":
        rows = client.query(
            """
            SELECT
                a.id,
                u.full_name,
                c.title,
                t.title,
                a.score,
                a.submitted_at,
                c.teacher_name
            FROM test_attempts FINAL AS a
            INNER JOIN users FINAL AS u ON a.user_id = u.id
            INNER JOIN courses FINAL AS c ON a.course_id = c.id
            INNER JOIN tests FINAL AS t ON a.test_id = t.id
            WHERE a.status = 'submitted' AND a.teacher_id = %(user_id)s
            ORDER BY a.submitted_at DESC
            """,
            parameters={"user_id": user.id},
        ).result_rows
    else:
        rows = client.query(
            """
            SELECT
                a.id,
                u.full_name,
                c.title,
                t.title,
                a.score,
                a.submitted_at,
                c.teacher_name
            FROM test_attempts FINAL AS a
            INNER JOIN users FINAL AS u ON a.user_id = u.id
            INNER JOIN courses FINAL AS c ON a.course_id = c.id
            INNER JOIN tests FINAL AS t ON a.test_id = t.id
            WHERE a.status = 'submitted'
            ORDER BY a.submitted_at DESC
            """
        ).result_rows

    return [
        ReviewQueueItem(
            attempt_id=row[0],
            student_name=row[1],
            course_title=row[2],
            test_title=row[3],
            score=row[4],
            submitted_at=row[5],
            teacher_name=row[6],
        )
        for row in rows
    ]


def _ensure_course_access(user: UserProfile, course_id: str) -> None:
    client = create_clickhouse_client()
    if user.role == "admin":
        return

    if user.role == "teacher":
        row = client.query(
            "SELECT id FROM courses FINAL WHERE id = %(course_id)s AND teacher_id = %(user_id)s LIMIT 1",
            parameters={"course_id": course_id, "user_id": user.id},
        ).first_row
    else:
        row = client.query(
            """
            SELECT id
            FROM course_enrollments FINAL
            WHERE course_id = %(course_id)s AND user_id = %(user_id)s AND status = 'active'
            LIMIT 1
            """,
            parameters={"course_id": course_id, "user_id": user.id},
        ).first_row

    if row is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к курсу")


def _list_course_tests(user: UserProfile, course_id: str) -> list[TestSummary]:
    client = create_clickhouse_client()
    rows = client.query(
        """
        SELECT id, course_id, title, description, duration_minutes, max_attempts, passing_score
        FROM tests FINAL
        WHERE course_id = %(course_id)s
        ORDER BY title
        """,
        parameters={"course_id": course_id},
    ).result_rows

    latest_by_test: dict[str, tuple[str, int | None]] = {}
    if user.role == "student":
        attempt_rows = client.query(
            """
            SELECT test_id, status, score, updated_at
            FROM test_attempts FINAL
            WHERE course_id = %(course_id)s AND user_id = %(user_id)s
            ORDER BY updated_at DESC
            """,
            parameters={"course_id": course_id, "user_id": user.id},
        ).result_rows
        for test_id, status_name, score, _ in attempt_rows:
            latest_by_test.setdefault(test_id, (status_name, score))

    return [
        _test_row_to_summary(
            row,
            latest_status=latest_by_test.get(row[0], ("new", None))[0],
            latest_score=latest_by_test.get(row[0], ("new", None))[1],
        )
        for row in rows
    ]


def _test_row_to_summary(row: tuple, latest_status: str, latest_score: int | None) -> TestSummary:
    return TestSummary(
        id=row[0],
        course_id=row[1],
        title=row[2],
        description=row[3],
        duration_minutes=row[4],
        max_attempts=row[5],
        passing_score=row[6],
        latest_status=latest_status,
        latest_score=latest_score,
    )


def _get_test_questions(test_id: str, include_correct: bool = False) -> list[TestQuestion] | list[dict[str, Any]]:
    client = create_clickhouse_client()
    rows = client.query(
        """
        SELECT id, prompt, options_json, correct_option_ids_json, question_type, position, points
        FROM test_questions FINAL
        WHERE test_id = %(test_id)s
        ORDER BY position
        """,
        parameters={"test_id": test_id},
    ).result_rows
    if include_correct:
        return [
            {
                "id": row[0],
                "prompt": row[1],
                "options": json.loads(row[2]),
                "correct_option_ids": json.loads(row[3]),
                "question_type": row[4],
                "position": row[5],
                "points": row[6],
            }
            for row in rows
        ]
    return [
        TestQuestion(
            id=row[0],
            prompt=row[1],
            options=json.loads(row[2]),
            question_type=row[4],
            position=row[5],
            points=row[6],
        )
        for row in rows
    ]


def _get_course_teacher_id(course_id: str) -> str:
    client = create_clickhouse_client()
    row = client.query(
        "SELECT teacher_id FROM courses FINAL WHERE id = %(course_id)s LIMIT 1",
        parameters={"course_id": course_id},
    ).first_row
    return row[0] if row else ""


def _get_enrollment_id(user_id: str, course_id: str) -> str | None:
    client = create_clickhouse_client()
    row = client.query(
        """
        SELECT id
        FROM course_enrollments FINAL
        WHERE user_id = %(user_id)s AND course_id = %(course_id)s
        LIMIT 1
        """,
        parameters={"user_id": user_id, "course_id": course_id},
    ).first_row
    return row[0] if row else None


def _get_course_progress(user_id: str, course_id: str) -> int:
    client = create_clickhouse_client()
    row = client.query(
        """
        SELECT progress
        FROM course_enrollments FINAL
        WHERE user_id = %(user_id)s AND course_id = %(course_id)s
        LIMIT 1
        """,
        parameters={"user_id": user_id, "course_id": course_id},
    ).first_row
    return int(row[0]) if row else 0


def _refresh_course_progress(user_id: str, course_id: str) -> None:
    client = create_clickhouse_client()
    enrollment_row = client.query(
        """
        SELECT id, role, status
        FROM course_enrollments FINAL
        WHERE user_id = %(user_id)s AND course_id = %(course_id)s
        LIMIT 1
        """,
        parameters={"user_id": user_id, "course_id": course_id},
    ).first_row
    if enrollment_row is None:
        return

    total_modules = client.query(
        "SELECT count() FROM course_modules FINAL WHERE course_id = %(course_id)s",
        parameters={"course_id": course_id},
    ).first_row[0]
    completed_modules = client.query(
        """
        SELECT count()
        FROM course_module_progress FINAL
        WHERE user_id = %(user_id)s AND course_id = %(course_id)s AND status = 'completed'
        """,
        parameters={"user_id": user_id, "course_id": course_id},
    ).first_row[0]
    test_rows = client.query(
        """
        SELECT t.id, t.passing_score
        FROM tests FINAL AS t
        WHERE t.course_id = %(course_id)s
        """,
        parameters={"course_id": course_id},
    ).result_rows
    passed_tests = 0
    for test_id, passing_score in test_rows:
        attempt = client.query(
            """
            SELECT max(score)
            FROM test_attempts FINAL
            WHERE user_id = %(user_id)s AND test_id = %(test_id)s AND status = 'submitted'
            """,
            parameters={"user_id": user_id, "test_id": test_id},
        ).first_row[0]
        if attempt is not None and int(attempt) >= int(passing_score):
            passed_tests += 1

    modules_ratio = completed_modules / total_modules if total_modules else 0
    tests_ratio = passed_tests / len(test_rows) if test_rows else 0
    progress = int(round((modules_ratio * 70) + (tests_ratio * 30)))

    now = utc_now()
    client.insert(
        "course_enrollments",
        [[enrollment_row[0], course_id, user_id, enrollment_row[1], progress, enrollment_row[2], now, now]],
        column_names=["id", "course_id", "user_id", "role", "progress", "status", "last_activity_at", "updated_at"],
    )


def _create_result_notifications(
    actor_user_id: str,
    attempt_id: str,
    test_id: str,
    course_id: str,
    teacher_id: str,
    score: int,
) -> None:
    client = create_clickhouse_client()
    user_name = client.query(
        "SELECT full_name FROM users FINAL WHERE id = %(user_id)s LIMIT 1",
        parameters={"user_id": actor_user_id},
    ).first_row[0]
    test_title = client.query(
        "SELECT title FROM tests FINAL WHERE id = %(test_id)s LIMIT 1",
        parameters={"test_id": test_id},
    ).first_row[0]
    course_title = client.query(
        "SELECT title FROM courses FINAL WHERE id = %(course_id)s LIMIT 1",
        parameters={"course_id": course_id},
    ).first_row[0]
    admin_rows = client.query(
        "SELECT id FROM users FINAL WHERE role = 'admin' AND status = 'approved'",
    ).result_rows

    recipients = {teacher_id, *(row[0] for row in admin_rows)}
    now = utc_now()
    notifications = []
    for recipient_id in recipients:
        if not recipient_id:
            continue
        notification_id = f"notify-{recipient_id}-{attempt_id}"
        notifications.append(
            [
                notification_id,
                recipient_id,
                actor_user_id,
                "test_result",
                f"Новый результат: {test_title}",
                f"{user_name} завершил тест '{test_title}' по курсу '{course_title}' с результатом {score}%.",
                "test_attempt",
                attempt_id,
                0,
                now,
                now,
            ]
        )
    if notifications:
        client.insert(
            "notifications",
            notifications,
            column_names=["id", "recipient_user_id", "actor_user_id", "kind", "title", "body", "entity_type", "entity_id", "is_read", "created_at", "updated_at"],
        )
