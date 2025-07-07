from main import app
from resources.routers.todos import get_db, get_current_user
from resources.models import Users
from fastapi.testclient import TestClient
from fastapi import status
from .test_db import TestingSessionLocal, engine
import pytest
from resources.models import Todos


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return Users(id=1, username="testuser", email="testuser@email.com", role="admin")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


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


def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Todo"


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Todo"
    assert data["description"] == "This is a test todo item."
    assert data["owner_id"] == 1


def test_read_one_not_found(test_todo):
    response = client.get("/todos/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Todo not found"


def test_create_todo(test_todo):
    new_todo = {
        "title": "New Todo",
        "description": "This is a new todo item.",
        "complete": False,
        "priority": 2,
    }
    response = client.post("/todos/", json=new_todo)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Todo"
    assert data["description"] == "This is a new todo item."
    assert data["complete"] is False
    assert data["priority"] == 2
    assert data["owner_id"] == 1


def test_update_todo(test_todo):
    updated_todo = {
        "title": "Updated Todo",
        "description": "This is an updated todo item.",
        "complete": True,
        "priority": 3,
    }
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the update
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Todo"
    assert data["description"] == "This is an updated todo item."
    assert data["complete"] is True
    assert data["priority"] == 3


def test_update_todo_not_found(test_todo):
    updated_todo = {
        "title": "Updated Todo",
        "description": "This is an updated todo item.",
        "complete": True,
        "priority": 3,
    }
    response = client.put("/todos/9999", json=updated_todo)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Todo not found"


def test_delete_todo(test_todo):
    response = client.delete("/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the deletion
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Todo not found"


def test_delete_todo_not_found(test_todo):
    response = client.delete("/todos/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Todo not found"
