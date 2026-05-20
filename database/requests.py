from asyncpg import Pool


async def upsert_user(pool: Pool, tg_id: int, username: str | None, full_name: str, phone: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (tg_id, username, full_name, phone)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (tg_id) DO UPDATE
                SET phone     = EXCLUDED.phone,
                    full_name = EXCLUDED.full_name;
            """,
            tg_id, username, full_name, phone,
        )


async def insert_car(pool: Pool, tg_id: int, details: str) -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO cars (tg_id, details) VALUES ($1, $2) RETURNING id;",
            tg_id, details,
        )
        return row["id"]


async def insert_appointment(pool: Pool, tg_id: int, car_id: int, service: str, slot: str) -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO appointments (tg_id, car_id, service, slot) VALUES ($1, $2, $3, $4) RETURNING id;",
            tg_id, car_id, service, slot,
        )
        return row["id"]


async def is_slot_taken(pool: Pool, slot: str) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM appointments WHERE slot = $1 LIMIT 1;", slot)
        return row is not None
