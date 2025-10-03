import requests
import json
import time
import random
import string
from typing import Dict
BASE_URL = "http://localhost:8000/api/v1"

class DWCTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.admin_token = None
        self.test_results = []
        
    def generate_random_string(self, length=8):
        """Генерация случайной строки для тестовых данных"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def print_result(self, endpoint: str, status_code: int, success: bool, details: str = ""):
        icon = "✅" if success else "❌"
        details_text = f" - {details}" if details else ""
        print(f"{icon} {endpoint}: {status_code}{details_text}")
        self.test_results.append((endpoint, status_code, success, details))
    
    def get_headers(self, token: str = None) -> Dict:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def test_auth(self):
        """Тестирование аутентификации"""
        print("🔐 Testing Authentication...")
        
        # Логин администратора
        login_data = {"phone": "+79999999999", "password": "admin123"}
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if resp.status_code == 200:
            self.admin_token = resp.json()["access_token"]
            self.user_id = resp.json()["user"]["id"]
            self.print_result("POST /auth/login", resp.status_code, True, "Admin login")
        else:
            self.print_result("POST /auth/login", resp.status_code, False, f"Error: {resp.text}")
            return False
        
        # Регистрация тестового пользователя с уникальным номером
        random_phone = f"+7999{random.randint(1000000, 9999999)}"
        register_data = {"phone": random_phone, "password": "test123"}
        resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if resp.status_code == 201:
            # ВАЖНО: Сохраняем токен пользователя!
            self.token = resp.json()["access_token"]
            self.print_result("POST /auth/register", resp.status_code, True, f"User: {random_phone}")
        else:
            # Если регистрация не удалась, логинимся как обычный пользователь
            user_login_data = {"phone": "+79998887766", "password": "test123"}
            resp = requests.post(f"{BASE_URL}/auth/login", json=user_login_data)
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                self.print_result("POST /auth/login (user)", resp.status_code, True, "Existing user login")
            else:
                self.print_result("POST /auth/register", resp.status_code, False, "Use existing test user")
        
        # ДОБАВЬ ОТЛАДОЧНУЮ ИНФОРМАЦИЮ
        print(f"   Admin token: {'✅' if self.admin_token else '❌'}")
        print(f"   User token: {'✅' if self.token else '❌'}")
        
        return True
    
    def test_users_endpoints(self):
        """Тестирование эндпоинтов пользователей"""
        print("\n👥 Testing Users Endpoints...")
        
        if not self.token:
            self.print_result("GET /users/me (user)", 0, False, "No user token")
            return
        
        # GET /users/me (user)
        resp = requests.get(f"{BASE_URL}/users/me", headers=self.get_headers(self.token))
        self.print_result("GET /users/me (user)", resp.status_code, resp.status_code == 200)
        
        # PUT /users/me (user)
        update_data = {"full_name": "Test User", "email": "test@example.com"}
        resp = requests.put(f"{BASE_URL}/users/me", json=update_data, headers=self.get_headers(self.token))
        self.print_result("PUT /users/me (user)", resp.status_code, resp.status_code == 200)
        
        # GET /users/ (admin)
        resp = requests.get(f"{BASE_URL}/users/", headers=self.get_headers(self.admin_token))
        self.print_result("GET /users/ (admin)", resp.status_code, resp.status_code == 200)
        
        # GET /users/{user_id} (admin)
        if self.user_id:
            resp = requests.get(f"{BASE_URL}/users/{self.user_id}", headers=self.get_headers(self.admin_token))
            self.print_result(f"GET /users/{self.user_id} (admin)", resp.status_code, resp.status_code == 200)
    
    def test_products_endpoints(self):
        """Тестирование эндпоинтов товаров"""
        print("\n🛍️ Testing Products Endpoints...")
        
        # GET /products/ (public)
        resp = requests.get(f"{BASE_URL}/products/")
        self.print_result("GET /products/ (public)", resp.status_code, resp.status_code == 200)
        
        # POST /products/ (admin) - с уникальным артикулом
        random_article = f"TEST{self.generate_random_string(6)}"
        product_data = {
            "name": f"Test Product {random_article}",
            "article": random_article,
            "price": 1000.0,
            "sizes": ["S", "M", "L"],
            "order_type": "order",
            "stock_count": 10
        }
        resp = requests.post(f"{BASE_URL}/products/", json=product_data, headers=self.get_headers(self.admin_token))
        product_id = resp.json().get("id") if resp.status_code == 201 else None
        self.print_result("POST /products/ (admin)", resp.status_code, resp.status_code == 201, f"Article: {random_article}")
        
        if product_id:
            # GET /products/{product_id} (public)
            resp = requests.get(f"{BASE_URL}/products/{product_id}")
            self.print_result(f"GET /products/{product_id} (public)", resp.status_code, resp.status_code == 200)
    
    def test_orders_endpoints(self):
        """Тестирование эндпоинтов заказов"""
        print("\n📦 Testing Orders Endpoints...")
        
        if not self.token:
            self.print_result("GET /orders/ (user)", 0, False, "No user token")
            return
            
        # GET /orders/ (user)
        resp = requests.get(f"{BASE_URL}/orders/", headers=self.get_headers(self.token))
        self.print_result("GET /orders/ (user)", resp.status_code, resp.status_code == 200)
        
        # GET /orders/admin/all (admin)
        resp = requests.get(f"{BASE_URL}/orders/admin/all", headers=self.get_headers(self.admin_token))
        self.print_result("GET /orders/admin/all (admin)", resp.status_code, resp.status_code == 200)
    
    def test_promo_codes_endpoints(self):
        """Тестирование эндпоинтов промокодов"""
        print("\n🎫 Testing Promo Codes Endpoints...")
        
        # POST /promo-codes/validate (public)
        validate_data = {"code": "TEST10", "product_ids": [1]}
        resp = requests.post(f"{BASE_URL}/promo-codes/validate", json=validate_data)
        self.print_result("POST /promo-codes/validate (public)", resp.status_code, resp.status_code == 200)
        
        # POST /promo-codes/ (admin) - с уникальным кодом
        random_code = f"TEST{self.generate_random_string(6)}"
        promo_data = {
            "code": random_code,
            "description": "Test promo code",
            "discount_percent": 10,
            "max_uses": 100
        }
        resp = requests.post(f"{BASE_URL}/promo-codes/", json=promo_data, headers=self.get_headers(self.admin_token))
        self.print_result("POST /promo-codes/ (admin)", resp.status_code, resp.status_code == 201, f"Code: {random_code}")
    
    def test_pages_endpoints(self):
        """Тестирование эндпоинтов страниц"""
        print("\n📄 Testing Pages Endpoints...")
        
        # GET /pages/ (public)
        resp = requests.get(f"{BASE_URL}/pages/")
        self.print_result("GET /pages/ (public)", resp.status_code, resp.status_code == 200)
        
        # POST /pages/ (admin) - с уникальным slug
        random_slug = f"test-page-{self.generate_random_string(6)}"
        page_data = {
            "slug": random_slug,
            "title": "Test Page",
            "content": "<p>Test content</p>"
        }
        resp = requests.post(f"{BASE_URL}/pages/", json=page_data, headers=self.get_headers(self.admin_token))
        self.print_result("POST /pages/ (admin)", resp.status_code, resp.status_code == 201, f"Slug: {random_slug}")
        
        # GET /pages/{slug} (public)
        resp = requests.get(f"{BASE_URL}/pages/{random_slug}")
        self.print_result(f"GET /pages/{random_slug} (public)", resp.status_code, resp.status_code == 200)
    
    def test_health_endpoints(self):
        """Тестирование health check эндпоинтов"""
        print("\n🏥 Testing Health Endpoints...")
        
        # GET /
        resp = requests.get(f"http://localhost:8000/")
        self.print_result("GET /", resp.status_code, resp.status_code == 200)
        
        # GET /health
        resp = requests.get(f"http://localhost:8000/health")
        self.print_result("GET /health", resp.status_code, resp.status_code == 200)
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Starting DWC API Comprehensive Tests")
        print("=" * 50)
        
        start_time = time.time()
        
        # Запускаем тесты по порядку
        tests = [
            self.test_auth,
            self.test_users_endpoints,
            self.test_products_endpoints,
            self.test_orders_endpoints,
            self.test_promo_codes_endpoints,
            self.test_pages_endpoints,
            self.test_health_endpoints,
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.3)  # Небольшая пауза между группами тестов
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Статистика
        end_time = time.time()
        total_time = end_time - start_time
        
        successful = sum(1 for _, _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success rate: {(successful/total)*100:.1f}%" if total > 0 else "0%")
        print(f"Total time: {total_time:.2f} seconds")
        
        # Показать неудачные тесты
        failed_tests = [(endpoint, status, details) for endpoint, status, success, details in self.test_results if not success]
        if failed_tests:
            print(f"\n❌ Failed tests:")
            for endpoint, status, details in failed_tests:
                print(f"   - {endpoint}: {status} {details}")

if __name__ == "__main__":
    tester = DWCTester()
    tester.run_all_tests()