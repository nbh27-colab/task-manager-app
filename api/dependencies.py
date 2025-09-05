# api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError # Correct: JWTError is directly from jose
import json # Added for debugging prints

from . import schemas
from database import crud, models
from database.connection import get_db
from core.security import decode_access_token # type: ignore # Ignoring type check for now, will resolve later

# OAuth2PasswordBearer will be used to extract the token from the request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token") # Corrected tokenUrl

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTPException if the token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        
        # --- DEBUGGING PRINTS ---
        print(f"Debug: Token received: {token[:30]}...") # Print first 30 chars of token
        if payload is None:
            print("Debug: Payload is None after decoding.")
            raise credentials_exception
        print(f"Debug: Decoded payload: {json.dumps(payload, indent=2)}") # Print full payload
        # --- END DEBUGGING PRINTS ---

        # --- IMPORTANT FIX HERE: Get 'sub' as string and convert to int ---
        user_id_str: str = payload.get("sub") 
        if user_id_str is None:
            print("Debug: 'sub' claim is missing or None in payload.")
            raise credentials_exception
        
        try:
            user_id = int(user_id_str) # Convert string 'sub' to int
        except (ValueError, TypeError):
            print(f"Debug: 'sub' claim is not a valid integer string: {user_id_str}")
            raise credentials_exception
        # --- END FIX ---

    except JWTError as e: # This is the correct way to catch JWTError
        print(f"Debug: JWTError in get_current_user: {e}")
        raise credentials_exception
    except Exception as e: # Catch any other unexpected errors
        print(f"Debug: An unexpected error in get_current_user: {e}")
        raise credentials_exception
    
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        print(f"Debug: User with ID {user_id} not found in database.")
        raise credentials_exception
    
    print(f"Debug: Successfully authenticated user: {user.email} (ID: {user.id})") # Success message
    return user