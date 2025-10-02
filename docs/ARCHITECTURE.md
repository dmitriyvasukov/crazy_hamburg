# Architecture Documentation

## Обзор архитектуры

DWC Shop Backend построен на современном стеке технологий с использованием микросервисной архитектуры и следованием принципам Clean Architecture.

## Структура проекта

```
dwc-shop-backend/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── endpoints/          # Роутеры для каждого модуля
│   │   │   ├── auth.py         # Аутентификация
│   │   │   ├── users.py        # Пользователи
│   │   │   ├── products.py     # Товары
│   │   │   ├── orders.py       # Заказы
│   │   │   ├── promo_codes.py  # Промокоды
│   │   │   ├── pages.py        # Страницы
│   │   │   └── analytics.py    # Аналитика
│   │   └── __init__.py         # API роутер
│   │
│   ├── core/                   # Ядро приложения
│   │   ├── config.py           # Конфигурация
│   │   ├── database.py         # Подключение к БД
│   │   └── security.py         # Безопасность и JWT
│   │
│   ├── models/                 # SQLAlchemy модели
│   │   ├── user.py             # Модель пользователя
│   │   ├── product.py          # Модель товара
│   │   ├── order.py            # Модель заказа
│   │   ├── promo_code.py       # Модель промокода
│   │   ├── page.py             # Модель страницы
│   │   └── preorder.py         # Модели предзаказов
│   │
│   ├── schemas/                # Pydantic схемы
│   │   ├── user.py             # Схемы пользователя
│   │   ├── product.py          # Схемы товара
│   │   ├── order.py            # Схемы заказа
│   │   ├── promo_code.py       # Схемы промокода
│   │   └── page.py             # Схемы страницы
│   │
│   ├── services/               # Бизнес-логика
│   │   ├── payment.py          # Сервис оплаты (ЮKassa)
│   │   └── sms.py              # Сервис SMS
│   │
│   ├── utils/                  # Утилиты
│   │   └── validators.py       # Валидаторы
│   │
│   ├── init_db.py              # Инициализация БД
│   └── main.py                 # Точка входа
│
├── alembic/                    # Миграции БД
│   ├── versions/               # Версии миграций
│   └── env.py                  # Конфигурация Alembic
│
├── docs/                       # Документация
│   ├── API.md                  # API документация
│   ├── ARCHITECTURE.md         # Архитектура
│   └── DEPLOYMENT.md           # Деплой
│
├── scripts/                    # Скрипты
│   └── init.sh                 # Скрипт инициализации
│
├── tests/                      # Тесты
│   └── test_auth.py            # Тесты аутентификации
│
├── .env                        # Переменные окружения
├── .env.example                # Пример переменных
├── .gitignore                  # Git ignore
├── alembic.ini                 # Конфигурация Alembic
├── docker-compose.yml          # Docker Compose
├── Dockerfile                  # Docker образ
├── Makefile                    # Команды управления
├── pytest.ini                  # Конфигурация pytest
├── README.md                   # Readme
└── requirements.txt            # Python зависимости
```

## Слои архитектуры

### 1. API Layer (app/api/)

Отвечает за:
- HTTP endpoints
- Валидацию входных данных
- Сериализацию ответов
- Обработку ошибок

**Принципы:**
- Каждый модуль имеет свой роутер
- Используются Pydantic схемы для валидации
- Dependency Injection для получения сессии БД

### 2. Business Logic Layer (app/services/)

Отвечает за:
- Бизнес-логику приложения
- Интеграцию с внешними сервисами
- Сложные операции

**Сервисы:**
- `PaymentService` - работа с ЮKassa
- `SMSService` - отправка SMS

### 3. Data Access Layer (app/models/)

Отвечает за:
- Определение структуры БД
- ORM маппинг
- Связи между таблицами

**Модели:**
- `User` - пользователи
- `Product` - товары
- `Order` - заказы
- `PromoCode` - промокоды
- `Page` - страницы
- `PreorderWave` - волны предзаказов

### 4. Core Layer (app/core/)

Отвечает за:
- Конфигурацию приложения
- Безопасность
- Подключение к БД

## База данных

### Схема

```
users
├── id (PK)
├── phone (unique)
├── password_hash
├── full_name
├── email
├── address
├── cdek_point
├── telegram
├── vk
├── is_admin
├── is_active
├── created_at
└── updated_at

products
├── id (PK)
├── name
├── description
├── article (unique)
├── price
├── sizes (JSON)
├── size_table (JSON)
├── care_instructions
├── order_type (enum)
├── stock_count
├── preorder_waves_total
├── preorder_wave_capacity
├── current_wave
├── current_wave_count
├── is_active
├── is_archived
├── created_at
└── updated_at

product_media
├── id (PK)
├── product_id (FK)
├── url
├── order
└── created_at

orders
├── id (PK)
├── user_id (FK)
├── order_number (unique)
├── total_amount
├── discount_amount
├── final_amount
├── status (enum)
├── payment_status (enum)
├── tracking_number
├── delivery_address
├── cdek_point
├── payment_id
├── payment_url
├── receipt_url
├── promo_code_id (FK)
├── created_at
├── updated_at
├── paid_at
└── shipped_at

order_items
├── id (PK)
├── order_id (FK)
├── product_id (FK)
├── size
├── quantity
├── price
├── is_preorder
├── preorder_wave
└── created_at

promo_codes
├── id (PK)
├── code (unique)
├── description
├── discount_percent
├── discount_amount
├── max_uses
├── current_uses
├── valid_from
├── valid_until
├── is_active
├── created_at
└── updated_at

promo_code_products (many-to-many)
├── promo_code_id (FK)
└── product_id (FK)

pages
├── id (PK)
├── slug (unique)
├── title
├── content
├── created_at
└── updated_at

preorder_waves
├── id (PK)
├── product_id (FK)
├── wave_number
├── capacity
├── current_count
├── status (enum)
├── is_completed
├── created_at
├── updated_at
└── completed_at

preorder_statuses
├── id (PK)
├── order_id (FK)
├── wave_id (FK)
├── status (enum)
├── status_message
├── created_at
└── updated_at
```

## Потоки данных

### Создание заказа

```
1. Клиент → POST /api/v1/orders/
2. Валидация данных (Pydantic)
3. Проверка товаров и наличия
4. Применение промокода (если есть)
5. Создание заказа в БД
6. Создание позиций заказа
7. Обновление счётчиков товаров
8. Создание платежа в ЮKassa
9. Возврат ссылки на оплату
```

### Обработка предзаказов

```
1. Клиент заказывает товар с order_type="preorder"
2. Проверка доступности текущей волны
3. Добавление к current_wave_count
4. Если волна заполнена:
   - current_wave += 1
   - current_wave_count = 0
5. Если все волны заполнены:
   - order_type = "waiting"
6. Админ управляет статусами волн
```

### Аутентификация

```
1. Клиент → POST /api/v1/auth/login
2. Проверка телефона и пароля
3. Создание JWT токена (действует 24ч)
4. Возврат токена клиенту
5. Клиент добавляет токен в заголовок Authorization
6. На каждом защищённом endpoint проверка токена
```

## Безопасность

### JWT Authentication
- Токены действуют 24 часа
- Алгоритм: HS256
- Секретный ключ хранится в переменных окружения

### Passwords
- Хеширование: bcrypt
- Минимум 6 символов
- Хранятся только хеши

### CORS
- Настраиваемый список разрешённых origins
- По умолчанию: localhost:3000, localhost:8000

### Database
- Подготовленные запросы (SQLAlchemy ORM)
- Защита от SQL injection
- Валидация всех входных данных

## Масштабирование

### Horizontal Scaling
- Stateless архитектура
- JWT токены (без сессий на сервере)
- Можно запустить несколько инстансов backend

### Database Scaling
- Read replicas для чтения
- Connection pooling
- Индексы на часто запрашиваемых полях

### Caching
- Redis для кэширования (можно добавить)
- Кэш промокодов
- Кэш товаров

## Мониторинг и логирование

### Логи
- Структурированные логи
- Уровни: DEBUG, INFO, WARNING, ERROR
- Вывод в stdout (Docker)

### Метрики
- Health check endpoint
- Можно добавить Prometheus metrics
- Отслеживание времени ответа

### Ошибки
- Централизованная обработка
- HTTP status codes
- Детальные сообщения об ошибках

## Тестирование

### Unit Tests
- pytest для unit тестов
- Тесты для каждого endpoint
- Моки для внешних сервисов

### Integration Tests
- Тесты с реальной БД
- Docker для test окружения

### Load Testing
- Apache Bench
- Locust
- k6

## Будущие улучшения

1. **WebSockets** - для real-time уведомлений
2. **Celery** - для фоновых задач
3. **Redis** - для кэширования
4. **Elasticsearch** - для поиска
5. **S3** - для хранения медиа
6. **GraphQL** - альтернативный API
7. **Rate Limiting** - защита от DDoS
8. **API Versioning** - для обратной совместимости
