from fastapi import FastAPI
from api.endpoints import tasks, projects, categories, users, ai
from database.connection import Base, engine


app = FastAPI(title="Task Management System")


app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])


@app.on_event("startup")
def on_startup():
 Base.metadata.create_all(bind=engine)