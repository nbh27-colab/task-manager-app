from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database import crud, models
from api.schemas import ProjectSchema


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def read_projects(db: Session = Depends(get_db)):
    return crud.get_all(db, models.Project)


@router.get("/{project_id}")
def read_project(project_id: int, db: Session = Depends(get_db)):
    return crud.get_by_id(db, models.Project, project_id)


@router.post("/")
def create_project(project: ProjectSchema, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Project, project)


@router.put("/{project_id}")
def update_project(project_id: int, project: ProjectSchema, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Project, project_id, project)


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Project, project_id)


