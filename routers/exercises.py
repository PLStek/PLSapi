import base64
import subprocess
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

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


@router.get("/", response_model=List[schemas.Exercise])
def get_exercises(db: Session = Depends(get_db)):
    query = db.query(models.Exercise)
    return query.all()


@router.get("/{id}", response_model=schemas.Exercise)
def get_exercise(id: int, db: Session = Depends(get_db)):
    query = db.query(models.Exercise).filter_by(id=id)
    exercise = query.first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    exercise.content = base64.b64decode(exercise.content).decode("utf-8")
    return exercise


@router.post("/", response_model=schemas.Exercise, status_code=status.HTTP_201_CREATED)
def add_exercise(
    exercise: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
):
    new_exercise = models.Exercise(**exercise.model_dump())
    compiled_content_bytes = _compile_content(exercise.content).encode("utf-8")
    new_exercise.content = base64.b64encode(compiled_content_bytes)
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise
