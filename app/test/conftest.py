from resources.models import Todos, Users
from .test_db import engine, TestingSessionLocal
import pytest
from resources.routers.auth import bcrypt_context


@pytest.fixture
def test_user():
    user = Users(
        username="testuser",
        email="test@email.com",
        first_name="Test",
        last_name="User",
        phone_number="1234567890",
        hashed_password=bcrypt_context.hash("password"),
        role="admin",
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    with engine.connect() as connection:
        connection.execute(Users.__table__.delete())
        connection.commit()


@pytest.fixture
def test_todo(test_user):
    db = TestingSessionLocal()
    todo = Todos(
        title="Test Todo",
        description="This is a test todo item.",
        complete=False,
        priority=1,
        owner_id=test_user.id,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    with engine.connect() as connection:
        connection.execute(Todos.__table__.delete())
        connection.commit()
