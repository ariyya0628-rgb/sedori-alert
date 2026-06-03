from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.time_utils import utc_now


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(100), default="Admin")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    shop_code: Mapped[str] = mapped_column(String(50), default="all")
    min_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    include_terms: Mapped[str] = mapped_column(Text, default="")
    exclude_terms: Mapped[str] = mapped_column(Text, default="")
    allowed_condition_ranks: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    user: Mapped[User] = relationship()


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    discord_webhook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    discord_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    user: Mapped[User] = relationship()


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    shop_code: Mapped[str] = mapped_column(String(50), default="manual")
    product_title: Mapped[str] = mapped_column(String(500))
    product_url: Mapped[str] = mapped_column(Text)
    matched_keyword: Mapped[str] = mapped_column(String(255))
    discord_status: Mapped[str] = mapped_column(String(50))
    discord_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    skip_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notified_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    user: Mapped[User] = relationship()


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shop_code: Mapped[str] = mapped_column(String(50), index=True)
    external_product_id: Mapped[str] = mapped_column(String(255), index=True)
    unique_key: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    price: Mapped[int] = mapped_column(Integer, default=0)
    product_url: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    condition_rank: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stock_status: Mapped[str] = mapped_column(String(50), default="instock")
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shop_code: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50))
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    matched_count: Mapped[int] = mapped_column(Integer, default=0)
    notified_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicates_skipped: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    finished_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class SchedulerSetting(Base):
    __tablename__ = "scheduler_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    shop_code: Mapped[str] = mapped_column(String(50), default="offmall")
    keyword: Mapped[str] = mapped_column(String(255), default="")
    interval_minutes: Mapped[int] = mapped_column(Integer, default=10)
    limit: Mapped[int] = mapped_column(Integer, default=10)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
