# api/schemas/project.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    """Base schema for project, containing common fields."""
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass

class ProjectUpdate(ProjectBase):
    """Schema for updating an existing project."""
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectInDBBase(ProjectBase):
    """Base schema for project data as stored in the database."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    """Schema for project data returned to the client."""
    pass
