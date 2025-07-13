from datetime import timedelta
from fastapi import HTTPException
from jose import jwt
from main import app
import pytest
from resources.routers.auth import (
    get_db,
    authenticate_user,
    create_access_token,
    SECRETE_KEY,
    ALOGITHM,
    get_current_user,
)
from .test_db import override_get_db, TestingSessionLocal

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(
        username=test_user.username, password="password", db=db
    )
    db.close()
    assert authenticated_user is not False
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username


def test_authenticate_user_invalid_credentials():
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(
        username="invaliduser", password="wrongpassword", db=db
    )
    db.close()
    assert authenticated_user is False


def test_create_access_token(test_user):
    token = create_access_token(
        username=test_user.username,
        user_id=test_user.id,
        expires_delta=timedelta(minutes=30),
    )
    assert isinstance(token, str)
    assert len(token) > 0

    decoded_token = jwt.decode(token, SECRETE_KEY, algorithms=[ALOGITHM])
    assert decoded_token["sub"] == test_user.username
    assert decoded_token["user_id"] == test_user.id


@pytest.mark.asyncio
async def test_get_current_user(test_user):
    db = TestingSessionLocal()
    token = create_access_token(
        username=test_user.username,
        user_id=test_user.id,
        expires_delta=timedelta(minutes=30),
    )
    current_user = await get_current_user(token, db=db)
    db.close()

    assert current_user is not None
    assert current_user.username == test_user.username
    assert current_user.id == test_user.id
    assert current_user.role == test_user.role


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    token = create_access_token(
        username="invaliduser",
        user_id=999,
        expires_delta=timedelta(minutes=30),
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, db=TestingSessionLocal())
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
