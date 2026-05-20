import asyncpg
from asyncpg import Pool

_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    tg_id      BIGINT PRIMARY KEY,
    username   TEXT,
    full_name  TEXT,
    phone      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

_CREATE_CARS = """
CREATE TABLE IF NOT EXISTS cars (
    id         SERIAL PRIMARY KEY,
    tg_id      BIGINT REFERENCES users(tg_id) ON DELETE CASCADE,
    details    TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

_CREATE_APPOINTMENTS = """
CREATE TABLE IF NOT EXISTS appointments (
    id         SERIAL PRIMARY KEY,
    tg_id      BIGINT REFERENCES users(tg_id) ON DELETE CASCADE,
    car_id     INT  REFERENCES cars(id) ON DELETE CASCADE,
    service    TEXT NOT NULL,
    slot       TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

db_pool: Pool | None = None


async def init_db(pg_url: str) -> Pool:
    global db_pool
    db_pool = await asyncpg.create_pool(pg_url, min_size=2, max_size=10)
    async with db_pool.acquire() as conn:
        await conn.execute(_CREATE_USERS)
        await conn.execute(_CREATE_CARS)
        await conn.execute(_CREATE_APPOINTMENTS)
    return db_pool


async def close_db() -> None:
    if db_pool:
        await db_pool.close()
