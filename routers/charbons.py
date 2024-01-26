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
    del charbon_dict["course"]
    return charbon_dict


def _get_charbon_query(db: Session):
    return db.query(models.Charbon).options(
        joinedload(models.Charbon.actionneurs), joinedload(models.Charbon.course)
    )


@router.get("/", response_model=List[schemas.Charbon])
def get_charbons(db: Session = Depends(get_db)):
    query = _get_charbon_query(db)
    charbons = [_transform_charbon(charbon) for charbon in query.all()]
    return charbons


@router.get("/{id}", response_model=schemas.Charbon)
def get_charbon_by_id(id: int, db: Session = Depends(get_db)):
    query = _get_charbon_query(db).filter_by(id=id)
    charbon = _transform_charbon(query.first())
    if not charbon:
        raise HTTPException(status_code=404, detail="Charbon not found")

    return charbon


@router.post("/", response_model=schemas.Charbon, status_code=status.HTTP_201_CREATED)
def add_charbon(charbon: schemas.CharbonCreate, db: Session = Depends(get_db)):
    charbon_dump = charbon.model_dump()
    if "actionneurs" in charbon_dump:
        del charbon_dump["actionneurs"]
    new_charbon = models.Charbon(**charbon_dump)

    if charbon.replay_link:
        video_id = extract_video_id_from_url(charbon.replay_link)
        duration = get_youtube_video_duration(video_id, settings.youtube_api_key)
        if duration is None:
            raise HTTPException(
                status_code=400, detail="Could not extract duration from video"
            )
        new_charbon.duration = duration
    else:
        new_charbon.duration = None

    db.add(new_charbon)
    db.flush()

    actionneurs = [
        models.CharbonHost(charbon_id=new_charbon.id, actionneur_id=actionneur)
        for actionneur in charbon.actionneurs
    ]

    db.add_all(actionneurs)

    db.commit()

    inserted_charbon = _get_charbon_query(db).filter_by(id=new_charbon.id).first()

    return _transform_charbon(inserted_charbon)


@router.put("/{id}", response_model=schemas.Charbon)
def update_charbon(
    id: int, charbon: schemas.CharbonCreate, db: Session = Depends(get_db)
):
    new_charbon = charbon.model_dump()
    if "actionneurs" in new_charbon:
        del new_charbon["actionneurs"]

    if charbon.replay_link:
        video_id = extract_video_id_from_url(charbon.replay_link)
        duration = get_youtube_video_duration(video_id, settings.youtube_api_key)
        if duration is None:
            raise HTTPException(
                status_code=400, detail="Could not extract duration from video"
            )
        new_charbon["duration"] = duration
    else:
        new_charbon.duration = None

    db.query(models.Charbon).filter_by(id=id).update(new_charbon)

    db.query(models.CharbonHost).filter_by(charbon_id=id).delete()
    actionneurs = [
        models.CharbonHost(charbon_id=id, actionneur_id=actionneur)
        for actionneur in charbon.actionneurs
    ]
    db.add_all(actionneurs)

    db.commit()

    inserted_charbon = _get_charbon_query(db).filter_by(id=id).first()

    return _transform_charbon(inserted_charbon)


@router.delete("/{id}")
def delete_charbon(id: int, db: Session = Depends(get_db)):
    db.query(models.Charbon).filter_by(id=id).delete()
    db.commit()

    return {}
