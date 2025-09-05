# database/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional

from . import models # models.py is in the same directory

# Import specific schemas used in CRUD functions
from api.schemas.user import UserCreate, UserBase, UserLogin
from api.schemas.project import ProjectCreate, ProjectUpdate
from api.schemas.category import CategoryCreate, CategoryUpdate
from api.schemas.task import TaskCreate, TaskUpdate, TaskPriorityUpdate, TaskUrgencyImportance, TaskTimeEstimation

from core.security import get_password_hash

# --- User CRUD Operations ---

def get_user(db: Session, user_id: int):
    """Retrieve a user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Retrieve a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of users."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate): # Use UserCreate directly
    """Create a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserBase): # Use UserBase directly
    """Update an existing user."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Delete a user by their ID."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# --- Project CRUD Operations ---

def get_project(db: Session, project_id: int):
    """Retrieve a project by its ID."""
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_user_project(db: Session, project_id: int, user_id: int):
    """Retrieve a project by its ID, ensuring it belongs to the specified user."""
    return db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == user_id
    ).first()

def get_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Retrieve projects belonging to a specific user."""
    return db.query(models.Project).filter(models.Project.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_project(db: Session, project: ProjectCreate, user_id: int): # Use ProjectCreate directly
    """Create a new project for a user."""
    db_project = models.Project(**project.model_dump(), owner_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_update: ProjectUpdate): # Use ProjectUpdate directly
    """Update an existing project."""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        for key, value in project_update.model_dump(exclude_unset=True).items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    """Delete a project by its ID."""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project



# --- Category CRUD Operations ---

def get_category(db: Session, category_id: int):
    """Retrieve a category by its ID."""
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_user_category(db: Session, category_id: int, user_id: int):
    """Retrieve a category by its ID, ensuring it belongs to the specified user."""
    return db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.owner_id == user_id
    ).first()

def get_user_categories(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Retrieve categories belonging to a specific user."""
    return db.query(models.Category).filter(models.Category.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_category(db: Session, category: CategoryCreate, user_id: int): # Use CategoryCreate directly
    """Create a new category for a user."""
    db_category = models.Category(**category.model_dump(), owner_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category_update: CategoryUpdate): # Use CategoryUpdate directly
    """Update an existing category."""
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        for key, value in category_update.model_dump(exclude_unset=True).items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    """Delete a category by its ID."""
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category



# --- Task CRUD Operations ---

def get_task(db: Session, task_id: int):
    """Retrieve a task by its ID."""
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_user_task(db: Session, task_id: int, user_id: int):
    """Retrieve a task by its ID, ensuring it belongs to the specified user."""
    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user_id
    ).first()

def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100,
                   priority: Optional[int] = None,
                   status: Optional[str] = None, project_id: Optional[int] = None,
                   category_id: Optional[int] = None, search_query: Optional[str] = None):
    """
    Retrieve tasks belonging to a specific user, with optional filters and search.
    """
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)

    if status:
        query = query.filter(models.Task.status == status)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    if category_id:
        query = query.filter(models.Task.category_id == category_id)
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    if search_query:
        # Simple text search on title and description
        query = query.filter(
            (models.Task.title.ilike(f"%{search_query}%")) |
            (models.Task.description.ilike(f"%{search_query}%"))
        )

    return query.offset(skip).limit(limit).all()

def create_user_task(db: Session, task: TaskCreate, user_id: int): # Use TaskCreate directly
    """Create a new task for a user."""
    # Set default priority, urgency, importance if not provided by the schema
    priority_value = task.priority if task.priority is not None else 5
    urgency_score_value = task.urgency_score if hasattr(task, 'urgency_score') and task.urgency_score is not None else 0.0
    importance_score_value = task.importance_score if hasattr(task, 'importance_score') and task.importance_score is not None else 0.0

    # Get data from task schema, excluding the fields we want to set explicitly
    task_data_for_model = task.model_dump(exclude_unset=True)

    # Remove priority, urgency_score, importance_score from the dumped dictionary
    # as we are setting them explicitly below.
    task_data_for_model.pop('priority', None)
    task_data_for_model.pop('urgency_score', None)
    task_data_for_model.pop('importance_score', None)

    db_task = models.Task(
        **task_data_for_model, # Unpack the modified dictionary
        owner_id=user_id,
        priority=priority_value,
        urgency_score=urgency_score_value,
        importance_score=importance_score_value
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: TaskUpdate): # Use TaskUpdate directly
    """Update an existing task."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        
        # Handle actual_time_spent_hours if status changes to "Done" and times are available
        if db_task.status == "Done" and db_task.started_at and db_task.completed_at:
            time_diff = db_task.completed_at - db_task.started_at
            db_task.actual_time_spent_hours = time_diff.total_seconds() / 3600.0
        elif db_task.status != "Done":
            # Reset actual_time_spent_hours if task is no longer done
            db_task.actual_time_spent_hours = None

        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    """Delete a task by its ID."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task

def update_task_priority(db: Session, task_id: int, priority: int):
    """Update the priority of a task."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.priority = priority
        db.commit()
        db.refresh(db_task)
    return db_task

def update_task_urgency_importance(db: Session, task_id: int, urgency_score: float, importance_score: float, priority: int) -> Optional[models.Task]:
    """Update urgency, importance, and priority scores of a task (typically by AI)."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.urgency_score = urgency_score
        db_task.importance_score = importance_score
        db_task.priority = priority
        db.commit()
        db.refresh(db_task)
    return db_task

def update_task_ai_estimated_time(db: Session, task_id: int, ai_estimated_time_hours: float, confidence_score: Optional[float] = None) -> Optional[models.Task]:
    """
    Update the AI estimated time and optional confidence score for a task.
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.ai_estimated_time_hours = ai_estimated_time_hours
        if confidence_score is not None: # Ensure confidence_score is provided before setting
            db_task.confidence_score = confidence_score 
        db.commit()
        db.refresh(db_task)
    return db_task