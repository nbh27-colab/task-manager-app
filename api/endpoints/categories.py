# api/endpoints/categories.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import crud, models
from database.connection import get_db
from api.dependencies import get_current_user
from api.schemas.category import Category, CategoryCreate, CategoryUpdate

router = APIRouter()

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category_for_current_user(
    category: CategoryCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new category for the current authenticated user.
    """
    # Optional: check if category name already exists for this user
    # existing_categories = crud.get_user_categories(db, current_user.id)
    # if any(cat.name.lower() == category.name.lower() for cat in existing_categories):
    #     raise HTTPException(status_code=400, detail="Category with this name already exists.")
    return crud.create_user_category(db=db, category=category, user_id=current_user.id)

@router.get("/", response_model=List[Category])
def read_categories_for_current_user(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of categories belonging to the current authenticated user.
    """
    categories = crud.get_user_categories(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific category by its ID.
    The category must belong to the current authenticated user.
    """
    category = crud.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this category")
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing category.
    The category must belong to the current authenticated user.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    if db_category.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this category")
    
    return crud.update_category(db=db, category_id=category_id, category_update=category_update)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a category.
    The category must belong to the current authenticated user.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    if db_category.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this category")
    
    crud.delete_category(db=db, category_id=category_id)
    return {"message": "Category deleted successfully"}
