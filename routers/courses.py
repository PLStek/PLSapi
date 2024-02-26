from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

import models
import schemas
from database import get_db
from oauth import get_current_admin

router = APIRouter(prefix="/courses")


@router.get("/", response_model=List[schemas.Course])
def get_courses(db: Session = Depends(get_db)):
    try:
        query = db.query(models.Course)
        return query.all()
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/{id}/", response_model=schemas.Course)
def get_course(id: str, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Course).filter_by(id=id)
        course = query.first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
def add_course(
    course: schemas.CourseCreate,
    admin: Annotated[models.Actionneur, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    try:
        new_course = models.Course(**course.model_dump())
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return new_course
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/{id}/", response_model=schemas.Course)
def update_course(
    id: str,
    course: schemas.CourseCreate,
    admin: Annotated[models.Actionneur, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    try:
        updated_rows = (
            db.query(models.Course).filter_by(id=id).update(course.model_dump())
        )
        db.commit()
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        return get_course(id, db)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
