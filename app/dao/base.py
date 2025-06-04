from sqlalchemy import select

from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_all(
        cls,
        offset: int | None = None,
        limit: int | None = None,
        **filters,
    ):
        async with async_session_maker() as session:
            query = select(cls.model)

            for field, value in filters.items():
                if value is not None and hasattr(cls.model, field):
                    query = query.where(getattr(cls.model, field) == value)

            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            result = await session.execute(query)
            return result.scalars().all()
