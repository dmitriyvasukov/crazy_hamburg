# DWC Internet Shop Backend

Backend для интернет-магазина дизайнерской одежды с поддержкой предзаказов.

## Основные возможности

- 🛍️ Управление товарами (обычные заказы и предзаказы)
- 👥 Система пользователей (администраторы и клиенты)
- 🎟️ Система промокодов
- 📦 Управление заказами и статусами
- 💳 Интеграция с ЮKassa
- 📊 Аналитика и отчёты
- 🔐 JWT аутентификация
- 📱 SMS верификация телефонов

## Технологический стек

- **FastAPI** - современный веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции БД
- **Pydantic** - валидация данных
- **Docker** - контейнеризация
- **JWT** - аутентификация

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone <repository-url>
cd dwc-shop-backend
```

### 2. Настройте переменные окружения

```bash
cp .env.example .env
# Отредактируйте .env файл, установите SECRET_KEY и другие параметры
```

### 3. Запустите через Docker Compose

```bash
# Собрать и запустить контейнеры
docker-compose up -d

# Или используйте Makefile
make up
```

### 4. Инициализируйте базу данных

```bash
# Создать администратора и базовые страницы
docker-compose exec backend python -m app.init_db

# Или через Makefile
make init
```

### 5. Готово!

- **API**: http://localhost:8000
- **Документация**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Вход администратора**: 
  - Телефон: `+79999999999` (по умолчанию, см. `.env`)
  - Пароль: `admin123` (по умолчанию, см. `.env`)

## Структура проекта

```
.
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Конфигурация и настройки
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   ├── utils/            # Утилиты
│   └── main.py          # Точка входа
├── alembic/             # Миграции БД
├── docker-compose.yml   # Docker настройки
├── Dockerfile          # Docker образ
└── requirements.txt    # Python зависимости
```

## API Документация

После запуска доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Основные команды

```bash
# Запустить сервисы
make up

# Остановить сервисы
make down

# Перезапустить сервисы
make restart

# Посмотреть логи
make logs

# Инициализировать БД
make init

# Создать новую миграцию
make migrate msg="description"

# Очистить всё
make clean
```

## Переменные окружения

Основные переменные в `.env`:

```env
# База данных
DATABASE_URL=postgresql://dwc_user:dwc_password@db:5432/dwc_shop

# Безопасность (ВАЖНО: измените в продакшене!)
SECRET_KEY=your-secret-key-here

# Администратор
ADMIN_PHONE=+79999999999
ADMIN_PASSWORD=admin123

# ЮKassa (получите в личном кабинете ЮKassa)
YUKASSA_SHOP_ID=your_shop_id
YUKASSA_SECRET_KEY=your_secret_key

# CORS (frontend URLs)
CORS_ORIGINS=["http://localhost:3000"]
```

Полный список см. в `.env.example`

## Примеры использования API

См. подробную документацию:
- [API Documentation](docs/API.md) - описание всех endpoints
- [Examples](docs/EXAMPLES.md) - примеры запросов
- [Architecture](docs/ARCHITECTURE.md) - архитектура проекта
- [Deployment](docs/DEPLOYMENT.md) - деплой в продакшен

### Быстрый пример

```bash
# 1. Регистрация пользователя
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79001234567", "password": "mypassword"}'

# 2. Получить список товаров
curl "http://localhost:8000/api/v1/products/"

# 3. Создать заказ (с токеном)
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"product_id": 1, "size": "Oki", "quantity": 1}],
    "delivery_address": "Москва, ул. Ленина, 1"
  }'
```

## Особенности реализации

### Система предзаказов

Товары могут иметь три типа:
- **order** - обычный заказ со склада
- **preorder** - предзаказ с волнами производства
- **waiting** - ожидание (все волны заполнены)

Когда клиент заказывает товар с предзаказом:
1. Товар добавляется в текущую волну
2. При заполнении волны автоматически открывается следующая
3. После заполнения всех волн товар переходит в статус "waiting"
4. Администратор управляет статусами волн через админ-панель

### Промокоды

- Можно привязать к конкретным товарам
- Поддержка процентной и фиксированной скидки
- Ограничение по количеству использований
- Ограничение по времени действия

### Платежи

Интеграция с ЮKassa:
- Автоматическое создание платежа
- Генерация чека для ФНС (54-ФЗ)
- Webhook для обработки статусов
- Поддержка отмены платежей

### Аналитика

- Статистика продаж за период
- Количество предзаказов
- Список клиентов
- Использование промокодов
- Экспорт в CSV

## Тестирование

```bash
# Запустить тесты
docker-compose exec backend pytest

# С покрытием
docker-compose exec backend pytest --cov=app
```

## Разработка

### Добавление новой миграции

```bash
# Создать миграцию автоматически
make migrate msg="add new field"

# Применить миграции
docker-compose exec backend alembic upgrade head

# Откатить миграцию
docker-compose exec backend alembic downgrade -1
```

### Структура кода

- `app/api/endpoints/` - API роутеры
- `app/models/` - модели БД (SQLAlchemy)
- `app/schemas/` - схемы валидации (Pydantic)
- `app/services/` - бизнес-логика
- `app/core/` - конфигурация и утилиты

## Production Deployment

См. [DEPLOYMENT.md](docs/DEPLOYMENT.md) для детальных инструкций.

Короткий чек-лист:
1. ✅ Измените `SECRET_KEY` на случайную строку
2. ✅ Настройте реальные credentials для ЮKassa
3. ✅ Настройте CORS для вашего frontend
4. ✅ Используйте HTTPS
5. ✅ Настройте backup базы данных
6. ✅ Настройте мониторинг и логирование
7. ✅ Настройте firewall

## Troubleshooting

### База данных не запускается

```bash
# Проверить логи
docker-compose logs db

# Пересоздать volume
docker-compose down -v
docker-compose up -d
```

### Backend не запускается

```bash
# Проверить логи
docker-compose logs backend

# Пересобрать образ
docker-compose build backend
docker-compose up -d backend
```

### Ошибки миграций

```bash
# Откатить все миграции
docker-compose exec backend alembic downgrade base

# Применить заново
docker-compose exec backend alembic upgrade head
```
