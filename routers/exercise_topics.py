from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload

import models
import schemas
from database import get_db

router = APIRouter(prefix="/exercise_topics")


def _transform_et(et: models.ExerciseTopic) -> Dict[str, Any]:
    et_dict: Dict[str, Any] = et.__dict__
    et_dict["course_type"] = et.course.type
    del et_dict["course"]
    return et_dict


@router.get("/")
def get_exercise_topics(db: Session = Depends(get_db)):
    query = db.query(models.ExerciseTopic).options(
        joinedload(models.ExerciseTopic.course)
    )
    return [_transform_et(et) for et in query.all()]


@router.get("/{id}")
def get_exercise_topic(id: int, db: Session = Depends(get_db)):
    query = (
        db.query(models.ExerciseTopic)
        .options(selectinload(models.ExerciseTopic.course))
        .filter(models.ExerciseTopic.id == id)
    )
    et = _transform_et(query.first())
    if not et:
        raise HTTPException(status_code=404, detail="Exercise topic not found")

    return et


@router.post("/", response_model=schemas.ExerciseTopic, status_code=201)
def add_exercise_topic(et: schemas.ExerciseTopicCreate, db: Session = Depends(get_db)):
    new_et = models.ExerciseTopic(**et.model_dump())
    db.add(new_et)
    db.commit()
    db.refresh(new_et)

    return new_et
