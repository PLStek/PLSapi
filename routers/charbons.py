from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db

router = APIRouter(prefix="/charbons")


def transform_charbon(charbon: models.Charbon) -> dict:
    charbon_dict = charbon.__dict__
    charbon_dict["actionneurs"] = [
        actionneur.actionneur.id for actionneur in charbon.actionneurs
    ]
    return charbon_dict


@router.get("/", response_model=List[schemas.Charbon])
def get_charbons(db: Session = Depends(get_db)):
    query = (
        db.query(models.Charbon).options(joinedload(models.Charbon.actionneurs)).all()
    )

    result = []
    for charbon in query:
        result.append(transform_charbon(charbon))
    return query


@router.get("/{id}", response_model=schemas.Charbon)
def get_charbon(id: int, db: Session = Depends(get_db)):
    query = (
        db.query(models.Charbon)
        .options(joinedload(models.Charbon.actionneurs))
        .filter(models.Charbon.id == id)
        .first()
    )

    return transform_charbon(query)


@router.post("/")
def add_charbon(charbon: schemas.CharbonCreate, db: Session = Depends(get_db)):
    new_charbon = models.Charbon(**charbon.model_dump())
    db.add(new_charbon)
    db.commit()
    db.refresh(new_charbon)

    return new_charbon


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
