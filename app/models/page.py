from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.core.database import Base


class Page(Base):
    """Page model - технические страницы"""
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Page info
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Page {self.slug}>"
