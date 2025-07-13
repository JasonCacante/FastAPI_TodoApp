from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from resources.models import Todos, Users
from resources.db import SessionLocal
from pydantic import BaseModel, Field
from resources.routers import auth
from resources.routers.auth import get_current_user
from resources.models import Users

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "current_secure_password123",
                "new_password": "new_secure_password123",
            }
        }
    }


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[Users, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Users).filter(Users.id == user.id).first()


@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_model = db.query(Users).filter(Users.id == user.id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    if not auth.bcrypt_context.verify(
        user_verification.old_password, user_model.hashed_password
    ):
        raise HTTPException(status_code=403, detail="Old password is incorrect")
    user_model.hashed_password = auth.bcrypt_context.hash(
        user_verification.new_password
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return {"detail": "Password changed successfully"}


@router.put("/phone_number", status_code=status.HTTP_200_OK)
async def update_phone_number(
    user: user_dependency, db: db_dependency, phone_number: str
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_model = db.query(Users).filter(Users.id == user.id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    return {"detail": "Phone number updated successfully"}
