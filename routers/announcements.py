from enum import Enum
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db

router = APIRouter(prefix="/announcements")


class SortOptions(str, Enum):
    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"

    def get_sort_option(self):
        options = {
            SortOptions.DATE_ASC: models.Announcement.datetime.asc(),
            SortOptions.DATE_DESC: models.Announcement.datetime.desc(),
            SortOptions.NAME_ASC: models.Announcement.title.asc(),
            SortOptions.NAME_DESC: models.Announcement.title.desc(),
        }
        return options.get(self, models.Announcement.datetime.desc())


@router.get("/", response_model=List[schemas.Announcement])
def get_announcements(
    limit: int = 10,
    offset: int = 0,
    sort: SortOptions = SortOptions.DATE_DESC,
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Announcement)
        .order_by(sort.get_sort_option())
        .limit(limit)
        .offset(offset)
    )
    return query.all()


@router.get("/{id}", response_model=schemas.Announcement)
def get_announcement(id: int, db: Session = Depends(get_db)):
    query = db.query(models.Announcement).filter_by(id=id).first()

    return query


@router.post("/")
def add_announcement(
    announcement: schemas.AnnouncementCreate, db: Session = Depends(get_db)
):
    new_announcement = models.Announcement(**announcement.model_dump())
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)

    return get_announcement(new_announcement.id, db)


@router.put("/{id}")
def update_announcement(
    id: int, announcement: schemas.AnnouncementCreate, db: Session = Depends(get_db)
):
    db.query(models.Announcement).filter_by(id=id).update(announcement.model_dump())
    db.commit()

    return get_announcement(id, db)


@router.delete("/{id}")
def delete_announcement(id: int, db: Session = Depends(get_db)):
    db.query(models.Announcement).filter_by(id=id).delete()
    db.commit()

    return {}
