from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_url: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    clicks: Mapped[int] = mapped_column(Integer, default=0)

    clicks_logs: Mapped[list["ClickLog"]] = relationship(
        "ClickLog", back_populates="url"
    )


class ClickLog(Base):
    __tablename__ = "click_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(
        ForeignKey("urls.id"), nullable=False, index=True
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    url: Mapped["URL"] = relationship("URL", back_populates="clicks_logs")
