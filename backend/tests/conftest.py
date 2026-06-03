import os
import tempfile
from pathlib import Path


test_db_path = Path(tempfile.gettempdir()) / f"sedori_alert_pytest_{os.getpid()}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path.as_posix()}"

import pytest  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.seed import seed_admin_user  # noqa: E402


@pytest.fixture(autouse=True)
def reset_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_admin_user(db)
    yield
