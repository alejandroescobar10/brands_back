import sys, asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import asyncio
import sqlalchemy as sa
from api.db.session import engine

async def main():
    async with engine.connect() as conn:
        val = await conn.scalar(sa.text("SELECT 1"))
        print("DB OK:", val)

if __name__ == "__main__":
    asyncio.run(main())
