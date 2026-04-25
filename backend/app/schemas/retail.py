from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StoreBase(BaseModel):
    store_location: str
    store_rating: float = Field(..., ge=0.0, le=5.0)

class StoreCreate(StoreBase):
    pass

class StoreResponse(StoreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    unit_price: float = Field(..., gt=0.0)
    stock_on_hand: int = Field(0, ge=0)

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    store_id: int
    product_id: int
    discount_percentage: float = Field(0.0, ge=0.0, le=100.0)
    revenue: float = Field(..., ge=0.0)
    customer_type: str
    payment_mode: str
    promotion_applied: bool = False
    holiday_flag: bool = False

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
