from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import models, crud
from database.connection import get_db
from api.dependencies import get_current_user

# Import TaskService instead of crud directly for core operations
from services.task_service import TaskService # NEW IMPORT

# Import all necessary schemas, including the new AI ones
from api.schemas.task import Task, TaskCreate, TaskUpdate, TaskPriorityUpdate, TaskStatusUpdate, TaskStatusEnum, TaskTimeEstimation
from api.schemas.ai import TaskSuggestionRequest, TaskSuggestionResponse # NEW IMPORT for AI schemas
from api.schemas.project import Project
from api.schemas.category import Category

router = APIRouter()

# Dependency to get TaskService instance
def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task_for_current_user(
    task: TaskCreate,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service) # Use TaskService
):
    """
    Create a new task for the current authenticated user.
    Optionally assign to a project or category.
    """
    if task.project_id:
        # Validate project belongs to user
        project = crud.get_project(task_service.db, task.project_id)
        if not project or project.owner_id != current_user.id:
            raise HTTPException(status_code=400, detail="Project not found or does not belong to you.")
    if task.category_id:
        # Validate category belongs to user
        category = crud.get_category(task_service.db, task.category_id)
        if not category or category.owner_id != current_user.id:
            raise HTTPException(status_code=400, detail="Category not found or does not belong to you.")
            
    # Use TaskService to create the task
    return task_service.create_task(task=task, user_id=current_user.id)

@router.get("/", response_model=List[Task])
def read_tasks_for_current_user(
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by task status"),
    priority: Optional[int] = Query(None, ge=1, le=10, description="Filter by task priority"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by title or description"), # Added search parameter
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service) # Use TaskService
):
    """
    Retrieve a list of tasks belonging to the current authenticated user, with optional filters.
    """
    # Pass filters directly to crud.get_user_tasks via task_service.db
    tasks = crud.get_user_tasks(
        db=task_service.db, # Use task_service's db session
        user_id=current_user.id,
        status=status.value if status else None, # Pass enum value to crud
        priority=priority,
        project_id=project_id,
        category_id=category_id,
        search_query=search, # Pass search query
        skip=skip,
        limit=limit
    )
    return tasks

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service) # Use TaskService
):
    """
    Retrieve a single task by ID.
    The task must belong to the current authenticated user.
    """
    db_task = task_service.get_task(task_id=task_id) # Use TaskService
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    return db_task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service) # Use TaskService
):
    """
    Update an existing task.
    The task must belong to the current authenticated user.
    """
    db_task = task_service.get_task(task_id=task_id) # Use TaskService
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    # Validate project_id or category_id if provided in update
    if task_update.project_id is not None:
        project = crud.get_project(task_service.db, task_update.project_id)
        if not project or project.owner_id != current_user.id:
            raise HTTPException(status_code=400, detail="Invalid project_id or project does not belong to you.")
    if task_update.category_id is not None:
        category = crud.get_category(task_service.db, task_update.category_id)
        if not category or category.owner_id != current_user.id:
            raise HTTPException(status_code=400, detail="Invalid category_id or category does not belong to you.")

    # Use TaskService to update the task
    return task_service.update_task(task_id=task_id, task_update=task_update)

@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service) # Use TaskService
):
    """
    Update the status of a task and automatically manage started_at/completed_at timestamps.
    The task must belong to the current authenticated user.
    """
    db_task = task_service.get_task(task_id=task_id) # Use TaskService
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task's status")

    task_data_to_update = status_update.model_dump(exclude_unset=True)

    # --- Logic for started_at and completed_at based on status changes ---
    if status_update.status == TaskStatusEnum.IN_PROGRESS and not db_task.started_at:
        task_data_to_update["started_at"] = datetime.now()
        task_data_to_update["completed_at"] = None # Reset if re-entering In Progress
    elif status_update.status == TaskStatusEnum.DONE and not db_task.completed_at:
        task_data_to_update["completed_at"] = datetime.now()
    elif status_update.status != TaskStatusEnum.DONE and db_task.completed_at:
        task_data_to_update["completed_at"] = None # Reset if not Done

    # Create a TaskUpdate schema from the new status and calculated times
    temp_task_update = TaskUpdate(**task_data_to_update)
    
    # Use TaskService to update the task
    updated_task = task_service.update_task(task_id=task_id, task_update=temp_task_update)
    return updated_task

@router.patch("/{task_id}/priority", response_model=Task)
def update_task_priority(
    task_id: int,
    priority_update: TaskPriorityUpdate,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service) # Use TaskService
):
    """
    Update the priority of a task.
    The task must belong to the current authenticated user.
    """
    db_task = task_service.get_task(task_id=task_id) # Use TaskService
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task's priority")
    
    # Note: TaskService doesn't have a specific update_task_priority function.
    # We will use the generic update_task with a TaskUpdate schema.
    task_update_data = TaskUpdate(priority=priority_update.priority)
    updated_task = task_service.update_task(task_id=task_id, task_update=task_update_data)
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service) # Use TaskService
):
    """
    Delete a task.
    The task must belong to the current authenticated user.
    """
    db_task = task_service.get_task(task_id=task_id) # Use TaskService
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    # Use TaskService to delete the task (this will also handle vector DB deletion)
    task_service.delete_task(task_id=task_id)
    return # FastAPI will handle 204 No Content


# --- NEW AI Endpoints ---

@router.post("/suggest", response_model=TaskSuggestionResponse)
async def get_task_suggestions( # Made async
    request: TaskSuggestionRequest,
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get AI-driven suggestions for task attributes (category, project, tags, priority)
    based on the provided title and description.
    """
    suggestions = await task_service.get_ai_suggestions_for_task(request=request, user_id=current_user.id) # Await the async call
    return suggestions

@router.post("/estimate", response_model=TaskTimeEstimation)
def estimate_task_time(
    task_data: TaskCreate, # Can use TaskCreate as input for estimation of a new task
    current_user: models.User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get an AI-driven estimate for the completion time of a new task.
    """
    estimated_time = task_service.estimate_task_completion_time(task_data=task_data, user_id=current_user.id)
    return estimated_time
