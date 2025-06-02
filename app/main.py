from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from resources.models import Base, Todos
from resources.db import engine, SessionLocal

app = FastAPI()

Base.metadata.create_all(bind=engine)  # Create database tables


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todos/{todo_id}")
async def read_todo(todo_id: int, db: db_dependency):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")
