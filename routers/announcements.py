from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db

router = APIRouter(prefix="/announcements")


@router.get("/", response_model=List[schemas.Announcement])
def get_announcements(db: Session = Depends(get_db)):
    query = db.query(models.Announcement).all()
    return query


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

    return new_announcement


@router.put("/{id}")
def update_announcement(
    id: int, announcement: schemas.AnnouncementCreate, db: Session = Depends(get_db)
):
    db.query(models.Announcement).filter_by(id=id).update(announcement.model_dump())
    db.commit()

    return db.query(models.Announcement).filter_by(id=id).first()


@router.delete("/{id}")
def delete_announcement(id: int, db: Session = Depends(get_db)):
    db.query(models.Announcement).filter_by(id=id).delete()
    db.commit()

    return {}
