from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database import crud, models
from api.schemas import CategorySchema


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def read_categories(db: Session = Depends(get_db)):
    return crud.get_all(db, models.Category)


@router.get("/{category_id}")
def read_category(category_id: int, db: Session = Depends(get_db)):
    return crud.get_by_id(db, models.Category, category_id)


@router.post("/")
def create_category(category: CategorySchema, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Category, category)


@router.put("/{category_id}")
def update_category(category_id: int, category: CategorySchema, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Category, category_id, category)


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Category, category_id)