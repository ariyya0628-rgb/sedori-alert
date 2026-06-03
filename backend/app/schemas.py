from datetime import datetime

from pydantic import BaseModel, HttpUrl


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    display_name: str


class KeywordCreate(BaseModel):
    keyword: str
    shop_code: str = "all"


class KeywordUpdate(BaseModel):
    keyword: str | None = None
    shop_code: str | None = None
    enabled: bool | None = None


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    shop_code: str
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationSettingRequest(BaseModel):
    discord_webhook_url: HttpUrl | None = None
    discord_enabled: bool = False


class NotificationSettingResponse(BaseModel):
    discord_configured: bool
    discord_enabled: bool
    masked_webhook_url: str | None


class NotificationResponse(BaseModel):
    id: int
    shop_code: str
    product_title: str
    product_url: str
    matched_keyword: str
    discord_status: str
    discord_error: str | None
    notified_at: datetime

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    shop_code: str
    external_product_id: str
    title: str
    price: int
    product_url: str
    image_url: str | None
    category: str | None
    stock_status: str
    detected_at: datetime

    model_config = {"from_attributes": True}


class CrawlLogResponse(BaseModel):
    id: int
    shop_code: str
    status: str
    fetched_count: int
    matched_count: int
    notified_count: int
    duplicates_skipped: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime

    model_config = {"from_attributes": True}


class MockCrawlerRunResponse(BaseModel):
    fetched_count: int
    matched_count: int
    notifications_created: int
    duplicates_skipped: int


class ShopCrawlerRunResponse(MockCrawlerRunResponse):
    status: str
    error_message: str | None


class SchedulerSettingRequest(BaseModel):
    enabled: bool
    shop_code: str
    keyword: str
    interval_minutes: int
    limit: int


class SchedulerSettingResponse(BaseModel):
    enabled: bool
    shop_code: str
    keyword: str
    interval_minutes: int
    limit: int
    last_run_at: datetime | None
    next_run_at: datetime | None

    model_config = {"from_attributes": True}


class SchedulerRunDueResponse(BaseModel):
    ran: bool
    reason: str | None = None
    result: ShopCrawlerRunResponse | None = None
