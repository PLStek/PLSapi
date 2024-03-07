from typing import Annotated, Any, Dict, List

from discord_auth import get_current_actionneur
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, joinedload, selectinload

import models
import schemas
from database import get_db

router = APIRouter(prefix="/exercise_topics", tags=["Exercise topics"])


def _transform_et(et: models.ExerciseTopic) -> Dict[str, Any]:
    et_dict: Dict[str, Any] = et.__dict__
    et_dict["course_type"] = et.course.type
    del et_dict["course"]
    return et_dict


@router.get("/")
def get_exercise_topics(db: Session = Depends(get_db)):
    try:
        query = db.query(models.ExerciseTopic).options(
            joinedload(models.ExerciseTopic.course)
        )
        return [_transform_et(et) for et in query.all()]
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/{id}/")
def get_exercise_topic(id: int, db: Session = Depends(get_db)):
    try:
        query = (
            db.query(models.ExerciseTopic)
            .options(selectinload(models.ExerciseTopic.course))
            .filter_by(id=id)
        )
        et = _transform_et(query.first())
        if not et:
            raise HTTPException(status_code=404, detail="Exercise topic not found")
        return et
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/", response_model=schemas.ExerciseTopic, status_code=201)
def add_exercise_topic(
    et: schemas.ExerciseTopicCreate,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        new_et = models.ExerciseTopic(**et.model_dump())
        db.add(new_et)
        db.commit()
        db.refresh(new_et)
        return get_exercise_topic(new_et.id, db)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/{id}/")
def update_exercise_topic(
    id: int,
    et: schemas.ExerciseTopicCreate,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        updated_rows = (
            db.query(models.ExerciseTopic).filter_by(id=id).update(et.model_dump())
        )
        db.commit()
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Exercise topic not found")
        return get_exercise_topic(id, db)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/{id}/")
def delete_exercise_topic(
    id: int,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        deleted_rows = db.query(models.ExerciseTopic).filter_by(id=id).delete()
        db.commit()
        if deleted_rows == 0:
            raise HTTPException(status_code=404, detail="Exercise topic not found")
        return {}
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
