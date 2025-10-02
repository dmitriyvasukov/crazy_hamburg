# 🚀 Quick Start Guide

Быстрый запуск DWC Shop Backend за 5 минут!

## Шаг 1: Клонирование и настройка (1 мин)

```bash
# Клонировать репозиторий
git clone <repository-url>
cd dwc-shop-backend

# Скопировать файл с переменными окружения
cp .env.example .env

# Отредактировать .env (опционально для разработки)
# Для начала можно оставить значения по умолчанию
```

## Шаг 2: Запуск через Docker (2 мин)

```bash
# Запустить все сервисы
docker-compose up -d

# Дождаться запуска (проверить статус)
docker-compose ps
```

Вы должны увидеть два контейнера в статусе "Up":
- `dwc_db` - PostgreSQL база данных
- `dwc_backend` - FastAPI приложение

## Шаг 3: Инициализация базы данных (1 мин)

```bash
# Создать администратора и базовые страницы
docker-compose exec backend python -m app.init_db
```

Вы увидите:
```
✅ Создан администратор: +79999999999
✅ Создана страница: faq
✅ Создана страница: offer
✅ Создана страница: privacy
✅ Создана страница: about
✅ База данных инициализирована успешно!
```

## Шаг 4: Проверка (1 мин)

```bash
# Проверить, что API работает
curl http://localhost:8000/health
```

Ответ должен быть:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

## 🎉 Готово!

Ваш backend запущен и доступен:

- **API**: http://localhost:8000
- **Swagger документация**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Первые действия

### 1. Войти как администратор

Откройте Swagger UI: http://localhost:8000/docs

**Шаг 1:** Найдите endpoint `POST /api/v1/auth/login`

**Шаг 2:** Нажмите "Try it out" и введите:
```json
{
  "phone": "+79999999999",
  "password": "admin123"
}
```

**Шаг 3:** Скопируйте полученный `access_token`

**Шаг 4:** Нажмите кнопку "Authorize" в правом верхнем углу Swagger UI

**Шаг 5:** Введите: `Bearer ВАШ_ТОКЕН`

### 2. Создать первый товар

В Swagger UI найдите endpoint `POST /api/v1/products/`

```json
{
  "name": "Футболка DWC Classic",
  "description": "Классическая дизайнерская футболка из лимитированной коллекции",
  "article": "DWC-TS-001",
  "price": 2500,
  "sizes": ["Oki", "Big"],
  "size_table": {
    "Oki": {
      "chest": "100-105 см",
      "length": "70 см"
    },
    "Big": {
      "chest": "110-115 см",
      "length": "75 см"
    }
  },
  "care_instructions": "Стирка при 30°C, не отбеливать, гладить при низкой температуре",
  "order_type": "order",
  "stock_count": 10,
  "preorder_waves_total": 0,
  "preorder_wave_capacity": 0,
  "media_urls": [
    "https://example.com/tshirt1.jpg",
    "https://example.com/tshirt2.jpg"
  ]
}
```

### 3. Зарегистрировать клиента

Endpoint: `POST /api/v1/auth/register`

```json
{
  "phone": "+79001234567",
  "password": "mypassword123"
}
```

### 4. Создать заказ

Сначала войдите как клиент, затем используйте endpoint `POST /api/v1/orders/`

```json
{
  "items": [
    {
      "product_id": 1,
      "size": "Oki",
      "quantity": 1
    }
  ],
  "delivery_address": "Москва, ул. Ленина, д. 1, кв. 10"
}
```

## Полезные команды

```bash
# Посмотреть логи
docker-compose logs -f backend

# Остановить сервисы
docker-compose down

# Перезапустить
docker-compose restart

# Полностью очистить и начать заново
docker-compose down -v
docker-compose up -d
docker-compose exec backend python -m app.init_db
```

## Что дальше?

📖 Изучите полную документацию:
- [README.md](README.md) - Основная документация
- [API.md](docs/API.md) - Описание всех endpoints
- [EXAMPLES.md](docs/EXAMPLES.md) - Примеры использования
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Архитектура проекта
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Деплой в production

🔧 Настройте интеграции:
- ЮKassa для приёма платежей
- SMS провайдер для отправки кодов
- CORS для вашего frontend

🎨 Разработайте frontend:
- Используйте Swagger UI как reference
- Подключитесь к API используя токены
- Реализуйте корзину и оформление заказов

## Структура проекта

```
dwc-shop-backend/
├── app/
│   ├── api/endpoints/     # API роутеры
│   ├── core/              # Конфигурация
│   ├── models/            # Модели БД
│   ├── schemas/           # Валидация
│   ├── services/          # Бизнес-логика
│   └── main.py           # Точка входа
├── docs/                  # Документация
├── tests/                 # Тесты
├── .env                   # Настройки
├── docker-compose.yml     # Docker конфигурация
└── README.md             # Документация
```

## Возникли проблемы?

### Порт 8000 занят

```bash
# Измените порт в docker-compose.yml
ports:
  - "8001:8000"  # Вместо 8000:8000
```

### База данных не подключается

```bash
# Проверьте логи БД
docker-compose logs db

# Пересоздайте volume
docker-compose down -v
docker-compose up -d
```

### Миграции не применяются

```bash
# Примените вручную
docker-compose exec backend alembic upgrade head
```

## Контакты и поддержка

- GitHub Issues: Создайте issue в репозитории
- Документация: См. папку `docs/`
- Email: support@dwc-shop.com

---

**Поздравляем! 🎊**

Ваш backend интернет-магазина DWC готов к использованию!
