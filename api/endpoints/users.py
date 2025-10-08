from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database import crud, models
from api.schemas import UserSchema


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def read_users(db: Session = Depends(get_db)):
    return crud.get_all(db, models.User)


@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_by_id(db, models.User, user_id)


@router.post("/")
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    return crud.create_item(db, models.User, user)


@router.put("/{user_id}")
def update_user(user_id: int, user: UserSchema, db: Session = Depends(get_db)):
    return crud.update_item(db, models.User, user_id, user)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.User, user_id)