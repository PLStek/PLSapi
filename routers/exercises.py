import base64
import subprocess
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from oauth import get_current_actionneur, get_current_user

router = APIRouter(prefix="/exercises")

COMPILER_COMMAND = ["python3", "compile_plsmarkdown.py"]
COMPILER_DIRECTORY = "compiler"


def _compile_content(content: str) -> str:
    process = subprocess.run(
        COMPILER_COMMAND,
        input=content.encode("utf-8"),
        capture_output=True,
        cwd=COMPILER_DIRECTORY,
        check=True,
    )
    return process.stdout.decode("utf-8")


# TODO: dont request content from db
@router.get("/", response_model=List[schemas.Exercise])
def get_exercises(topic_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Exercise)
        if topic_id:
            query = query.filter_by(topic_id=topic_id)
        return query.all()
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/{id}", response_model=schemas.Exercise)
def get_exercise(
    id: int,
    user: Annotated[int, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        exercise = db.query(models.Exercise).get(id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        if exercise.copyright and user is None:
            raise HTTPException(
                status_code=401,
                detail="You need a valid token to access this exercise",
            )
        return exercise
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/", response_model=schemas.Exercise, status_code=status.HTTP_201_CREATED)
def add_exercise(
    exercise: schemas.ExerciseCreate,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        new_exercise = models.Exercise(**exercise.model_dump())
        compiled_content_bytes = _compile_content(exercise.content).encode("utf-8")
        new_exercise.content = base64.b64encode(compiled_content_bytes)
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        return new_exercise
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/{id}", response_model=schemas.Exercise)
def update_exercise(
    id: int,
    exercise: schemas.ExerciseCreate,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        new_exercise = exercise.model_dump()
        if exercise.content:
            compiled_content_bytes = _compile_content(exercise.content).encode("utf-8")
            new_exercise["content"] = base64.b64encode(compiled_content_bytes)

        updated_rows = db.query(models.Exercise).filter_by(id=id).update(new_exercise)
        db.commit()
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return get_exercise(id, db)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
