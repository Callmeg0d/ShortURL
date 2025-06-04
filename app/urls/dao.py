import random
import string
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select, update

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.urls.models import URL, ClickLog
from app.urls.schemas import URLCreate


def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


class URLDAO(BaseDAO):
    model = URL

    @classmethod
    async def create_short_url(cls, url_data: URLCreate) -> URL:
        short_code = generate_short_code()
        original_url_str = str(url_data.original_url)
        new_url = URL(original_url=original_url_str, short_url=short_code)

        async with async_session_maker() as session:
            session.add(new_url)
            await session.commit()
            await session.refresh(new_url)
            return new_url

    @classmethod
    async def get_by_short_url(cls, short_url: str) -> URL | None:
        async with async_session_maker() as session:
            result = await session.execute(
                select(URL).where(URL.short_url == short_url)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def increment_clicks(cls, url: URL) -> None:
        async with async_session_maker() as session:
            await session.execute(
                update(URL).where(URL.id == url.id).values(clicks=URL.clicks + 1)
            )
            await session.commit()

    @classmethod
    async def deactivate_url(cls, short_url: str) -> bool | None:
        async with async_session_maker() as session:
            url = await session.execute(
                select(URL.is_active).where(URL.short_url == short_url)
            )
            url = url.scalar_one_or_none()

            if url is None:
                return None
            if not url:
                return False

            result = await session.execute(
                update(URL)
                .where(URL.short_url == short_url, URL.is_active == True)
                .values(is_active=False)
            )
            await session.commit()
            return result.rowcount > 0

    @classmethod
    async def log_click(cls, url_id: int) -> None:
        async with async_session_maker() as session:
            click = ClickLog(url_id=url_id)
            session.add(click)
            await session.commit()

    @classmethod
    async def get_stats_for_all_urls(cls):
        async with async_session_maker() as session:
            now = datetime.now(timezone.utc)
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(days=1)

            result = await session.execute(select(cls.model))
            urls = result.scalars().all()

            stats = []
            for url in urls:
                clicks_last_hour = await session.execute(
                    select(func.count()).where(
                        ClickLog.url_id == url.id,
                        ClickLog.clicked_at >= one_hour_ago,
                    )
                )
                clicks_last_day = await session.execute(
                    select(func.count()).where(
                        ClickLog.url_id == url.id,
                        ClickLog.clicked_at >= one_day_ago,
                    )
                )

                stats.append(
                    {
                        "short_url": url.short_url,
                        "original_url": url.original_url,
                        "last_hour_clicks": clicks_last_hour.scalar(),
                        "last_day_clicks": clicks_last_day.scalar(),
                    }
                )

            return stats

    @classmethod
    async def find_all_urls(
        cls,
        offset: int | None = None,
        limit: int | None = None,
        is_active: bool | None = None,
    ):
        return await cls.find_all(
            offset=offset,
            limit=limit,
            is_active=is_active,
        )

    @classmethod
    async def get_stats_sorted_by_clicks(cls, period: str):
        async with async_session_maker() as session:
            now = datetime.now(timezone.utc)
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(days=1)

            subquery = (
                select(
                    ClickLog.url_id,
                    func.count(case((ClickLog.clicked_at >= one_hour_ago, 1))).label(
                        "clicks_last_hour"
                    ),
                    func.count(case((ClickLog.clicked_at >= one_day_ago, 1))).label(
                        "clicks_last_day"
                    ),
                )
                .group_by(ClickLog.url_id)
                .subquery()
            )

            query = select(
                cls.model.short_url,
                cls.model.original_url,
                func.coalesce(subquery.c.clicks_last_hour, 0).label("last_hour_clicks"),
                func.coalesce(subquery.c.clicks_last_day, 0).label("last_day_clicks"),
            ).outerjoin(subquery, cls.model.id == subquery.c.url_id)

            if period == "hour":
                order_col = func.coalesce(subquery.c.clicks_last_hour, 0)
            elif period == "day":
                order_col = func.coalesce(subquery.c.clicks_last_day, 0)
            else:
                raise ValueError("Invalid period: use 'hour' or 'day'")

            query = query.order_by(order_col.desc())

            result = await session.execute(query)
            rows = result.all()

            stats = [
                {
                    "short_url": row.short_url,
                    "original_url": row.original_url,
                    "last_hour_clicks": row.last_hour_clicks,
                    "last_day_clicks": row.last_day_clicks,
                }
                for row in rows
            ]

            return stats
