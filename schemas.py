from typing import List, Optional

from pydantic import BaseModel


class CharbonBase(BaseModel):
    title: str
    description: str
    datetime: int
    duration: Optional[int]
    course_id: str


class CharbonCreate(CharbonBase):
    pass


class Charbon(CharbonBase):
    id: int
    actionneurs: List[int]

    class Config:
        orm_mode = True


class Course(BaseModel):
    id: str
    type_id: int

    class Config:
        orm_mode = True


class AnnouncementBase(BaseModel):
    title: str
    content: str
    datetime: int


class AnnouncementCreate(AnnouncementBase):
    pass


class Announcement(AnnouncementBase):
    id: int

    class Config:
        orm_mode = True
