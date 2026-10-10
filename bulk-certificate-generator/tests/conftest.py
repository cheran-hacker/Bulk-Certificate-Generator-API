import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.main import app as fastapi_app
from app.db.base import Base
from app.api.dependencies import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

fastapi_app.dependency_overrides[get_db] = override_get_db

import app.services.processing_service
app.services.processing_service.SessionLocal = TestingSessionLocal

@pytest.fixture(scope="function", autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    with TestClient(fastapi_app) as c:
        yield c
        
@pytest.fixture(autouse=True)
def set_env():
    os.environ["CERTIFICATE_STORAGE_PATH"] = "test_certificates"
    yield
    import shutil
    if os.path.exists("test_certificates"):
        shutil.rmtree("test_certificates")
