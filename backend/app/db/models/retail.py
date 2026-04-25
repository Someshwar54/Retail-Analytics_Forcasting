from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..session import Base

class Store(Base):
    """
    SQLAlchemy model representing a retail store.
    """
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    store_location = Column(String, index=True, nullable=False)
    store_rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="store")


class Product(Base):
    """
    SQLAlchemy model representing a product.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, nullable=False)
    subcategory = Column(String, index=True)
    brand = Column(String, index=True)
    unit_price = Column(Float, nullable=False)
    stock_on_hand = Column(Integer, default=0)

    # Relationships
    transactions = relationship("Transaction", back_populates="product")


class Transaction(Base):
    """
    SQLAlchemy model representing a sales transaction.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    store_id = Column(Integer, ForeignKey("stores.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # Pricing & Metrics
    discount_percentage = Column(Float, default=0.0)
    revenue = Column(Float, nullable=False)
    
    # Transaction Specifics
    customer_type = Column(String)  # e.g., 'New', 'Returning'
    payment_mode = Column(String)
    promotion_applied = Column(Boolean, default=False)
    holiday_flag = Column(Boolean, default=False)

    # Relationships
    store = relationship("Store", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")
