from enum import Enum
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

import models
import schemas
from database import get_db
from oauth import get_current_actionneur

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
    try:
        query = (
            db.query(models.Announcement)
            .order_by(sort.get_sort_option())
            .limit(limit)
            .offset(offset)
        )
        return query.all()
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/{id}/", response_model=schemas.Announcement)
def get_announcement(id: int, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Announcement).filter_by(id=id).one()
        return query
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Announcement not found")
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/")
def add_announcement(
    announcement: schemas.AnnouncementCreate,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        new_announcement = models.Announcement(**announcement.model_dump())
        db.add(new_announcement)
        db.commit()
        db.refresh(new_announcement)
        return get_announcement(new_announcement.id, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Announcement already exists or violates a constraint",
        )
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/{id}/")
def update_announcement(
    id: int,
    announcement: schemas.AnnouncementCreate,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        ann = db.query(models.Announcement).filter_by(id=id).one()
        ann.update(announcement.model_dump())
        db.commit()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Announcement not found")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error, check your data")
    return get_announcement(id, db)


@router.delete("/{id}/")
def delete_announcement(
    id: int,
    actionneur: Annotated[models.Actionneur, Depends(get_current_actionneur)],
    db: Session = Depends(get_db),
):
    try:
        ann = db.query(models.Announcement).filter_by(id=id).one()
        db.delete(ann)
        db.commit()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {}
