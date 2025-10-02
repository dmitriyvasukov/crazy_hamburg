"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, get_current_user, get_current_admin
from app.models.user import User
from app.models.product import Product, OrderType
from app.models.page import Page

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_user(db_session):
    """Create admin user"""
    user = User(
        phone="+79999999999",
        password_hash=get_password_hash("admin123"),
        full_name="Admin",
        is_admin=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    """Create regular user"""
    user = User(
        phone="+79001234567",
        password_hash=get_password_hash("user123"),
        full_name="Test User",
        is_admin=False,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, regular_user):
    """Create authenticated client with regular user"""
    def override_get_current_user():
        return regular_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(client, admin_user):
    """Create authenticated client with admin user"""
    def override_get_current_user():
        return admin_user
    
    def override_get_current_admin():
        return admin_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    yield client
    app.dependency_overrides.clear()


# Keep old fixtures for backward compatibility  
@pytest.fixture
def admin_token(admin_user):
    """Get admin auth token"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": admin_user.id})
    return token


@pytest.fixture
def user_token(regular_user):
    """Get user auth token"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": regular_user.id})
    return token


@pytest.fixture
def test_product(db_session):
    """Create test product"""
    product = Product(
        name="Test T-Shirt",
        description="Test description",
        article="TEST-001",
        price=2500.0,
        sizes=["Oki", "Big"],
        order_type=OrderType.ORDER,
        stock_count=10,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_page(db_session):
    """Create test page"""
    page = Page(
        slug="test",
        title="Test Page",
        content="<h1>Test</h1>"
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(page)
    return page
