from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from resources.models import Todos
from resources.db import SessionLocal
from pydantic import BaseModel, Field
from resources.routers import auth

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    completed: bool = False
    priority: int = Field(1, ge=1, le=5)  # Default priority set to 1

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Todo Example",
                "description": "This is an example of a todo item.",
                "completed": False,
                "priority": 1,
            }
        }
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoRequest, db: db_dependency):
    new_todo = Todos(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(todo: TodoRequest, db: db_dependency, todo_id: int = Path(gt=0)):
    existing_todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    for key, value in todo.model_dump().items():
        setattr(existing_todo, key, value)

    db.commit()
    return None


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()
    return None
