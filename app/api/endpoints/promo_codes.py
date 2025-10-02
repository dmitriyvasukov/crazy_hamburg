from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.promo_code import PromoCode
from app.models.product import Product
from app.schemas.promo_code import PromoCodeCreate, PromoCodeUpdate, PromoCodeResponse, PromoCodeValidation

router = APIRouter()


@router.get("/", response_model=list[PromoCodeResponse])
async def get_promo_codes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Получить все промокоды (только для администраторов)
    """
    promo_codes = db.query(PromoCode).offset(skip).limit(limit).all()
    return promo_codes


@router.get("/{promo_code_id}", response_model=PromoCodeResponse)
async def get_promo_code(
    promo_code_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Получить промокод по ID (только для администраторов)
    """
    promo_code = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()
    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Промокод не найден"
        )
    return promo_code


class PromoCodeValidateRequest(BaseModel):
    code: str
    product_ids: List[int]

@router.post("/validate", response_model=PromoCodeValidation)
async def validate_promo_code(
    request: PromoCodeValidateRequest,
    db: Session = Depends(get_db)
):
    """
    Проверить валидность промокода
    """
    code = request.code
    product_ids = request.product_ids
    promo_code = db.query(PromoCode).filter(PromoCode.code == code).first()
    
    if not promo_code:
        return PromoCodeValidation(
            is_valid=False,
            message="Промокод не найден"
        )
    
    if not promo_code.is_valid():
        return PromoCodeValidation(
            is_valid=False,
            message="Промокод недействителен или истёк срок действия"
        )
    
    # Check if promo code applies to products
    if promo_code.products:
        promo_product_ids = [p.id for p in promo_code.products]
        if not any(pid in promo_product_ids for pid in product_ids):
            return PromoCodeValidation(
                is_valid=False,
                message="Промокод не применим к выбранным товарам"
            )
    
    return PromoCodeValidation(
        is_valid=True,
        message="Промокод действителен",
        discount_percent=promo_code.discount_percent,
        discount_amount=promo_code.discount_amount
    )


@router.post("/", response_model=PromoCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_promo_code(
    promo_data: PromoCodeCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Создать промокод (только для администраторов)
    """
    # Check if code already exists
    existing = db.query(PromoCode).filter(PromoCode.code == promo_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Промокод с таким кодом уже существует"
        )
    
    # Create promo code
    promo_code = PromoCode(
        code=promo_data.code,
        description=promo_data.description,
        discount_percent=promo_data.discount_percent,
        discount_amount=promo_data.discount_amount,
        max_uses=promo_data.max_uses,
        valid_from=promo_data.valid_from,
        valid_until=promo_data.valid_until
    )
    
    # Add products
    if promo_data.product_ids:
        products = db.query(Product).filter(Product.id.in_(promo_data.product_ids)).all()
        promo_code.products = products
    
    db.add(promo_code)
    db.commit()
    db.refresh(promo_code)
    
    return promo_code


@router.put("/{promo_code_id}", response_model=PromoCodeResponse)
async def update_promo_code(
    promo_code_id: int,
    promo_data: PromoCodeUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Обновить промокод (только для администраторов)
    """
    promo_code = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()
    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Промокод не найден"
        )
    
    # Update fields
    update_data = promo_data.dict(exclude_unset=True)
    
    # Handle product_ids separately
    if "product_ids" in update_data:
        product_ids = update_data.pop("product_ids")
        if product_ids is not None:
            products = db.query(Product).filter(Product.id.in_(product_ids)).all()
            promo_code.products = products
    
    for field, value in update_data.items():
        setattr(promo_code, field, value)
    
    db.commit()
    db.refresh(promo_code)
    
    return promo_code


@router.delete("/{promo_code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promo_code(
    promo_code_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Удалить промокод (только для администраторов)
    """
    promo_code = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()
    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Промокод не найден"
        )
    
    # Soft delete - deactivate instead of deleting
    promo_code.is_active = False
    
    db.commit()
    
    return None
