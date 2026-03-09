from app.core.config import settings
from app.db.clickhouse import create_clickhouse_client


def ensure_schema() -> None:
    admin_client = create_clickhouse_client(database="")
    admin_client.command(f"CREATE DATABASE IF NOT EXISTS {settings.clickhouse_database}")

    client = create_clickhouse_client(settings.clickhouse_database)

    client.command(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id UInt64,
            title String,
            teacher String,
            group_name String,
            progress UInt8,
            modules UInt16,
            status LowCardinality(String),
            updated_at DateTime DEFAULT now()
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """
    )

    client.command(
        """
        CREATE TABLE IF NOT EXISTS visit_leads (
            id UUID,
            name String,
            email String,
            phone String,
            message String,
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree
        ORDER BY created_at
        """
    )

    rows = client.query("SELECT count() FROM courses").result_rows
    if rows and rows[0][0] == 0:
        client.command(
            """
            INSERT INTO courses (id, title, teacher, group_name, progress, modules, status)
            VALUES
              (1, 'Programming with Python', 'Savelieva O.I.', 'ISP24-23', 74, 12, 'active'),
              (2, 'Databases and SQL', 'Karpenko N.A.', 'ISP24-23', 58, 10, 'active'),
              (3, 'Computer Networks', 'Gromov K.A.', 'ISP24-22', 40, 11, 'active')
            """
        )
