# main.py

from fastapi import FastAPI
from database.connection import create_db_tables
from api.endpoints import users, projects, categories, tasks

app = FastAPI(
    title="Task Management CRUD API",
    description="A FastAPI application for managing tasks, projects, and categories.",
    version="0.1.0",
)

# Call this function once when the application starts to create all database tables
@app.on_event("startup")
async def startup_event():
    create_db_tables()
    print("Database tables created or already exist.")

# Include the routers
app.include_router(users.router, prefix="/users", tags=["users", "Authentication"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Management CRUD API!"}

