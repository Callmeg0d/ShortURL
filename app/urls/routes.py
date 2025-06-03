from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.exceptions import (CannotFindURLException, ExpiredURLException,
                            InactiveURLException)
from app.urls.dao import URLDAO
from app.urls.schemas import URLCreate, URLRead

EXPIRATION_TIME = timedelta(days=1)

router = APIRouter(prefix="/urls", tags=["URLs"])


@router.post("/create", response_model=URLRead)
async def create_short_url(url_data: URLCreate):
    url = await URLDAO.create_short_url(url_data)
    return url


@router.get("/all", response_model=List[URLRead])
async def get_all_urls():
    urls = await URLDAO.find_all()
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


@router.get("/{short_url}", response_model=URLRead)
async def get_info_by_short_url(short_url: str):
    url = await URLDAO.get_by_short_url(short_url)
    if not url:
        raise CannotFindURLException
    return url


@router.get("/stats/{short_url}")
async def get_click_stats_by_short_url(short_url: str):
    stats = await URLDAO.get_stats_by_short_url(short_url)
    if not stats:
        raise CannotFindURLException
    return stats
