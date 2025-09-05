# database/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base

class User(Base):
    """
    SQLAlchemy model for a user in the system.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tasks = relationship("Task", back_populates="owner")
    projects = relationship("Project", back_populates="owner")
    categories = relationship("Category", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Project(Base):
    """
    SQLAlchemy model for a project. Tasks can belong to projects.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class Category(Base):
    """
    SQLAlchemy model for a task category (e.g., Work, Personal, Study).
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # Category names should be unique for a user? (Consider scope later)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="categories")
    tasks = relationship("Task", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Task(Base):
    """
    SQLAlchemy model for a task.
    Includes fields for AI suggestions and performance tracking.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="To Do") # e.g., "To Do", "In Progress", "Done", "On Hold", "Cancelled"
    deadline = Column(DateTime(timezone=True), nullable=True)

    # Priority & Urgency/Importance (AI-calculated or user-defined)
    priority = Column(Integer, default=5, index=True) # e.g., 1 (highest) to 10 (lowest)
    urgency_score = Column(Float, nullable=True)    # AI calculated score (e.g., 0.0 to 1.0)
    importance_score = Column(Float, nullable=True) # AI calculated score (e.g., 0.0 to 1.0)

    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    owner = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")

    # Time tracking
    initial_estimated_time_hours = Column(Float, nullable=True) # User's initial estimate
    ai_estimated_time_hours = Column(Float, nullable=True)      # AI's refined estimate
    confidence_score = Column(Float, nullable=True) # AI's confidence in the estimate (0.0 to 1.0)
    actual_time_spent_hours = Column(Float, nullable=True)      # Time recorded by user/system
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Additional fields for AI & organization
    tags = Column(String, nullable=True) # Comma-separated string of tags, e.g., "urgent,meeting,report"
    reference_docs = Column(Text, nullable=True) # URLs or paths to reference documents
    
    # AI-generated suggestions (for future storage, optional for prototype)
    # ai_suggested_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    # ai_suggested_tags = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
