#!/bin/bash

echo "🚀 Инициализация DWC Shop Backend"
echo ""

# Wait for database
echo "⏳ Ожидание запуска базы данных..."
sleep 5

# Run migrations
echo "📦 Применение миграций базы данных..."
alembic upgrade head

# Initialize database with default data
echo "🔧 Инициализация данных..."
python -m app.init_db

echo ""
echo "✅ Инициализация завершена!"
echo "🌐 API доступно по адресу: http://localhost:8000"
echo "📚 Документация: http://localhost:8000/docs"
echo ""
echo "👤 Администратор:"
echo "   Телефон: ${ADMIN_PHONE}"
echo "   Пароль: ${ADMIN_PASSWORD}"
