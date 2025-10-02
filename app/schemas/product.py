from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductMediaBase(BaseModel):
    url: str
    order: int = 0


class ProductMediaResponse(ProductMediaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., description="Название товара")
    description: Optional[str] = Field(None, description="Описание")
    article: str = Field(..., description="Артикул")
    price: float = Field(..., gt=0, description="Цена")
    sizes: List[str] = Field(default_factory=list, description="Доступные размеры")
    size_table: Optional[Dict[str, Any]] = Field(None, description="Таблица размеров")
    care_instructions: Optional[str] = Field(None, description="Инструкции по уходу")


class ProductCreate(ProductBase):
    order_type: str = Field(default="order", description="Тип заказа: order, preorder, waiting")
    stock_count: int = Field(default=0, description="Количество на складе")
    preorder_waves_total: int = Field(default=0, description="Количество волн предзаказа")
    preorder_wave_capacity: int = Field(default=0, description="Вместимость волны")
    media_urls: List[str] = Field(default_factory=list, description="URL фотографий")


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    sizes: Optional[List[str]] = None
    size_table: Optional[Dict[str, Any]] = None
    care_instructions: Optional[str] = None
    order_type: Optional[str] = None
    stock_count: Optional[int] = None
    preorder_waves_total: Optional[int] = None
    preorder_wave_capacity: Optional[int] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    order_type: str
    stock_count: int
    preorder_waves_total: int
    preorder_wave_capacity: int
    current_wave: int
    current_wave_count: int
    is_active: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    media: List[ProductMediaResponse] = []
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int
