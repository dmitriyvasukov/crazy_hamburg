from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.product import Product, OrderType
from app.models.promo_code import PromoCode
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse

router = APIRouter()


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить заказы текущего пользователя
    """
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return OrderListResponse(
        orders=orders,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить заказ по ID
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Check if user owns this order or is admin
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )
    
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый заказ
    """
    # Calculate total
    total_amount = 0
    order_items_data = []
    
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с ID {item_data.product_id} не найден"
            )
        
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Товар {product.name} недоступен для заказа"
            )
        
        # Check availability
        if product.order_type == OrderType.WAITING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Товар {product.name} в режиме ожидания"
            )
        
        is_preorder = product.order_type == OrderType.PREORDER
        preorder_wave = None
        
        if is_preorder:
            # Check preorder availability
            if product.current_wave > product.preorder_waves_total:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Все волны предзаказа для {product.name} заполнены"
                )
            preorder_wave = product.current_wave
        else:
            # Check stock
            if product.stock_count < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно товара {product.name} на складе"
                )
        
        item_total = product.price * item_data.quantity
        total_amount += item_total
        
        order_items_data.append({
            "product": product,
            "size": item_data.size,
            "quantity": item_data.quantity,
            "price": product.price,
            "is_preorder": is_preorder,
            "preorder_wave": preorder_wave
        })
    
    # Apply promo code
    discount_amount = 0
    promo_code = None
    
    if order_data.promo_code:
        promo_code = db.query(PromoCode).filter(
            PromoCode.code == order_data.promo_code
        ).first()
        
        if promo_code and promo_code.is_valid():
            if promo_code.discount_percent > 0:
                discount_amount = total_amount * (promo_code.discount_percent / 100)
            elif promo_code.discount_amount > 0:
                discount_amount = min(promo_code.discount_amount, total_amount)
    
    final_amount = total_amount - discount_amount
    
    # Generate order number
    order_number = f"DWC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Create order
    order = Order(
        user_id=current_user.id,
        order_number=order_number,
        total_amount=total_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
        delivery_address=order_data.delivery_address,
        cdek_point=order_data.cdek_point,
        promo_code_id=promo_code.id if promo_code else None
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            size=item_data["size"],
            quantity=item_data["quantity"],
            price=item_data["price"],
            is_preorder=item_data["is_preorder"],
            preorder_wave=item_data["preorder_wave"]
        )
        db.add(order_item)
        
        # Update stock or preorder count
        product = item_data["product"]
        if item_data["is_preorder"]:
            product.current_wave_count += item_data["quantity"]
            
            # Check if wave is full
            if product.current_wave_count >= product.preorder_wave_capacity:
                product.current_wave += 1
                product.current_wave_count = 0
                
                # Check if all waves are done
                if product.current_wave > product.preorder_waves_total:
                    product.order_type = OrderType.WAITING
        else:
            product.stock_count -= item_data["quantity"]
    
    # Update promo code usage
    if promo_code:
        promo_code.current_uses += 1
    
    db.commit()
    db.refresh(order)
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Обновить заказ (только для администраторов)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Update fields
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status":
            value = OrderStatus(value)
            if value == OrderStatus.SHIPPED:
                order.shipped_at = datetime.utcnow()
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/admin/all", response_model=OrderListResponse)
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Получить все заказы (только для администраторов)
    """
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return OrderListResponse(
        orders=orders,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )
