"""
Comprehensive API tests
"""
import pytest


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_new_user(self, client):
        """Test user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "phone": "+79111111111",
                "password": "testpass123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["phone"] == "+79111111111"
        assert data["user"]["is_admin"] is False
    
    def test_register_duplicate_phone(self, client, regular_user):
        """Test registration with existing phone"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "phone": "+79001234567",
                "password": "testpass123"
            }
        )
        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"].lower()
    
    def test_register_invalid_phone(self, client):
        """Test registration with invalid phone"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "phone": "123",
                "password": "testpass123"
            }
        )
        assert response.status_code == 422
    
    def test_login_success(self, client, regular_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "phone": "+79001234567",
                "password": "user123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, regular_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "phone": "+79001234567",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "phone": "+79999999998",
                "password": "anypassword"
            }
        )
        assert response.status_code == 401


class TestUserEndpoints:
    """Test user endpoints"""
    
    def test_get_current_user(self, authenticated_client):
        """Test getting current user info"""
        response = authenticated_client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+79001234567"
        assert data["is_admin"] is False
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting user without token"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 403
    
    def test_update_user_profile(self, authenticated_client):
        """Test updating user profile"""
        response = authenticated_client.put(
            "/api/v1/users/me",
            json={
                "full_name": "Updated Name",
                "email": "test@example.com",
                "telegram": "@testuser"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["email"] == "test@example.com"
        assert data["telegram"] == "@testuser"
    
    def test_get_all_users_as_admin(self, admin_client, regular_user):
        """Test getting all users as admin"""
        response = admin_client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_all_users_as_regular_user(self, authenticated_client):
        """Test getting all users as regular user (should fail)"""
        response = authenticated_client.get("/api/v1/users/")
        assert response.status_code == 403


class TestProductEndpoints:
    """Test product endpoints"""
    
    def test_get_products_list(self, client, test_product):
        """Test getting products list"""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert len(data["products"]) >= 1
    
    def test_get_products_with_filters(self, client, test_product):
        """Test getting products with filters"""
        response = client.get("/api/v1/products/?is_active=true&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 5
    
    def test_get_single_product(self, client, test_product):
        """Test getting single product"""
        response = client.get(f"/api/v1/products/{test_product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == "Test T-Shirt"
    
    def test_get_nonexistent_product(self, client):
        """Test getting non-existent product"""
        response = client.get("/api/v1/products/9999")
        assert response.status_code == 404
    
    def test_create_product_as_admin(self, admin_client):
        """Test creating product as admin"""
        response = admin_client.post(
            "/api/v1/products/",
            json={
                "name": "New Product",
                "description": "New description",
                "article": "NEW-001",
                "price": 3500.0,
                "sizes": ["Oki"],
                "order_type": "order",
                "stock_count": 5,
                "media_urls": ["https://example.com/photo.jpg"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Product"
        assert data["article"] == "NEW-001"
    
    def test_create_product_as_user(self, authenticated_client):
        """Test creating product as regular user (should fail)"""
        response = authenticated_client.post(
            "/api/v1/products/",
            json={
                "name": "New Product",
                "article": "NEW-002",
                "price": 3500.0,
                "sizes": ["Oki"],
                "order_type": "order",
                "stock_count": 5,
                "media_urls": []
            }
        )
        assert response.status_code == 403
    
    def test_create_product_duplicate_article(self, admin_client, test_product):
        """Test creating product with duplicate article"""
        response = admin_client.post(
            "/api/v1/products/",
            json={
                "name": "Another Product",
                "article": "TEST-001",
                "price": 3500.0,
                "sizes": ["Oki"],
                "order_type": "order",
                "stock_count": 5,
                "media_urls": []
            }
        )
        assert response.status_code == 400
    
    def test_update_product(self, admin_client, test_product):
        """Test updating product"""
        response = admin_client.put(
            f"/api/v1/products/{test_product.id}",
            json={
                "price": 2800.0,
                "stock_count": 15
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 2800.0
        assert data["stock_count"] == 15
    
    def test_archive_product(self, admin_client, test_product):
        """Test archiving product"""
        response = admin_client.post(
            f"/api/v1/products/{test_product.id}/archive"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_archived"] is True
        assert data["is_active"] is False
    
    def test_delete_product(self, admin_client, test_product):
        """Test deleting product"""
        response = admin_client.delete(
            f"/api/v1/products/{test_product.id}"
        )
        assert response.status_code == 204


class TestOrderEndpoints:
    """Test order endpoints"""
    
    def test_create_order(self, authenticated_client, test_product):
        """Test creating order"""
        response = authenticated_client.post(
            "/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": test_product.id,
                        "size": "Oki",
                        "quantity": 2
                    }
                ],
                "delivery_address": "Moscow, Lenin St., 1"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "order_number" in data
        assert data["total_amount"] == 5000.0
        assert len(data["items"]) == 1
    
    def test_create_order_with_promo_code(self, authenticated_client, test_product, db_session):
        """Test creating order with promo code"""
        from app.models.promo_code import PromoCode
        
        # Create promo code
        promo = PromoCode(
            code="TEST10",
            discount_percent=10.0,
            is_active=True
        )
        db_session.add(promo)
        db_session.commit()
        
        response = authenticated_client.post(
            "/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": test_product.id,
                        "size": "Oki",
                        "quantity": 1
                    }
                ],
                "delivery_address": "Moscow, Lenin St., 1",
                "promo_code": "TEST10"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["discount_amount"] == 250.0
        assert data["final_amount"] == 2250.0
    
    def test_create_order_insufficient_stock(self, authenticated_client, test_product):
        """Test creating order with insufficient stock"""
        response = authenticated_client.post(
            "/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": test_product.id,
                        "size": "Oki",
                        "quantity": 100
                    }
                ],
                "delivery_address": "Moscow, Lenin St., 1"
            }
        )
        assert response.status_code == 400
        assert "недостаточно" in response.json()["detail"].lower()
    
    def test_get_user_orders(self, authenticated_client):
        """Test getting user's orders"""
        response = authenticated_client.get("/api/v1/orders/")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "total" in data
    
    def test_get_all_orders_as_admin(self, admin_client):
        """Test getting all orders as admin"""
        response = admin_client.get("/api/v1/orders/admin/all")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data


class TestPromoCodeEndpoints:
    """Test promo code endpoints"""
    
    def test_create_promo_code(self, admin_client):
        """Test creating promo code"""
        response = admin_client.post(
            "/api/v1/promo-codes/",
            json={
                "code": "NEWCODE",
                "description": "Test promo",
                "discount_percent": 15.0,
                "discount_amount": 0.0,
                "max_uses": 100
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "NEWCODE"
        assert data["discount_percent"] == 15.0
    
    def test_validate_promo_code(self, client, db_session):
        """Test validating promo code"""
        from app.models.promo_code import PromoCode
        
        # Create promo code
        promo = PromoCode(
            code="VALID10",
            discount_percent=10.0,
            is_active=True
        )
        db_session.add(promo)
        db_session.commit()
        
        response = client.post(
            "/api/v1/promo-codes/validate",
            json={
                "code": "VALID10",
                "product_ids": [1]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["discount_percent"] == 10.0
    
    def test_validate_invalid_promo_code(self, client):
        """Test validating invalid promo code"""
        response = client.post(
            "/api/v1/promo-codes/validate",
            json={
                "code": "INVALID",
                "product_ids": [1]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
    
    def test_get_all_promo_codes(self, admin_client):
        """Test getting all promo codes"""
        response = admin_client.get("/api/v1/promo-codes/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_delete_promo_code(self, admin_client, db_session):
        """Test deleting (deactivating) promo code"""
        from app.models.promo_code import PromoCode
        
        promo = PromoCode(code="DELETE", discount_percent=10.0, is_active=True)
        db_session.add(promo)
        db_session.commit()
        db_session.refresh(promo)
        
        response = admin_client.delete(
            f"/api/v1/promo-codes/{promo.id}"
        )
        assert response.status_code == 204


class TestPageEndpoints:
    """Test page endpoints"""
    
    def test_get_all_pages(self, client, test_page):
        """Test getting all pages"""
        response = client.get("/api/v1/pages/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_page_by_slug(self, client, test_page):
        """Test getting page by slug"""
        response = client.get(f"/api/v1/pages/{test_page.slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test"
        assert data["title"] == "Test Page"
    
    def test_get_nonexistent_page(self, client):
        """Test getting non-existent page"""
        response = client.get("/api/v1/pages/nonexistent")
        assert response.status_code == 404
    
    def test_create_page(self, admin_client):
        """Test creating page"""
        response = admin_client.post(
            "/api/v1/pages/",
            json={
                "slug": "new-page",
                "title": "New Page",
                "content": "<h1>New Content</h1>"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "new-page"
    
    def test_update_page(self, admin_client, test_page):
        """Test updating page"""
        response = admin_client.put(
            f"/api/v1/pages/{test_page.slug}",
            json={
                "title": "Updated Title",
                "content": "<h1>Updated</h1>"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    
    def test_delete_page(self, admin_client, test_page):
        """Test deleting page"""
        response = admin_client.delete(
            f"/api/v1/pages/{test_page.slug}"
        )
        assert response.status_code == 204


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    def test_get_sales_statistics(self, admin_client):
        """Test getting sales statistics"""
        response = admin_client.get("/api/v1/analytics/sales")
        assert response.status_code == 200
        data = response.json()
        assert "total_sales" in data
        assert "orders_count" in data
        assert "average_order_value" in data
    
    def test_get_preorders_statistics(self, admin_client):
        """Test getting preorders statistics"""
        response = admin_client.get("/api/v1/analytics/preorders")
        assert response.status_code == 200
        data = response.json()
        assert "total_preorders" in data
    
    def test_get_customers_statistics(self, admin_client):
        """Test getting customers statistics"""
        response = admin_client.get("/api/v1/analytics/customers")
        assert response.status_code == 200
        data = response.json()
        assert "total_customers" in data
        assert "customers_with_orders" in data
    
    def test_get_promo_codes_statistics(self, admin_client):
        """Test getting promo codes statistics"""
        response = admin_client.get("/api/v1/analytics/promo-codes")
        assert response.status_code == 200
        data = response.json()
        assert "orders_with_promo" in data
        assert "orders_without_promo" in data
    
    def test_analytics_as_regular_user(self, authenticated_client):
        """Test accessing analytics as regular user (should fail)"""
        response = authenticated_client.get("/api/v1/analytics/sales")
        assert response.status_code == 403


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
