from pydantic import BaseModel, Field
from datetime import datetime


class PageBase(BaseModel):
    slug: str = Field(..., description="URL-идентификатор страницы")
    title: str = Field(..., description="Заголовок")
    content: str = Field(..., description="Содержимое HTML")


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    title: str = None
    content: str = None


class PageResponse(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
