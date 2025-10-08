from pydantic import BaseModel
from datetime import datetime


class UserSchema(BaseModel):
    name: str


class ProjectSchema(BaseModel):
    name: str


class CategorySchema(BaseModel):
    name: str


class TaskSchema(BaseModel):
    title: str
    description: str
    status: str = "todo"
    due_date: datetime
    category_id: int
    project_id: int