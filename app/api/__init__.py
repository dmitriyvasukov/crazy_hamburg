from fastapi import APIRouter
from app.api.endpoints import auth, users, products, orders, promo_codes, pages, analytics, payment

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(promo_codes.router, prefix="/promo-codes", tags=["Promo Codes"])
api_router.include_router(pages.router, prefix="/pages", tags=["Pages"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(payment.router, prefix="/payment", tags=["Payment"])
