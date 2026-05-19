
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models.project as models
import schemas.project as schemas

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project=models.Project(name=project.name)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[schemas.ProjectResponse])
def read_projects(db:Session=Depends(get_db)):
    return db.query(models.Project).all()

@router.delete("/{project_id}")
def delete_project(project_id:int,db:Session=Depends(get_db)):
    project=db.query(models.Project).filter(models.Project.id==project_id).first()
    if not project:
        raise HTTPException(status_code=404,detail="Project not found")
    db.delete(project)
    db.commit()
    return {"ok":True}
