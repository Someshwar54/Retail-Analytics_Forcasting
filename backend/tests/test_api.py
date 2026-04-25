"""
test_api.py — Integration tests for the Retail Analytics & Forecasting API.

These tests use FastAPI's TestClient with an in-memory SQLite database
to verify that all endpoints return valid responses after seeding.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# We need to override the DB dependency *before* importing the app
from app.db.session import Base
from app.db.models.retail import Store, Product, Transaction
from app.api.dependencies import get_db
from app.main import app

# ── Test Database Setup ──────────────────────────────────────────────────────

TEST_DB_URL = "sqlite:///./test_retail_analytics.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """
    Creates schema and seeds a small synthetic dataset for testing.
    Runs once per test module.
    """
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()

    try:
        # Create stores (need at least n_clusters=4 stores for default segmentation test)
        stores = [
            Store(store_location="Downtown", store_rating=4.5),
            Store(store_location="Suburban Mall", store_rating=3.8),
            Store(store_location="Airport Terminal", store_rating=4.2),
            Store(store_location="Harbor District", store_rating=3.2),
            Store(store_location="University Plaza", store_rating=4.8),
        ]
        session.add_all(stores)
        session.commit()
        for s in stores:
            session.refresh(s)

        # Create products
        products = [
            Product(category="Electronics", subcategory="Phones", brand="TechBrand", unit_price=599.99, stock_on_hand=100),
            Product(category="Clothing", subcategory="Shirts", brand="FashionCo", unit_price=49.99, stock_on_hand=500),
            Product(category="Groceries", subcategory="Dairy", brand="FarmFresh", unit_price=3.99, stock_on_hand=1000),
        ]
        session.add_all(products)
        session.commit()
        for p in products:
            session.refresh(p)

        # Create synthetic transactions spanning 90 days
        base_date = datetime(2024, 1, 1)
        transactions = []
        for day_offset in range(90):
            for store in stores:
                for product in products:
                    transactions.append(Transaction(
                        store_id=store.id,
                        product_id=product.id,
                        timestamp=base_date + timedelta(days=day_offset),
                        discount_percentage=5.0 if day_offset % 7 == 0 else 0.0,
                        revenue=product.unit_price * (1 + day_offset * 0.01),
                        customer_type="Returning" if day_offset % 3 == 0 else "New",
                        payment_mode="Card" if day_offset % 2 == 0 else "Cash",
                        promotion_applied=day_offset % 14 == 0,
                        holiday_flag=day_offset % 30 == 0,
                    ))

        session.bulk_save_objects(transactions)
        session.commit()

        yield  # Tests run here

    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()  # Release all connections so Windows can delete the file
        # Clean up the test database file
        import os
        try:
            if os.path.exists("test_retail_analytics.db"):
                os.remove("test_retail_analytics.db")
        except PermissionError:
            pass  # Windows may still hold the file briefly; ignore


# ── Health Check Tests ───────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# ── Forecast Endpoint Tests ─────────────────────────────────────────────────

class TestForecastEndpoint:
    def test_forecast_default_steps(self):
        """Test forecasting with default 30-day horizon."""
        response = client.get("/api/v1/forecast/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "forecast_chart" in data
        assert "predictions_head" in data

    def test_forecast_custom_steps(self):
        """Test forecasting with a custom 7-day horizon."""
        response = client.get("/api/v1/forecast/?steps=7")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


# ── Driver Analysis Endpoint Tests ──────────────────────────────────────────

class TestDriversEndpoint:
    def test_drivers_analysis(self):
        """Test that sales driver analysis returns SHAP importance data."""
        response = client.get("/api/v1/drivers/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "drivers_chart" in data
        assert "global_importance" in data
        assert len(data["global_importance"]) > 0


# ── Store Segmentation Endpoint Tests ────────────────────────────────────────

class TestSegmentsEndpoint:
    def test_segments_default_clusters(self):
        """Test store segmentation with default 4 clusters."""
        response = client.get("/api/v1/segments/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "segments_chart" in data
        assert "cluster_summary" in data
        assert "store_assignments" in data

    def test_segments_custom_clusters(self):
        """Test store segmentation with 2 clusters."""
        response = client.get("/api/v1/segments/?n_clusters=2")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["cluster_summary"]) == 2
