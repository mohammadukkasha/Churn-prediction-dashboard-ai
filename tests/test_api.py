# tests/test_api.py
import os
import sys
# Make sure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Override DATABASE_URL before any app import ──────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_churn.db"

from app.database import Base, get_db   # noqa: E402
from app.main import app                # noqa: E402

# ── Test DB (SQLite) setup ───────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///./test_churn.db"
engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables in the test DB
Base.metadata.create_all(bind=engine_test)

client = TestClient(app)


# ── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def clean_tables():
    """Wipe tables before each test to ensure isolation."""
    from app.models import Customer, Prediction
    db = TestingSession()
    db.query(Prediction).delete()
    db.query(Customer).delete()
    db.commit()
    db.close()
    yield


SAMPLE_CUSTOMER = {
    "gender": "Female",
    "seniorcitizen": 0,
    "partner": "Yes",
    "dependents": "No",
    "tenure": 1,
    "phoneservice": "No",
    "multiplelines": "No phone service",
    "internetservice": "DSL",
    "onlinesecurity": "No",
    "onlinebackup": "Yes",
    "deviceprotection": "No",
    "techsupport": "No",
    "streamingtv": "No",
    "streamingmovies": "No",
    "contract": "Month-to-month",
    "paperlessbilling": "Yes",
    "paymentmethod": "Electronic check",
    "monthlycharges": 29.85,
    "totalcharges": 29.85
}


# ── Tests ─────────────────────────────────────────────────────────────────────
class TestHealthCheck:
    def test_root_returns_running(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "running"


class TestCustomerCreate:
    def test_create_customer_success(self):
        r = client.post("/api/customers", json=SAMPLE_CUSTOMER)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["gender"] == "Female"
        assert data["monthlycharges"] == 29.85
        assert "id" in data

    def test_create_customer_returns_prediction(self):
        r = client.post("/api/customers", json=SAMPLE_CUSTOMER)
        assert r.status_code == 201, r.text
        data = r.json()
        assert "prediction" in data
        pred = data["prediction"]
        assert pred is not None
        assert pred["prediction"] in ("Yes", "No")


class TestCustomerRead:
    def test_get_all_empty(self):
        r = client.get("/api/customers")
        assert r.status_code == 200
        assert r.json() == []

    def test_get_all_after_create(self):
        client.post("/api/customers", json=SAMPLE_CUSTOMER)
        r = client.get("/api/customers")
        assert r.status_code == 200
        assert len(r.json()) == 1


class TestDashboard:
    def test_dashboard_with_customers(self):
        client.post("/api/customers", json=SAMPLE_CUSTOMER)
        r = client.get("/api/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert data["total_customers"] == 1
        assert data["avg_monthly_charges"] == 29.85
