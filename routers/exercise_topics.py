from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/exercise_topics")


@router.get("/", response_model=List[schemas.ExerciseTopic])
def get_exercise_topics(db: Session = Depends(get_db)):
    query = (
        db.query(models.ExerciseTopic)
        .join(models.Course, models.ExerciseTopic.course_id == models.Course.id)
        .all()
    )
    return query


@router.post("/", response_model=schemas.ExerciseTopic, status_code=201)
def add_exercise_topic(
    exercise_topic: schemas.ExerciseTopicCreate, db: Session = Depends(get_db)
):
    new_exercise_topic = models.ExerciseTopic(**exercise_topic.model_dump())
    db.add(new_exercise_topic)
    db.commit()
    db.refresh(new_exercise_topic)

    return new_exercise_topic
