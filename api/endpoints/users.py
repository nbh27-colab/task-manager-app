# api/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # <-- Correct for form data login
from sqlalchemy.orm import Session
from datetime import timedelta

from database import crud, models
from database.connection import get_db
from core.security import verify_password, create_access_token
from api.dependencies import get_current_user
from core.config import settings # <-- Import settings object

from api.schemas.user import UserCreate, User, UserBase# Only import what's directly used as response_model or request_body

router = APIRouter()

# --- User Registration ---
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# --- User Login / Token Generation ---
@router.post("/token", response_model=dict) # Response model will be a dict containing access_token and token_type
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and generate an access token.
    """
    db_user = crud.get_user_by_email(db, email=form_data.username) # Use form_data.username
    if not db_user or not verify_password(form_data.password, db_user.hashed_password): # Use form_data.password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes) # Use settings object
    access_token = create_access_token(
        data={"sub": db_user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Get Current User Profile (Protected) ---
@router.get("/me/", response_model=User) # Path is relative to prefix /users, so /users/me/
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Retrieve the profile of the current authenticated user.
    Requires authentication.
    """
    return current_user

# --- Get User by ID (Protected, for admin or specific use cases) ---
@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve a user by ID.
    Requires authentication.
    """
    # For a prototype, we'll allow any authenticated user to get any user by ID.
    # In a real application, you'd add authorization checks here (e.g., current_user is admin, or current_user.id == user_id)
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# --- Update User (Protected) ---
@router.put("/me/", response_model=User)
def update_user_profile(user_update: UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update the profile of the current authenticated user.
    Requires authentication.
    """
    # Note: This endpoint does not allow updating password directly. A separate endpoint for password change is recommended.
    updated_user = crud.update_user(db, user_id=current_user.id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(status_code=500, detail="Failed to update user profile")
    return updated_user

# --- Delete User (Protected) ---
@router.delete("/me/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete the profile of the current authenticated user.
    Requires authentication.
    """
    if not crud.delete_user(db, current_user.id):
        raise HTTPException(status_code=500, detail="Failed to delete user profile")
    return {"message": "User deleted successfully"}

