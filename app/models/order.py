from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """Статусы заказов"""
    PENDING = "pending"  # Ожидает оплаты
    PAID = "paid"  # Оплачен
    PROCESSING = "processing"  # В обработке
    SHIPPED = "shipped"  # Отправлен
    DELIVERED = "delivered"  # Доставлен
    CANCELLED = "cancelled"  # Отменён


class PaymentStatus(str, enum.Enum):
    """Статусы оплаты"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Order(Base):
    """Order model - заказы"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order details
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Delivery
    tracking_number = Column(String(255), nullable=True)
    delivery_address = Column(Text, nullable=True)
    cdek_point = Column(String(255), nullable=True)
    
    # Payment
    payment_id = Column(String(255), nullable=True)  # ЮKassa payment ID
    payment_url = Column(String(500), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    
    # Promo code
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    promo_code = relationship("PromoCode")

    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    """Order item - позиции в заказе"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details
    size = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)
    
    # Preorder info
    is_preorder = Column(Boolean, default=False)
    preorder_wave = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem {self.id} in Order {self.order_id}>"
