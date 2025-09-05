# api/schemas/category.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    """Base schema for category, containing common fields."""
    name: str

class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass

class CategoryUpdate(CategoryBase):
    """Schema for updating an existing category."""
    name: Optional[str] = None

class CategoryInDBBase(CategoryBase):
    """Base schema for category data as stored in the database."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Category(CategoryInDBBase):
    """Schema for category data returned to the client."""
    pass
