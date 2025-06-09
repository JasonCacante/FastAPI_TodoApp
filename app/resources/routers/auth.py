from fastapi import APIRouter
from passlib.context import CryptContext
from starlette import status
from pydantic import BaseModel
from resources.models import Users


router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    firs_name: str
    last_name: str
    role: str


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest):
    user = Users(
        email=user.email,
        username=user.username,
        first_name=user.firs_name,
        last_name=user.last_name,
        role=user.role,
        hashed_password=bcrypt_context.hash(user.password),
    )
    return user
