from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette import status
from pydantic import BaseModel
from resources.models import Users
from sqlalchemy.orm import Session
from resources.db import SessionLocal
from typing import Annotated
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRETE_KEY = "69b8cf2accd3b24bd659c662a9d9896411897bbdf29a1c44b1e286d6a65717a8"
ALOGITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    role: str
    phone_number: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="templates")


## Pages ##
@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


## Endpoints ##
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "user_id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRETE_KEY, algorithm=ALOGITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency
):
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALOGITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: db_dependency):
    user = Users(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        phone_number=user.phone_number,
        hashed_password=bcrypt_context.hash(user.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "username": user.username, "email": user.email}


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
