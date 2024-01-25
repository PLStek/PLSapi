from typing import List, Optional

from pydantic import BaseModel


class CharbonBase(BaseModel):
    title: str
    description: str
    datetime: int
    course_id: str
    replay_link: Optional[str]
    actionneurs: List[int]


class CharbonCreate(CharbonBase):
    pass


class Charbon(CharbonBase):
    id: int
    course_type: str
    duration: Optional[int]

    class Config:
        orm_mode = True


class Course(BaseModel):
    id: str
    type: str

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


class ExerciseTopicBase(BaseModel):
    topic: str
    course_id: str


class ExerciseTopicCreate(ExerciseTopicBase):
    pass


class ExerciseTopic(ExerciseTopicBase):
    course_type: str
    id: int

    class Config:
        orm_mode = True
