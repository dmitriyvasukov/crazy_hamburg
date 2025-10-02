"""
Database initialization script
Creates initial data: admin user and default pages
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User
from app.models.page import Page


def init_admin_user(db: Session) -> None:
    """Create initial admin user"""
    admin = db.query(User).filter(User.phone == settings.ADMIN_PHONE).first()
    
    if not admin:
        admin = User(
            phone=settings.ADMIN_PHONE,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            full_name="Администратор",
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"✅ Создан администратор: {settings.ADMIN_PHONE}")
    else:
        print(f"ℹ️  Администратор уже существует: {settings.ADMIN_PHONE}")


def init_default_pages(db: Session) -> None:
    """Create default pages"""
    pages = [
        {
            "slug": "faq",
            "title": "Часто задаваемые вопросы",
            "content": "<h1>FAQ</h1><p>Здесь будут ответы на часто задаваемые вопросы.</p>"
        },
        {
            "slug": "offer",
            "title": "Договор оферты",
            "content": "<h1>Договор оферты</h1><p>Текст договора оферты.</p>"
        },
        {
            "slug": "privacy",
            "title": "Политика конфиденциальности",
            "content": "<h1>Политика конфиденциальности</h1><p>Текст политики конфиденциальности.</p>"
        },
        {
            "slug": "about",
            "title": "О проекте",
            "content": "<h1>О проекте DWC</h1><p>Информация о магазине дизайнерской одежды.</p>"
        }
    ]
    
    for page_data in pages:
        existing = db.query(Page).filter(Page.slug == page_data["slug"]).first()
        if not existing:
            page = Page(**page_data)
            db.add(page)
            print(f"✅ Создана страница: {page_data['slug']}")
        else:
            print(f"ℹ️  Страница уже существует: {page_data['slug']}")
    
    db.commit()


def init_db() -> None:
    """Initialize database with default data"""
    print("🔄 Инициализация базы данных...")
    
    db = SessionLocal()
    try:
        init_admin_user(db)
        init_default_pages(db)
        print("✅ База данных инициализирована успешно!")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
