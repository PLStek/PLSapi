from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from config import settings
from database import get_db
from utils import extract_video_id_from_url, get_youtube_video_duration

router = APIRouter(prefix="/charbons")


class SortOptions(str, Enum):
    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    DURATION_ASC = "duration_asc"
    DURATION_DESC = "duration_desc"

    def get_sort_option(self):
        options = {
            SortOptions.DATE_ASC: models.Charbon.datetime.asc(),
            SortOptions.DATE_DESC: models.Charbon.datetime.desc(),
            SortOptions.DURATION_ASC: models.Charbon.duration.asc(),
            SortOptions.DURATION_DESC: models.Charbon.duration.desc(),
        }
        return options.get(self, models.Charbon.datetime.desc())


def _transform_charbon(charbon: models.Charbon) -> Dict[str, Any]:
    charbon_dict: Dict[str, Any] = charbon.__dict__
    charbon_dict["actionneurs"] = [
        actionneur.actionneur.id for actionneur in charbon.actionneurs
    ]
    charbon_dict["course_type"] = charbon.course.type
    charbon_dict.pop("course", None)
    return charbon_dict


@router.get("/", response_model=List[schemas.Charbon])
def get_charbons(
    limit: int = 10,
    offset: int = 0,
    course_type: Optional[schemas.CourseType] = None,
    course: str | None = None,
    sort: Optional[SortOptions] = SortOptions.DATE_DESC,
    min_date: Optional[int] = None,
    max_date: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Charbon)
        .join(models.Course)
        .options(
            joinedload(models.Charbon.actionneurs), joinedload(models.Charbon.course)
        )
        .order_by(sort.get_sort_option())
    )
    if course_type:
        query = query.filter(models.Course.type == course_type)
    if course:
        query = query.filter(models.Charbon.course_id == course)
    if min_date:
        query = query.filter(models.Charbon.datetime >= min_date)
    if max_date:
        query = query.filter(models.Charbon.datetime <= max_date)
    query = query.offset(offset).limit(limit)

    charbons = [_transform_charbon(charbon) for charbon in query.all()]
    return charbons


@router.get("/{id}", response_model=schemas.Charbon)
def get_charbon(id: int, db: Session = Depends(get_db)):
    query = (
        db.query(models.Charbon)
        .options(
            joinedload(models.Charbon.actionneurs), joinedload(models.Charbon.course)
        )
        .filter_by(id=id)
    )
    charbon = _transform_charbon(query.first())
    if not charbon:
        raise HTTPException(status_code=404, detail="Charbon not found")

    return charbon


@router.post("/", response_model=schemas.Charbon, status_code=status.HTTP_201_CREATED)
def add_charbon(charbon: schemas.CharbonCreate, db: Session = Depends(get_db)):
    charbon_dump = charbon.model_dump()
    charbon_dump.pop("actionneurs")
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

    return get_charbon(new_charbon.id, db)


@router.put("/{id}", response_model=schemas.Charbon)
def update_charbon(
    id: int, charbon: schemas.CharbonCreate, db: Session = Depends(get_db)
):
    new_charbon = charbon.model_dump()
    new_charbon.pop("actionneurs", None)

    if charbon.replay_link:
        video_id = extract_video_id_from_url(charbon.replay_link)
        duration = get_youtube_video_duration(video_id, settings.youtube_api_key)
        if duration is None:
            raise HTTPException(
                status_code=400, detail="Could not extract duration from video"
            )
        new_charbon["duration"] = duration
    else:
        new_charbon["duration"] = None

    db.query(models.Charbon).filter_by(id=id).update(new_charbon)
    db.query(models.CharbonHost).filter_by(charbon_id=id).delete()
    actionneurs = [
        models.CharbonHost(charbon_id=id, actionneur_id=actionneur)
        for actionneur in charbon.actionneurs
    ]
    db.add_all(actionneurs)
    db.commit()

    return get_charbon(id, db)


@router.delete("/{id}")
def delete_charbon(id: int, db: Session = Depends(get_db)):
    db.query(models.Charbon).filter_by(id=id).delete()
    db.commit()

    return {}
