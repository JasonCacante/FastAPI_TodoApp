from fastapi import FastAPI
from resources.models import Base, Todos
from resources.db import engine
from resources.routers import auth, todos

app = FastAPI()

Base.metadata.create_all(bind=engine)  # Create database tables

app.include_router(auth.router)
app.include_router(todos.router)
