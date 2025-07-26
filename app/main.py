from fastapi import FastAPI, Request
from resources.models import Base
from resources.db import engine
from resources.routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)  # Create database tables

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/")
def test(resquest: Request):
    return templates.TemplateResponse("home.html", {"request": resquest})


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running successfully!"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
