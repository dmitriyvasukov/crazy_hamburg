from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.order import Order, PaymentStatus, OrderStatus
from app.services.payment import payment_service

router = APIRouter()


@router.post("/create/{order_id}")
async def create_payment(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать платёж для заказа
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Check if user owns this order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )
    
    # Check if already paid
    if order.payment_status == PaymentStatus.SUCCEEDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ уже оплачен"
        )
    
    try:
        # Create payment via YooKassa
        payment_data = payment_service.create_payment(order)
        
        # Update order with payment info
        order.payment_id = payment_data["payment_id"]
        order.payment_url = payment_data["confirmation_url"]
        
        db.commit()
        db.refresh(order)
        
        return {
            "payment_id": payment_data["payment_id"],
            "confirmation_url": payment_data["confirmation_url"],
            "order_number": order.order_number
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания платежа: {str(e)}"
        )


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить статус платежа
    """
    order = db.query(Order).filter(Order.payment_id == payment_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден"
        )
    
    # Check if user owns this order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )
    
    try:
        payment_info = payment_service.get_payment(payment_id)
        
        if payment_info and payment_info["paid"]:
            # Update order status
            if order.payment_status != PaymentStatus.SUCCEEDED:
                order.payment_status = PaymentStatus.SUCCEEDED
                order.status = OrderStatus.PAID
                order.paid_at = datetime.utcnow()
                db.commit()
        
        return payment_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статуса: {str(e)}"
        )


@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook для получения уведомлений от ЮKassa
    """
    try:
        body = await request.json()
        
        # Process webhook
        webhook_data = payment_service.process_webhook(body)
        
        # Find order
        payment_id = webhook_data["payment_id"]
        order = db.query(Order).filter(Order.payment_id == payment_id).first()
        
        if not order:
            return {"status": "ok"}
        
        # Update order status based on payment status
        if webhook_data["paid"] and webhook_data["status"] == "succeeded":
            order.payment_status = PaymentStatus.SUCCEEDED
            order.status = OrderStatus.PAID
            order.paid_at = datetime.utcnow()
        elif webhook_data["status"] == "canceled":
            order.payment_status = PaymentStatus.CANCELLED
            order.status = OrderStatus.CANCELLED
        
        db.commit()
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.post("/cancel/{payment_id}")
async def cancel_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отменить платёж
    """
    order = db.query(Order).filter(Order.payment_id == payment_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден"
        )
    
    # Check if user owns this order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )
    
    try:
        success = payment_service.cancel_payment(payment_id)
        
        if success:
            order.payment_status = PaymentStatus.CANCELLED
            order.status = OrderStatus.CANCELLED
            db.commit()
            
            return {"status": "cancelled"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось отменить платёж"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отмены платежа: {str(e)}"
        )
