from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from starlette import status
from pydantic import BaseModel
from resources.models import Users
from sqlalchemy.orm import Session
from resources.db import SessionLocal
from typing import Annotated


router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    firs_name: str
    last_name: str
    role: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: db_dependency):
    user = Users(
        email=user.email,
        username=user.username,
        first_name=user.firs_name,
        last_name=user.last_name,
        role=user.role,
        hashed_password=bcrypt_context.hash(user.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "username": user.username, "email": user.email}
