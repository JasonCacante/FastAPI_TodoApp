from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from resources.models import Todos
from resources.db import SessionLocal
from resources.routers.auth import get_current_user
from resources.models import Users

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[Users, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    if user is None or user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()
    return {"detail": "Todo deleted successfully"}
