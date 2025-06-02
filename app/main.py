from fastapi import FastAPI, Depends, HTTPException, Path
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from resources.models import Base, Todos
from resources.db import engine, SessionLocal
from pydantic import BaseModel, Field

app = FastAPI()

Base.metadata.create_all(bind=engine)  # Create database tables


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


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoRequest, db: db_dependency):
    new_todo = Todos(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo
