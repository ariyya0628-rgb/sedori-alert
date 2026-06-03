from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, crawl_logs, crawler, keywords, notification_settings, notifications, products, scheduler
from app.seed import seed_admin_user


Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed_admin_user(db)

app = FastAPI(title="Sedori Alert API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(keywords.router)
app.include_router(notification_settings.router)
app.include_router(notifications.router)
app.include_router(products.router)
app.include_router(crawl_logs.router)
app.include_router(crawler.router)
app.include_router(scheduler.router)


@app.get("/health")
def health():
    return {"status": "ok"}
