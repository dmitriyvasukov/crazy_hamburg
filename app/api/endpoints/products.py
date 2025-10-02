from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.product import Product, ProductMedia, OrderType
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    is_archived: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """
    Получить список товаров
    """
    query = db.query(Product)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    if is_archived is not None:
        query = query.filter(Product.is_archived == is_archived)
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return ProductListResponse(
        products=products,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Получить товар по ID
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Создать новый товар (только для администраторов)
    """
    # Check if article already exists
    existing = db.query(Product).filter(Product.article == product_data.article).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Товар с таким артикулом уже существует"
        )
    
    # Create product
    product = Product(
        name=product_data.name,
        description=product_data.description,
        article=product_data.article,
        price=product_data.price,
        sizes=product_data.sizes,
        size_table=product_data.size_table,
        care_instructions=product_data.care_instructions,
        order_type=OrderType(product_data.order_type),
        stock_count=product_data.stock_count,
        preorder_waves_total=product_data.preorder_waves_total,
        preorder_wave_capacity=product_data.preorder_wave_capacity
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Add media
    for idx, url in enumerate(product_data.media_urls):
        media = ProductMedia(product_id=product.id, url=url, order=idx)
        db.add(media)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Обновить товар (только для администраторов)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "order_type" and value:
            value = OrderType(value)
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Удалить товар (только для администраторов)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    db.delete(product)
    db.commit()
    
    return None


@router.post("/{product_id}/archive", response_model=ProductResponse)
async def archive_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Архивировать товар (только для администраторов)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    product.is_archived = True
    product.is_active = False
    
    db.commit()
    db.refresh(product)
    
    return product
