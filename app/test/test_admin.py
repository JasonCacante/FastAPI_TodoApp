from fastapi import status
from main import app
from resources.routers.admin import get_db, get_current_user
from .test_db import client, override_get_db, override_get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_todos_admin(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Todo"


def test_delete_todo_admin(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the todo was deleted
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Todo not found"


def test_delete_todo_not_found():
    response = client.delete("/admin/todo/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Todo not found"
