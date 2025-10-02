from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PromoCodeBase(BaseModel):
    code: str = Field(..., description="Код промокода")
    description: Optional[str] = Field(None, description="Описание")
    discount_percent: float = Field(default=0, ge=0, le=100, description="Процент скидки")
    discount_amount: float = Field(default=0, ge=0, description="Фиксированная скидка")


class PromoCodeCreate(PromoCodeBase):
    product_ids: List[int] = Field(default_factory=list, description="ID товаров для промокода")
    max_uses: Optional[int] = Field(None, ge=1, description="Максимальное количество использований")
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class PromoCodeUpdate(BaseModel):
    description: Optional[str] = None
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    product_ids: Optional[List[int]] = None
    max_uses: Optional[int] = Field(None, ge=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class PromoCodeResponse(PromoCodeBase):
    id: int
    max_uses: Optional[int] = None
    current_uses: int
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PromoCodeValidation(BaseModel):
    is_valid: bool
    message: str
    discount_percent: float = 0
    discount_amount: float = 0
