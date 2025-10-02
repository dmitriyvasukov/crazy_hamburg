from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.page import Page
from app.schemas.page import PageCreate, PageUpdate, PageResponse

router = APIRouter()


@router.get("/", response_model=list[PageResponse])
async def get_pages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить все страницы
    """
    pages = db.query(Page).offset(skip).limit(limit).all()
    return pages


@router.get("/{slug}", response_model=PageResponse)
async def get_page_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Получить страницу по slug
    """
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    return page


@router.post("/", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_page(
    page_data: PageCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Создать страницу (только для администраторов)
    """
    # Check if slug already exists
    existing = db.query(Page).filter(Page.slug == page_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Страница с таким slug уже существует"
        )
    
    page = Page(**page_data.dict())
    db.add(page)
    db.commit()
    db.refresh(page)
    
    return page


@router.put("/{slug}", response_model=PageResponse)
async def update_page(
    slug: str,
    page_data: PageUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Обновить страницу (только для администраторов)
    """
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    
    # Update fields
    update_data = page_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(page, field, value)
    
    db.commit()
    db.refresh(page)
    
    return page


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    slug: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Удалить страницу (только для администраторов)
    """
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    
    db.delete(page)
    db.commit()
    
    return None
