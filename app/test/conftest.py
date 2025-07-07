from resources.models import Todos
from .test_db import engine, TestingSessionLocal
import pytest


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Test Todo",
        description="This is a test todo item.",
        complete=False,
        priority=1,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    with engine.connect() as connection:
        connection.execute(Todos.__table__.delete())
        connection.commit()
