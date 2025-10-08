from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database import crud, models
from api.schemas import TaskSchema


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def read_tasks(db: Session = Depends(get_db)):
    return crud.get_all(db, models.Task)


@router.get("/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    return crud.get_by_id(db, models.Task, task_id)


@router.post("/")
def create_task(task: TaskSchema, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Task, task)


@router.put("/{task_id}")
def update_task(task_id: int, task: TaskSchema, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Task, task_id, task)


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Task, task_id)