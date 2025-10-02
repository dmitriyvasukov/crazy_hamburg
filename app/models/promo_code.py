from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Table, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

# Association table for many-to-many relationship
promo_code_products = Table(
    'promo_code_products',
    Base.metadata,
    Column('promo_code_id', Integer, ForeignKey('promo_codes.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True)
)


class PromoCode(Base):
    """Promo code model - промокоды"""
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Code info
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Discount
    discount_percent = Column(Float, nullable=False, default=0)  # Процент скидки
    discount_amount = Column(Float, nullable=False, default=0)  # Фиксированная скидка
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # Максимальное количество использований (None = безлимитно)
    current_uses = Column(Integer, default=0)
    
    # Validity
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", secondary=promo_code_products, back_populates="promo_codes")

    def __repr__(self):
        return f"<PromoCode {self.code}>"

    def is_valid(self) -> bool:
        """Check if promo code is currently valid"""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True
