# API Usage Examples

Примеры использования API интернет-магазина DWC.

## Базовая информация

**Base URL:** `http://localhost:8000/api/v1`

**Аутентификация:** Bearer Token в заголовке `Authorization`

---

## 1. Регистрация и вход

### Регистрация нового пользователя

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+79001234567",
    "password": "mypassword123"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "phone": "+79001234567",
    "full_name": null,
    "email": null,
    "is_admin": false,
    "is_active": true,
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### Вход

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+79001234567",
    "password": "mypassword123"
  }'
```

---

## 2. Работа с профилем

### Получить информацию о себе

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Обновить профиль

```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иван Петров",
    "email": "ivan@example.com",
    "address": "Москва, ул. Ленина, д. 1, кв. 10",
    "telegram": "@ivanpetrov",
    "vk": "ivanpetrov"
  }'
```

---

## 3. Товары

### Получить список товаров

```bash
# Все активные товары
curl -X GET "http://localhost:8000/api/v1/products/?is_active=true&limit=10"

# С пагинацией
curl -X GET "http://localhost:8000/api/v1/products/?skip=0&limit=5"
```

**Ответ:**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Футболка DWC Classic",
      "description": "Классическая дизайнерская футболка",
      "article": "DWC-TS-001",
      "price": 2500.0,
      "sizes": ["Oki", "Big"],
      "order_type": "order",
      "stock_count": 15,
      "is_active": true,
      "is_archived": false,
      "media": [
        {
          "id": 1,
          "url": "https://example.com/photo1.jpg",
          "order": 0
        }
      ]
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 10
}
```

### Получить товар по ID

```bash
curl -X GET "http://localhost:8000/api/v1/products/1"
```

### Создать товар (только админ)

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Худи DWC Limited",
    "description": "Лимитированное худи из премиум коллекции",
    "article": "DWC-HD-002",
    "price": 5500.0,
    "sizes": ["Oki", "Big"],
    "size_table": {
      "Oki": {"chest": "100-105", "length": "70"},
      "Big": {"chest": "110-115", "length": "75"}
    },
    "care_instructions": "Стирка при 30°C, не отбеливать",
    "order_type": "preorder",
    "stock_count": 0,
    "preorder_waves_total": 3,
    "preorder_wave_capacity": 10,
    "media_urls": [
      "https://example.com/hoodie1.jpg",
      "https://example.com/hoodie2.jpg"
    ]
  }'
```

### Обновить товар (только админ)

```bash
curl -X PUT "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 2700.0,
    "stock_count": 20
  }'
```

### Архивировать товар (только админ)

```bash
curl -X POST "http://localhost:8000/api/v1/products/1/archive" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 4. Промокоды

### Проверить промокод

```bash
curl -X POST "http://localhost:8000/api/v1/promo-codes/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SALE10",
    "product_ids": [1, 2]
  }'
```

**Ответ:**
```json
{
  "is_valid": true,
  "message": "Промокод действителен",
  "discount_percent": 10.0,
  "discount_amount": 0.0
}
```

### Создать промокод (только админ)

```bash
curl -X POST "http://localhost:8000/api/v1/promo-codes/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "NEWYEAR2024",
    "description": "Новогодняя скидка 15%",
    "discount_percent": 15.0,
    "discount_amount": 0.0,
    "product_ids": [1, 2, 3],
    "max_uses": 100,
    "valid_from": "2024-01-01T00:00:00",
    "valid_until": "2024-01-31T23:59:59"
  }'
```

### Получить все промокоды (только админ)

```bash
curl -X GET "http://localhost:8000/api/v1/promo-codes/" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 5. Заказы

### Создать заказ

```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "size": "Oki",
        "quantity": 2
      },
      {
        "product_id": 2,
        "size": "Big",
        "quantity": 1
      }
    ],
    "delivery_address": "Москва, ул. Ленина, д. 1, кв. 10",
    "promo_code": "SALE10"
  }'
```

**Ответ:**
```json
{
  "id": 1,
  "order_number": "DWC-20240115-A1B2C3D4",
  "total_amount": 7500.0,
  "discount_amount": 750.0,
  "final_amount": 6750.0,
  "status": "pending",
  "payment_status": "pending",
  "delivery_address": "Москва, ул. Ленина, д. 1, кв. 10",
  "created_at": "2024-01-15T10:30:00",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "size": "Oki",
      "quantity": 2,
      "price": 2500.0,
      "is_preorder": false
    }
  ]
}
```

### Получить свои заказы

```bash
curl -X GET "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Получить заказ по ID

```bash
curl -X GET "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Получить все заказы (только админ)

```bash
curl -X GET "http://localhost:8000/api/v1/orders/admin/all?skip=0&limit=20" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Обновить заказ (только админ)

```bash
curl -X PUT "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "shipped",
    "tracking_number": "1234567890"
  }'
```

---

## 6. Оплата

### Создать платёж для заказа

```bash
curl -X POST "http://localhost:8000/api/v1/payment/create/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Ответ:**
```json
{
  "payment_id": "2a8e9b75-000f-5000-8000-1234567890ab",
  "confirmation_url": "https://yoomoney.ru/checkout/payments/v2/...",
  "order_number": "DWC-20240115-A1B2C3D4"
}
```

### Проверить статус платежа

```bash
curl -X GET "http://localhost:8000/api/v1/payment/status/2a8e9b75-000f-5000-8000-1234567890ab" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Отменить платёж

```bash
curl -X POST "http://localhost:8000/api/v1/payment/cancel/2a8e9b75-000f-5000-8000-1234567890ab" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 7. Страницы

### Получить страницу

```bash
# FAQ
curl -X GET "http://localhost:8000/api/v1/pages/faq"

# О проекте
curl -X GET "http://localhost:8000/api/v1/pages/about"
```

### Обновить страницу (только админ)

```bash
curl -X PUT "http://localhost:8000/api/v1/pages/faq" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FAQ - Обновлённые вопросы",
    "content": "<h1>FAQ</h1><p>Новый контент FAQ...</p>"
  }'
```

---

## 8. Аналитика (только админ)

### Статистика продаж

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/sales?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Ответ:**
```json
{
  "period": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-01-31T23:59:59"
  },
  "total_sales": 125000.0,
  "orders_count": 45,
  "average_order_value": 2777.78,
  "products_sold": 89
}
```

### Статистика предзаказов

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/preorders" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Статистика клиентов

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/customers" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Экспорт клиентов в CSV

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/export/customers" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -o customers.csv
```

### Экспорт заказов в CSV

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/export/orders?start_date=2024-01-01T00:00:00" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -o orders.csv
```

---

## Python примеры

### Использование с requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Регистрация
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "phone": "+79001234567",
        "password": "mypassword123"
    }
)
data = response.json()
token = data["access_token"]

# Использование токена
headers = {"Authorization": f"Bearer {token}"}

# Получить товары
products = requests.get(f"{BASE_URL}/products/", headers=headers).json()

# Создать заказ
order = requests.post(
    f"{BASE_URL}/orders/",
    headers=headers,
    json={
        "items": [
            {"product_id": 1, "size": "Oki", "quantity": 1}
        ],
        "delivery_address": "Москва, ул. Ленина, 1"
    }
).json()

print(f"Заказ создан: {order['order_number']}")
```

---

## JavaScript/Fetch примеры

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Регистрация
async function register() {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      phone: '+79001234567',
      password: 'mypassword123',
    }),
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
}

// Получить товары
async function getProducts() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${BASE_URL}/products/`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return await response.json();
}

// Создать заказ
async function createOrder(items, address) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${BASE_URL}/orders/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      items: items,
      delivery_address: address,
    }),
  });
  
  return await response.json();
}
```

---

## Типичные сценарии

### Сценарий 1: Покупка товара клиентом

1. Регистрация/Вход
2. Просмотр товаров
3. Добавление в корзину (на frontend)
4. Создание заказа
5. Создание платежа
6. Переход на страницу оплаты
7. Проверка статуса платежа

### Сценарий 2: Управление товарами админом

1. Вход как админ
2. Создание нового товара
3. Загрузка фото товара
4. Установка параметров предзаказа
5. Активация товара
6. Мониторинг заказов
7. Обновление статусов

### Сценарий 3: Предзаказ

1. Клиент заказывает товар с type="preorder"
2. Система добавляет его в текущую волну
3. Когда волна заполняется, открывается следующая
4. Админ управляет статусами волн
5. Клиенты видят обновления в личном кабинете
