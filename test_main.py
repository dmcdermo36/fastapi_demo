import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from db_models import Base, Books

# Create a new database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the testing database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create the database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Setup: Create tables and add initial data
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Books(title="Test Book", author="Test Author", description="Test Description", rating=5))
    db.commit()
    db.close()
    yield
    # Teardown: Drop tables
    Base.metadata.drop_all(bind=engine)

def test_read_api(setup_database):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Book"
    assert data[0]["author"] == "Test Author"
    assert data[0]["description"] == "Test Description"
    assert data[0]["rating"] == 5

def test_create_book():
    new_book = {
        "title": "New Book",
        "author": "New Author",
        "description": "New Description",
        "rating": 4
    }
    response = client.post("/", json=new_book)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Book"
    assert data["author"] == "New Author"
    assert data["description"] == "New Description"
    assert data["rating"] == 4
    assert "id" in data