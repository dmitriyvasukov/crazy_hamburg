# Deployment Guide

## Требования

- Docker 20.10+
- Docker Compose 2.0+
- Минимум 2GB RAM
- PostgreSQL 15 (или через Docker)

## Подготовка

### 1. Клонировать репозиторий

```bash
git clone <repository-url>
cd dwc-shop-backend
```

### 2. Настроить переменные окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и установите:
- `SECRET_KEY` - секретный ключ (сгенерируйте случайную строку)
- `ADMIN_PHONE` - телефон администратора
- `ADMIN_PASSWORD` - пароль администратора
- `YUKASSA_SHOP_ID` - ID магазина в ЮKassa
- `YUKASSA_SECRET_KEY` - секретный ключ ЮKassa
- `DATABASE_URL` - URL подключения к PostgreSQL

### 3. Запустить через Docker Compose

```bash
# Собрать образы
make build

# Запустить сервисы
make up

# Проверить логи
make logs
```

Сервисы будут доступны на:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### 4. Инициализировать базу данных

```bash
make init
```

Это создаст:
- Администратора с указанными в `.env` данными
- Технические страницы (FAQ, Оферта, и т.д.)

## Production Deployment

### На VPS/Dedicated Server

1. Установите Docker и Docker Compose на сервер

2. Настройте файрвол:
```bash
# Разрешить HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Разрешить SSH
sudo ufw allow 22/tcp

sudo ufw enable
```

3. Используйте reverse proxy (Nginx):

```nginx
server {
    listen 80;
    server_name api.dwc-shop.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. Настройте SSL с Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.dwc-shop.com
```

5. Настройте автоматическое обновление:
```bash
# В crontab
0 3 * * * cd /path/to/project && docker-compose pull && docker-compose up -d
```

### На облачных платформах

#### AWS ECS / Azure Container Instances / Google Cloud Run

1. Соберите Docker образ:
```bash
docker build -t dwc-shop-backend .
```

2. Загрузите в registry:
```bash
docker tag dwc-shop-backend:latest registry.example.com/dwc-shop-backend:latest
docker push registry.example.com/dwc-shop-backend:latest
```

3. Настройте переменные окружения в платформе

4. Настройте внешнюю БД (AWS RDS, Azure Database, Cloud SQL)

## Мониторинг

### Логи

```bash
# Все логи
docker-compose logs -f

# Логи backend
docker-compose logs -f backend

# Логи БД
docker-compose logs -f db
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Метрики

Рекомендуется настроить:
- Prometheus для сбора метрик
- Grafana для визуализации
- Sentry для отслеживания ошибок

## Backup

### База данных

```bash
# Создать backup
docker-compose exec db pg_dump -U dwc_user dwc_shop > backup_$(date +%Y%m%d).sql

# Восстановить backup
docker-compose exec -T db psql -U dwc_user dwc_shop < backup_20240101.sql
```

### Автоматический backup

```bash
# В crontab
0 2 * * * cd /path/to/project && docker-compose exec db pg_dump -U dwc_user dwc_shop | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

## Обновление

```bash
# Получить последние изменения
git pull

# Пересобрать образы
make build

# Применить миграции
docker-compose exec backend alembic upgrade head

# Перезапустить
make restart
```

## Troubleshooting

### База данных недоступна

```bash
# Проверить статус
docker-compose ps

# Перезапустить БД
docker-compose restart db
```

### Ошибки миграций

```bash
# Откатить последнюю миграцию
docker-compose exec backend alembic downgrade -1

# Повторно применить
docker-compose exec backend alembic upgrade head
```

### Проблемы с портами

```bash
# Проверить занятые порты
netstat -tuln | grep 8000
netstat -tuln | grep 5432

# Изменить порты в docker-compose.yml
```

## Безопасность

1. **Никогда** не коммитьте `.env` файл
2. Используйте сильные пароли
3. Регулярно обновляйте зависимости
4. Настройте rate limiting
5. Используйте HTTPS в production
6. Ограничьте доступ к БД
7. Регулярно делайте backup
8. Мониторьте логи на подозрительную активность
