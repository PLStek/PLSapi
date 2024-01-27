from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db

router = APIRouter(prefix="/courses")


@router.get("/", response_model=List[schemas.Course])
def get_courses(db: Session = Depends(get_db)):
    query = db.query(models.Course)
    return query.all()


@router.get("/{id}", response_model=schemas.Course)
def get_course(id: str, db: Session = Depends(get_db)):
    query = db.query(models.Course).filter_by(id=id)
    course = query.first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


@router.post("/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
def add_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(**course.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.put("/{id}", response_model=schemas.Course)
def update_course(id: str, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db.query(models.Course).filter_by(id=id).update(course.model_dump())
    db.commit()
    return get_course(course.id, db)
