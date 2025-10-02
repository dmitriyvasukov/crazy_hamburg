from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    size: str
    quantity: int = Field(default=1, ge=1)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    price: float
    is_preorder: bool
    preorder_wave: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    delivery_address: Optional[str] = None
    cdek_point: Optional[str] = None
    promo_code: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    tracking_number: Optional[str] = None
    delivery_address: Optional[str] = None
    cdek_point: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    order_number: str
    total_amount: float
    discount_amount: float
    final_amount: float
    status: str
    payment_status: str
    tracking_number: Optional[str] = None
    delivery_address: Optional[str] = None
    cdek_point: Optional[str] = None
    payment_url: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int
