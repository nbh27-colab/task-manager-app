# api/schemas/task.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TaskStatusEnum(str, Enum):
    """Enumeration for task status."""
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"
    BLOCKED = "Blocked"

class TaskBase(BaseModel):
    """Base schema for task, containing common fields."""
    title: str
    description: Optional[str] = None
    status: Optional[str] = "To Do" # Default status
    deadline: Optional[datetime] = None
    project_id: Optional[int] = None
    category_id: Optional[int] = None
    initial_estimated_time_hours: Optional[float] = None
    tags: Optional[str] = None # Comma-separated string of tags
    reference_docs: Optional[str] = None # URLs or paths

class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    # title is required for creation
    title: str = Field(..., min_length=1, max_length=255)
    priority: Optional[int] = Field(None, ge=1, le=10, description="Priority from 1 (highest) to 10 (lowest).")
    urgency_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI calculated urgency score (0.0-1.0).")
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI calculated importance score (0.0-1.0).")


class TaskUpdate(TaskBase):
    """Schema for updating an existing task."""
    title: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    category_id: Optional[int] = None
    initial_estimated_time_hours: Optional[float] = None
    tags: Optional[str] = None
    reference_docs: Optional[str] = None
    # Fields for time tracking updates
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    ai_estimated_time_hours: Optional[float] = None
    actual_time_spent_hours: Optional[float] = None
    # Allow updating AI-related scores directly via TaskUpdate if needed
    priority: Optional[int] = Field(None, ge=1, le=10, description="Priority from 1 (highest) to 10 (lowest).")
    urgency_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI calculated urgency score (0.0-1.0).")
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI calculated importance score (0.0-1.0).")

class TaskUrgencyImportance(BaseModel):
    """Schema for AI urgency and importance scores."""
    urgency_score: float = Field(..., ge=0.0, le=1.0)
    importance_score: float = Field(..., ge=0.0, le=1.0)

class TaskInDBBase(TaskBase):
    """Base schema for task data as stored in the database."""
    id: int
    owner_id: int
    priority: int
    urgency_score: Optional[float] = None
    importance_score: Optional[float] = None
    ai_estimated_time_hours: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_time_spent_hours: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    """Schema for task data returned to the client."""
    pass

class TaskPriorityUpdate(BaseModel):
    """Schema for updating task priority."""
    priority: int = Field(..., ge=1, le=10) # Priority from 1 (highest) to 10 (lowest)

class TaskStatusUpdate(BaseModel):
    """Schema for updating task status."""
    status: str = Field(..., pattern="^(To Do|In Progress|Done|On Hold|Cancelled)$")

class TaskTimeEstimation(BaseModel):
    """Schema for AI time estimation response."""
    ai_estimated_time_hours: float
    confidence_score: Optional[float] = None # e.g., 0.0 to 1.0

# class TaskUrgencyImportance(BaseModel):
#     """Schema for AI urgency/importance calculation response."""
#     urgency_score: float
#     importance_score: float
#     priority: int # AI's suggested priority based on scores
