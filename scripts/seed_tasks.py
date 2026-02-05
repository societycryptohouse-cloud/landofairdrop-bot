import asyncio

from packages.db.seed import seed_tasks
from packages.db.session import async_session_maker


async def main():
    async with async_session_maker() as session:
        result = await seed_tasks(session)
        print(f"Seed done: created={result['created']} updated={result['updated']}")


if __name__ == "__main__":
    asyncio.run(main())
