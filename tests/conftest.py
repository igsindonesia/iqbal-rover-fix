import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.core.db import Base, get_db
from src.users.models import User
# ========================
# Setup test database
# ========================
if os.getenv("GITHUB_ACTIONS") == "true":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    connect_args = {"check_same_thread": False}
else:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/rover_backend_test"
    connect_args = {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# ========================
# Dependency override
# ========================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ========================
# Pytest fixture TestClient
# ========================
@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_user(test_db):
    test_db.query(User).delete();
    test_db.commit()
    user = User(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        firstname="Test",
        lastname="User",
        username="testuser",
        email="test@example.com",
        password="hashedpassword"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    yield user
    # kalau udah jalan lalu dihapus record nya
    test_db.query(User).delete()
    test_db.commit()