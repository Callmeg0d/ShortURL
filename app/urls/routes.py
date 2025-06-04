from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.exceptions import (
    CannotFindURLException,
    ExpiredURLException,
    InactiveURLException,
)
from app.urls.dao import URLDAO
from app.urls.schemas import URLCreate, URLRead, URLStatsRead

EXPIRATION_TIME = timedelta(days=1)

router = APIRouter(prefix="/urls", tags=["URLs"])


@router.post("/create", response_model=URLRead)
async def create_short_url(url_data: URLCreate):
    url = await URLDAO.create_short_url(url_data)
    return url


@router.get("/all", response_model=List[URLRead])
async def get_all_urls(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    is_active: bool | None = Query(None),
):
    urls = await URLDAO.find_all_urls(
        offset=(page - 1) * size,
        limit=size,
        is_active=is_active,
    )
    return urls


@router.get("/r/{short_url}")
async def redirect_to_original(short_url: str):
    url = await URLDAO.get_by_short_url(short_url)
    if not url:
        raise CannotFindURLException
    if not url.is_active:
        raise InactiveURLException
    if datetime.now(timezone.utc) > url.created_at + EXPIRATION_TIME:
        raise ExpiredURLException

    await URLDAO.log_click(url.id)

    await URLDAO.increment_clicks(url)

    return JSONResponse({"original_url": url.original_url})


@router.patch("/deactivate/{short_url}")
async def deactivate_url(short_url: str):
    updated = await URLDAO.deactivate_url(short_url)
    if updated is None:
        raise CannotFindURLException
    if not updated:
        raise InactiveURLException


@router.get("/stats", response_model=List[URLStatsRead])
async def get_all_url_stats():
    return await URLDAO.get_stats_for_all_urls()


@router.get("/stats/hour", response_model=List[URLStatsRead])
async def get_stats_sorted_by_hour():
    return await URLDAO.get_stats_sorted_by_clicks("hour")


@router.get("/stats/day", response_model=List[URLStatsRead])
async def get_stats_sorted_by_day():
    return await URLDAO.get_stats_sorted_by_clicks("day")


@router.get("/{short_url}", response_model=URLRead)
async def get_info_by_short_url(short_url: str):
    url = await URLDAO.get_by_short_url(short_url)
    if not url:
        raise CannotFindURLException
    return url
