import base64
import subprocess
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/exercises")


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
    process = subprocess.Popen(
        [
            "python3",
            "compile_plsmarkdown.py",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="compiler",
    )

    stdout, stderr = process.communicate(input=exercise.content.encode("utf-8"))
    if process.returncode == 0:
        new_exercise.content = base64.b64encode(stdout)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Could not compile exercise: {stderr.decode('utf-8')}",
        )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise
