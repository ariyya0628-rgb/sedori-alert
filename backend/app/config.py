from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./sedori_alert.db"
    jwt_secret: str = "change-this-local-secret"
    webhook_crypto_secret: str = "change-this-local-webhook-secret"
    cors_origin: str = "http://localhost:5173"
    seed_email: str = "admin@example.com"
    seed_password: str = "password123"


settings = Settings()
