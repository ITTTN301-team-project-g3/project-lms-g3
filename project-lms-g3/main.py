from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.database import engine, Base
from app.routers import auth, subject, task, dashboard

# Import models de SQLAlchemy dang ky day du metadata
from app.models.user import User
from app.models.subject import Subject
from app.models.task import Task

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Project Manager API",
    description="He thong quan ly hoc tap - LMS",
    version="1.1.0"
)

app.include_router(auth.router)
app.include_router(subject.router)
app.include_router(task.router)
app.include_router(dashboard.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "Server LMS FastAPI hoat dong tot!"}
