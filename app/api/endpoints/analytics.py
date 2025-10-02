from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional
import csv
import io

from fastapi.responses import StreamingResponse

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("/sales")
async def get_sales_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Статистика продаж за период
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Total sales
    total_sales = db.query(func.sum(Order.final_amount)).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_status == PaymentStatus.SUCCEEDED
        )
    ).scalar() or 0
    
    # Orders count
    orders_count = db.query(func.count(Order.id)).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_status == PaymentStatus.SUCCEEDED
        )
    ).scalar() or 0
    
    # Average order value
    avg_order_value = total_sales / orders_count if orders_count > 0 else 0
    
    # Products sold
    products_sold = db.query(func.sum(OrderItem.quantity)).join(Order).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_status == PaymentStatus.SUCCEEDED
        )
    ).scalar() or 0
    
    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "total_sales": total_sales,
        "orders_count": orders_count,
        "average_order_value": avg_order_value,
        "products_sold": products_sold
    }


@router.get("/preorders")
async def get_preorders_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Статистика предзаказов за период
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Total preorders
    preorders_count = db.query(func.count(OrderItem.id)).join(Order).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            OrderItem.is_preorder == True
        )
    ).scalar() or 0
    
    # Preorders by wave
    preorders_by_wave = db.query(
        OrderItem.preorder_wave,
        func.count(OrderItem.id).label('count')
    ).join(Order).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            OrderItem.is_preorder == True
        )
    ).group_by(OrderItem.preorder_wave).all()
    
    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "total_preorders": preorders_count,
        "preorders_by_wave": [
            {"wave": wave, "count": count}
            for wave, count in preorders_by_wave
        ]
    }


@router.get("/customers")
async def get_customers_statistics(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Статистика клиентов
    """
    # Total customers
    total_customers = db.query(func.count(User.id)).filter(User.is_admin == False).scalar() or 0
    
    # Customers with orders
    customers_with_orders = db.query(func.count(func.distinct(Order.user_id))).scalar() or 0
    
    # Customers without orders
    customers_without_orders = total_customers - customers_with_orders
    
    return {
        "total_customers": total_customers,
        "customers_with_orders": customers_with_orders,
        "customers_without_orders": customers_without_orders,
        "conversion_rate": (customers_with_orders / total_customers * 100) if total_customers > 0 else 0
    }


@router.get("/promo-codes")
async def get_promo_codes_statistics(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Статистика использования промокодов
    """
    # Orders with promo codes
    orders_with_promo = db.query(func.count(Order.id)).filter(
        Order.promo_code_id.isnot(None)
    ).scalar() or 0
    
    # Orders without promo codes
    orders_without_promo = db.query(func.count(Order.id)).filter(
        Order.promo_code_id.is_(None)
    ).scalar() or 0
    
    # Total discount given
    total_discount = db.query(func.sum(Order.discount_amount)).scalar() or 0
    
    return {
        "orders_with_promo": orders_with_promo,
        "orders_without_promo": orders_without_promo,
        "total_discount_given": total_discount
    }


@router.get("/export/customers")
async def export_customers(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Экспорт списка клиентов в CSV
    """
    customers = db.query(User).filter(User.is_admin == False).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Телефон', 'ФИО', 'Email', 'Telegram', 'VK',
        'Адрес', 'Пункт СДЭК', 'Дата регистрации'
    ])
    
    # Data
    for customer in customers:
        writer.writerow([
            customer.id,
            customer.phone,
            customer.full_name or '',
            customer.email or '',
            customer.telegram or '',
            customer.vk or '',
            customer.address or '',
            customer.cdek_point or '',
            customer.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=customers_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/export/orders")
async def export_orders(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Экспорт заказов в CSV
    """
    query = db.query(Order)
    
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    
    orders = query.all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Номер заказа', 'Клиент', 'Сумма', 'Скидка', 'Итого',
        'Статус', 'Статус оплаты', 'Трек-номер', 'Дата создания', 'Дата оплаты'
    ])
    
    # Data
    for order in orders:
        writer.writerow([
            order.order_number,
            order.user.phone,
            order.total_amount,
            order.discount_amount,
            order.final_amount,
            order.status.value,
            order.payment_status.value,
            order.tracking_number or '',
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.paid_at.strftime('%Y-%m-%d %H:%M:%S') if order.paid_at else ''
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=orders_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )
