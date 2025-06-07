import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import main_app
from src.database.config import get_db, init_db


SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread":False}
)

TestingSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False
)

init_db(engine=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

main_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestingSessionLocal(main_app) as c:
        yield c