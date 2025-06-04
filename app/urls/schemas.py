from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class URLCreate(BaseModel):
    original_url: HttpUrl

    @field_validator("original_url", mode="before")
    def convert_str_to_httpurl(cls, v):
        if isinstance(v, str):
            return HttpUrl(v)
        return v

    model_config = ConfigDict(from_attributes=True)


class URLRead(BaseModel):
    id: int
    original_url: HttpUrl
    short_url: str
    clicks: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class URLStatsRead(BaseModel):
    short_url: str
    original_url: str
    last_hour_clicks: int | None = Field(default=None)
    last_day_clicks: int | None = Field(default=None)

    model_config = ConfigDict(from_attributes=True)
