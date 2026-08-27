"""
Pytest fixtures and configuration for the ShortLink API test suite.

Creates an isolated test database (SQLite in-memory) and a
FastAPI TestClient for every test function, ensuring tests
never affect real data.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Use a file-based SQLite database for tests so we can inspect
# it during debugging if needed. The file is cleaned up between
# tests via drop_all.
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database and session for each test function.

    All tables are created before the test and dropped after,
    providing complete isolation between tests.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI TestClient that uses the isolated test database.

    Overrides the get_db dependency so all requests during the
    test go through the temporary database created by db_session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # db_session is cleaned up by its own fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()