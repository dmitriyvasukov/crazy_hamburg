# API Documentation

## Базовый URL
```
http://localhost:8000/api/v1
```

## Аутентификация

API использует JWT токены для аутентификации. После успешного входа/регистрации вы получаете токен, который нужно передавать в заголовке:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## Endpoints

### Authentication

#### POST /auth/register
Регистрация нового пользователя

**Request:**
```json
{
  "phone": "+79991234567",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "phone": "+79991234567",
    "is_admin": false,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### POST /auth/login
Вход пользователя

**Request:**
```json
{
  "phone": "+79991234567",
  "password": "password123"
}
```

**Response:** То же, что и при регистрации

---

### Users

#### GET /users/me
Получить информацию о текущем пользователе (требует аутентификации)

**Response:**
```json
{
  "id": 1,
  "phone": "+79991234567",
  "full_name": "Иван Иванов",
  "email": "ivan@example.com",
  "address": "Москва, ул. Ленина, 1",
  "cdek_point": "MSK123",
  "telegram": "@ivanov",
  "vk": "ivanov",
  "is_admin": false,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### PUT /users/me
Обновить профиль (требует аутентификации)

**Request:**
```json
{
  "full_name": "Иван Петров",
  "email": "new@example.com",
  "telegram": "@newusername"
}
```

#### GET /users/
Получить всех пользователей (только админ)

---

### Products

#### GET /products/
Получить список товаров

**Query params:**
- `skip`: int (default: 0)
- `limit`: int (default: 10)
- `is_active`: bool
- `is_archived`: bool

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Футболка DWC",
      "description": "Дизайнерская футболка",
      "article": "DWC-TS-001",
      "price": 2500.0,
      "sizes": ["Oki", "Big"],
      "size_table": {...},
      "care_instructions": "Стирка при 30°C",
      "order_type": "order",
      "stock_count": 10,
      "preorder_waves_total": 0,
      "preorder_wave_capacity": 0,
      "current_wave": 1,
      "current_wave_count": 0,
      "is_active": true,
      "is_archived": false,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00",
      "media": [
        {
          "id": 1,
          "url": "https://example.com/photo.jpg",
          "order": 0,
          "created_at": "2024-01-01T00:00:00"
        }
      ]
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 10
}
```

#### GET /products/{product_id}
Получить товар по ID

#### POST /products/
Создать товар (только админ)

**Request:**
```json
{
  "name": "Футболка DWC",
  "description": "Дизайнерская футболка",
  "article": "DWC-TS-001",
  "price": 2500.0,
  "sizes": ["Oki", "Big"],
  "size_table": {...},
  "care_instructions": "Стирка при 30°C",
  "order_type": "order",
  "stock_count": 10,
  "media_urls": ["https://example.com/photo1.jpg"]
}
```

#### PUT /products/{product_id}
Обновить товар (только админ)

#### DELETE /products/{product_id}
Удалить товар (только админ)

#### POST /products/{product_id}/archive
Архивировать товар (только админ)

---

### Orders

#### GET /orders/
Получить заказы текущего пользователя

**Response:**
```json
{
  "orders": [
    {
      "id": 1,
      "order_number": "DWC-20240101-A1B2C3D4",
      "total_amount": 5000.0,
      "discount_amount": 500.0,
      "final_amount": 4500.0,
      "status": "paid",
      "payment_status": "succeeded",
      "tracking_number": "123456789",
      "delivery_address": "Москва, ул. Ленина, 1",
      "cdek_point": null,
      "payment_url": null,
      "receipt_url": "https://...",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00",
      "paid_at": "2024-01-01T01:00:00",
      "shipped_at": null,
      "items": [
        {
          "id": 1,
          "product_id": 1,
          "size": "Oki",
          "quantity": 2,
          "price": 2500.0,
          "is_preorder": false,
          "preorder_wave": null,
          "created_at": "2024-01-01T00:00:00"
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

#### GET /orders/{order_id}
Получить заказ по ID

#### POST /orders/
Создать заказ

**Request:**
```json
{
  "items": [
    {
      "product_id": 1,
      "size": "Oki",
      "quantity": 2
    }
  ],
  "delivery_address": "Москва, ул. Ленина, 1",
  "cdek_point": null,
  "promo_code": "SALE10"
}
```

#### PUT /orders/{order_id}
Обновить заказ (только админ)

#### GET /orders/admin/all
Получить все заказы (только админ)

---

### Promo Codes

#### GET /promo-codes/
Получить все промокоды (только админ)

#### GET /promo-codes/{promo_code_id}
Получить промокод по ID (только админ)

#### POST /promo-codes/validate
Проверить валидность промокода

**Request:**
```json
{
  "code": "SALE10",
  "product_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "is_valid": true,
  "message": "Промокод действителен",
  "discount_percent": 10.0,
  "discount_amount": 0.0
}
```

#### POST /promo-codes/
Создать промокод (только админ)

**Request:**
```json
{
  "code": "SALE10",
  "description": "Скидка 10%",
  "discount_percent": 10.0,
  "discount_amount": 0.0,
  "product_ids": [1, 2],
  "max_uses": 100,
  "valid_from": "2024-01-01T00:00:00",
  "valid_until": "2024-12-31T23:59:59"
}
```

#### PUT /promo-codes/{promo_code_id}
Обновить промокод (только админ)

#### DELETE /promo-codes/{promo_code_id}
Удалить (деактивировать) промокод (только админ)

---

### Pages

#### GET /pages/
Получить все страницы

#### GET /pages/{slug}
Получить страницу по slug

#### POST /pages/
Создать страницу (только админ)

#### PUT /pages/{slug}
Обновить страницу (только админ)

#### DELETE /pages/{slug}
Удалить страницу (только админ)

---

### Analytics

#### GET /analytics/sales
Статистика продаж за период (только админ)

**Query params:**
- `start_date`: datetime
- `end_date`: datetime

**Response:**
```json
{
  "period": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-01-31T23:59:59"
  },
  "total_sales": 150000.0,
  "orders_count": 50,
  "average_order_value": 3000.0,
  "products_sold": 120
}
```

#### GET /analytics/preorders
Статистика предзаказов (только админ)

#### GET /analytics/customers
Статистика клиентов (только админ)

#### GET /analytics/promo-codes
Статистика промокодов (только админ)

#### GET /analytics/export/customers
Экспорт клиентов в CSV (только админ)

#### GET /analytics/export/orders
Экспорт заказов в CSV (только админ)

---

## Коды ошибок

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `204 No Content` - Успешно, нет содержимого
- `400 Bad Request` - Неверные данные
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Доступ запрещён
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Ошибка сервера
