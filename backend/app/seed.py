from sqlalchemy.orm import Session

from app.config import settings
from app.models import NotificationSetting, User
from app.security import hash_password


def seed_admin_user(db: Session) -> None:
    existing = db.query(User).filter(User.email == settings.seed_email).first()
    if existing:
        return

    user = User(
        email=settings.seed_email,
        password_hash=hash_password(settings.seed_password),
        display_name="Admin",
    )
    db.add(user)
    db.flush()
    db.add(NotificationSetting(user_id=user.id))
    db.commit()
