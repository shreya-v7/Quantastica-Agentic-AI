"""Run actual migrated PostgreSQL triggers, not just ORM metadata."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer


async def test_migrated_event_log_rejects_rewrites_and_clock_regression():
    with PostgresContainer("pgvector/pgvector:pg16") as pg:
        url = pg.get_connection_url().replace("psycopg2", "asyncpg")
        env = dict(os.environ, DATABASE_URL=url, ANTHROPIC_API_KEY="ci-placeholder")
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            env=env,
            cwd=Path(__file__).resolve().parents[1],
            check=True,
        )
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.execute(text("""
                INSERT INTO book_events
                    (id, household_id, event_type, payload, seq, idempotency_key,
                     created_at, valid_time, recorded_time)
                VALUES
                    ('e1', 'hh', 'book.snapshot', '{}'::jsonb, 1, 'e1',
                     now(), now(), now())
            """))
        commands = [
            "UPDATE book_events SET payload='{}'::jsonb WHERE id='e1'",
            "DELETE FROM book_events WHERE id='e1'",
            """INSERT INTO book_events
                (id, household_id, event_type, payload, seq, idempotency_key,
                 created_at, valid_time, recorded_time)
                SELECT 'e2', household_id, event_type, payload, 2, 'e2',
                       created_at, valid_time, recorded_time
                FROM book_events WHERE id='e1'""",
        ]
        for command in commands:
            with pytest.raises(DBAPIError):
                async with engine.begin() as conn:
                    await conn.execute(text(command))
        await engine.dispose()
