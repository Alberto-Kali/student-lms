import json

from app.core.config import settings
from app.core.security import hash_password, utc_now
from app.db.clickhouse import create_clickhouse_client


def ensure_schema() -> None:
    admin_client = create_clickhouse_client(database="")
    admin_client.command(f"CREATE DATABASE IF NOT EXISTS {settings.clickhouse_database}")

    client = create_clickhouse_client(settings.clickhouse_database)

    statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id String,
            username String,
            password_hash String,
            full_name String,
            role LowCardinality(String),
            status LowCardinality(String),
            email String,
            group_name String,
            department String,
            created_at DateTime,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS auth_sessions (
            id String,
            user_id String,
            token_hash String,
            created_at DateTime,
            expires_at DateTime,
            revoked UInt8,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS external_user_links (
            id String,
            local_user_id String,
            external_system String,
            external_user_id String,
            external_username String,
            linked_at DateTime,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS courses (
            id String,
            title String,
            description String,
            teacher_id String,
            teacher_name String,
            audience String,
            status LowCardinality(String),
            created_at DateTime,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS course_modules (
            id String,
            course_id String,
            title String,
            content String,
            position UInt16,
            estimated_minutes UInt16,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS course_enrollments (
            id String,
            course_id String,
            user_id String,
            role LowCardinality(String),
            progress UInt8,
            status LowCardinality(String),
            last_activity_at DateTime,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS course_module_progress (
            id String,
            enrollment_id String,
            course_id String,
            module_id String,
            user_id String,
            status LowCardinality(String),
            completed_at DateTime,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS tests (
            id String,
            course_id String,
            title String,
            description String,
            duration_minutes UInt16,
            max_attempts UInt8,
            passing_score UInt8,
            created_by_user_id String,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS test_questions (
            id String,
            test_id String,
            prompt String,
            options_json String,
            correct_option_ids_json String,
            question_type LowCardinality(String),
            position UInt16,
            points UInt8,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS test_attempts (
            id String,
            test_id String,
            course_id String,
            user_id String,
            teacher_id String,
            started_at DateTime,
            submitted_at DateTime,
            status LowCardinality(String),
            score UInt8,
            total_points UInt16,
            earned_points UInt16,
            answers_json String,
            feedback String,
            reviewed_by String,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS schedule_slots (
            id String,
            course_id String,
            teacher_id String,
            teacher_name String,
            group_name String,
            day_of_week UInt8,
            starts_at String,
            ends_at String,
            room String,
            subject String,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id String,
            recipient_user_id String,
            actor_user_id String,
            kind LowCardinality(String),
            title String,
            body String,
            entity_type String,
            entity_id String,
            is_read UInt8,
            created_at DateTime,
            updated_at DateTime
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
        """
        CREATE TABLE IF NOT EXISTS visit_leads (
            id String,
            name String,
            email String,
            phone String,
            message String,
            created_at DateTime
        ) ENGINE = MergeTree
        ORDER BY created_at
        """,
    ]

    for statement in statements:
        client.command(statement)

    users_count = client.query("SELECT count() FROM users").first_row[0]
    if users_count == 0:
        _seed_data(client)


def _seed_data(client) -> None:
    now = utc_now()
    users = [
        ["user-admin", "admin", hash_password("admin123"), "Наталья Рощина", "admin", "approved", "admin@college39.ru", "", "Цифровая платформа", now, now],
        ["user-teacher", "teacher", hash_password("teacher123"), "Ольга Савельева", "teacher", "approved", "teacher@college39.ru", "", "Кафедра программирования", now, now],
        ["user-student", "student", hash_password("student123"), "Альберто Дженуарди", "student", "approved", "student@college39.ru", "ИСП24-23", "", now, now],
        ["user-pending", "pending.student", hash_password("student123"), "Ирина Логинова", "student", "pending", "pending@college39.ru", "ИСП24-24", "", now, now],
        ["user-blocked", "blocked.teacher", hash_password("teacher123"), "Кирилл Денисов", "teacher", "blocked", "blocked@college39.ru", "", "Сетевые технологии", now, now],
    ]
    client.insert(
        "users",
        users,
        column_names=[
            "id",
            "username",
            "password_hash",
            "full_name",
            "role",
            "status",
            "email",
            "group_name",
            "department",
            "created_at",
            "updated_at",
        ],
    )

    courses = [
        ["course-ts", "Программирование на TypeScript", "Полный курс по компонентной архитектуре, типизации и сервисному взаимодействию.", "user-teacher", "Ольга Савельева", "ИСП24-23", "active", now, now],
        ["course-db", "Базы данных и SQL", "Практика проектирования схем, аналитических запросов и ClickHouse-паттернов.", "user-teacher", "Ольга Савельева", "ИСП24-23", "active", now, now],
    ]
    client.insert(
        "courses",
        courses,
        column_names=["id", "title", "description", "teacher_id", "teacher_name", "audience", "status", "created_at", "updated_at"],
    )

    modules = [
        ["module-ts-1", "course-ts", "Введение в курс", "Знакомство с программой, целями и критериями оценки.", 1, 20, now],
        ["module-ts-2", "course-ts", "Компоненты и композиция", "Практика построения UI-модулей и разделения по зонам ответственности.", 2, 35, now],
        ["module-ts-3", "course-ts", "API и состояние", "Работа с запросами, авторизацией и хранением сессии на фронте.", 3, 40, now],
        ["module-db-1", "course-db", "Реляционные основы", "Нормализация, связи и контроль качества схемы.", 1, 30, now],
        ["module-db-2", "course-db", "ClickHouse для LMS", "Append-only модель, аналитика и ReplacingMergeTree.", 2, 45, now],
    ]
    client.insert(
        "course_modules",
        modules,
        column_names=["id", "course_id", "title", "content", "position", "estimated_minutes", "updated_at"],
    )

    enrollments = [
        ["enroll-student-ts", "course-ts", "user-student", "student", 0, "active", now, now],
        ["enroll-student-db", "course-db", "user-student", "student", 0, "active", now, now],
    ]
    client.insert(
        "course_enrollments",
        enrollments,
        column_names=["id", "course_id", "user_id", "role", "progress", "status", "last_activity_at", "updated_at"],
    )

    tests = [
        ["test-ts-1", "course-ts", "Итоговый тест по TypeScript", "Проверка структуры SPA и типизации.", 30, 3, 70, "user-teacher", now],
        ["test-db-1", "course-db", "Контрольная по SQL и ClickHouse", "Проверка архитектуры БД и аналитических запросов.", 35, 3, 70, "user-teacher", now],
    ]
    client.insert(
        "tests",
        tests,
        column_names=["id", "course_id", "title", "description", "duration_minutes", "max_attempts", "passing_score", "created_by_user_id", "updated_at"],
    )

    questions = [
        [
            "q-ts-1",
            "test-ts-1",
            "Что лучше использовать для доступа к backend API на фронтенде?",
            json.dumps(["Прямые SQL-запросы", "Выделенный api-клиент", "Случайные fetch внутри компонентов"], ensure_ascii=False),
            json.dumps([1]),
            "single",
            1,
            5,
            now,
        ],
        [
            "q-ts-2",
            "test-ts-1",
            "Какие задачи должны быть на backend при авторизации?",
            json.dumps(["Хранение password_hash", "Проверка пароля", "Выдача сессии", "Рендеринг CSS"], ensure_ascii=False),
            json.dumps([0, 1, 2]),
            "multiple",
            2,
            10,
            now,
        ],
        [
            "q-db-1",
            "test-db-1",
            "Почему для append-only истории в ClickHouse удобно использовать ReplacingMergeTree?",
            json.dumps(["Он хранит последнюю версию записи", "Он заменяет nginx", "Он позволяет писать историю без update"], ensure_ascii=False),
            json.dumps([0, 2]),
            "multiple",
            1,
            10,
            now,
        ],
        [
            "q-db-2",
            "test-db-1",
            "Где нужна таблица сверки локальных и внешних пользователей?",
            json.dumps(["Для интеграции с внешними LMS", "Для CSS-тем", "Для расписания аудиторий"], ensure_ascii=False),
            json.dumps([0]),
            "single",
            2,
            5,
            now,
        ],
    ]
    client.insert(
        "test_questions",
        questions,
        column_names=["id", "test_id", "prompt", "options_json", "correct_option_ids_json", "question_type", "position", "points", "updated_at"],
    )

    schedule = [
        ["slot-1", "course-ts", "user-teacher", "Ольга Савельева", "ИСП24-23", 1, "08:30", "10:00", "A-304", "Программирование на TypeScript", now],
        ["slot-2", "course-db", "user-teacher", "Ольга Савельева", "ИСП24-23", 3, "10:15", "11:45", "A-211", "Базы данных и SQL", now],
    ]
    client.insert(
        "schedule_slots",
        schedule,
        column_names=["id", "course_id", "teacher_id", "teacher_name", "group_name", "day_of_week", "starts_at", "ends_at", "room", "subject", "updated_at"],
    )

    links = [
        ["link-1", "user-teacher", "sovereign-lms-alpha", "t-842", "olga.s", now, now],
        ["link-2", "user-teacher", "regional-college-portal", "teacher-77", "savelieva_olga", now, now],
    ]
    client.insert(
        "external_user_links",
        links,
        column_names=["id", "local_user_id", "external_system", "external_user_id", "external_username", "linked_at", "updated_at"],
    )
