from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class OrderType(str, enum.Enum):
    """Тип заказа товара"""
    ORDER = "order"  # Обычный заказ со склада
    PREORDER = "preorder"  # Предзаказ
    WAITING = "waiting"  # Ожидание (все волны закончились)


class SizeType(str, enum.Enum):
    """Типы размеров"""
    OKI = "Oki"
    BIG = "Big"


class Product(Base):
    """Product model - товары"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    article = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    
    # Size and care
    sizes = Column(JSON, nullable=False, default=list)  # ["Oki", "Big"]
    size_table = Column(JSON, nullable=True)  # Таблица размеров
    care_instructions = Column(Text, nullable=True)
    
    # Order type and stock
    order_type = Column(Enum(OrderType), default=OrderType.ORDER, nullable=False)
    stock_count = Column(Integer, default=0)  # Для обычных заказов
    
    # Preorder settings
    preorder_waves_total = Column(Integer, default=0)  # Общее количество волн
    preorder_wave_capacity = Column(Integer, default=0)  # Вместимость одной волны
    current_wave = Column(Integer, default=1)  # Текущая волна
    current_wave_count = Column(Integer, default=0)  # Заполненность текущей волны
    
    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    media = relationship("ProductMedia", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    promo_codes = relationship("PromoCode", secondary="promo_code_products", back_populates="products")

    def __repr__(self):
        return f"<Product {self.article}: {self.name}>"


class ProductMedia(Base):
    """Product media - фото товаров"""
    __tablename__ = "product_media"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Media info
    url = Column(String(500), nullable=False)
    order = Column(Integer, default=0)  # Порядок в карусели
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="media")

    def __repr__(self):
        return f"<ProductMedia {self.id} for Product {self.product_id}>"
