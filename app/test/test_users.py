from fastapi import status
from main import app
from resources.routers.users import get_db, get_current_user
from .test_db import client, override_get_db, override_get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user(test_user):
    response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "testuser"
    assert data["email"] == "test@email.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["phone_number"] == "1234567890"
    assert data["role"] == "admin"


def test_change_password(test_user):
    response = client.put(
        "/user/password",
        json={
            "old_password": "password",
            "new_password": "password123",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Password changed successfully"}


def test_change_password_incorrect_old(test_user):
    response = client.put(
        "/user/password",
        json={
            "old_password": "wrongpassword",
            "new_password": "password123",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Old password is incorrect"}


def test_update_phone_number(test_user):
    response = client.put("/user/phone_number", params={"phone_number": "0987654321"})

    assert response.status_code == status.HTTP_200_OK
