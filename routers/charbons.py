from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from config import settings
from database import get_db
from utils import extract_video_id_from_url, get_youtube_video_duration

router = APIRouter(prefix="/charbons")


def _transform_charbon(charbon: models.Charbon) -> Dict[str, Any]:
    charbon_dict: Dict[str, Any] = charbon.__dict__
    charbon_dict["actionneurs"] = [
        actionneur.actionneur.id for actionneur in charbon.actionneurs
    ]
    charbon_dict["course_type"] = charbon.course.type
    return charbon_dict


def _get_charbon_query(db: Session):
    return (
        db.query(models.Charbon)
        .options(joinedload(models.Charbon.actionneurs))
        .join(models.Course, models.Charbon.course_id == models.Course.id)
    )


@router.get("/", response_model=List[schemas.Charbon])
def get_charbons(db: Session = Depends(get_db)):
    query = _get_charbon_query(db).all()

    return [_transform_charbon(charbon) for charbon in query]


@router.get("/{id}", response_model=schemas.Charbon)
def get_charbon_by_id(id: int, db: Session = Depends(get_db)):
    query = _get_charbon_query(db).filter(models.Charbon.id == id).first()

    if not query:
        raise HTTPException(status_code=404, detail="Charbon not found")

    return _transform_charbon(query)


@router.post("/", response_model=schemas.Charbon, status_code=status.HTTP_201_CREATED)
def add_charbon(charbon: schemas.CharbonCreate, db: Session = Depends(get_db)):
    video_id = extract_video_id_from_url(charbon.replay_link)
    duration = get_youtube_video_duration(video_id, settings.youtube_api_key)

    new_charbon = models.Charbon(**charbon.model_dump())
    new_charbon.duration = duration

    db.add(new_charbon)
    db.commit()

    inserted_charbon = (
        _get_charbon_query(db).filter(models.Charbon.id == new_charbon.id).first()
    )

    return _transform_charbon(inserted_charbon)


@router.put("/{id}")
def update_charbon(
    id: int, charbon: schemas.CharbonCreate, db: Session = Depends(get_db)
):
    db.query(models.Charbon).filter(models.Charbon.id == id).update(
        charbon.model_dump()
    )
    db.commit()

    return db.query(models.Charbon).filter(models.Charbon.id == id).first()


@router.delete("/{id}")
def delete_charbon(id: int, db: Session = Depends(get_db)):
    db.query(models.Charbon).filter(models.Charbon.id == id).delete()
    db.commit()

    return {}
