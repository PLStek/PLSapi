import base64
from enum import Enum
from typing import List, Optional

from pydantic import Base64Str, BaseModel


class CourseType(str, Enum):
    MECA = "meca"
    ELEC = "elec"
    INFO = "info"
    MATH = "math"


class CharbonBase(BaseModel):
    title: str
    description: str
    datetime: int
    course_id: str
    replay_link: Optional[str] = None
    actionneurs: List[int]


class CharbonCreate(CharbonBase):
    pass


class Charbon(CharbonBase):
    id: int
    course_type: CourseType
    duration: Optional[int] = None

    class Config:
        orm_mode = True


class CourseBase(BaseModel):
    id: str
    type: str


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
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
    course_type: CourseType
    id: int

    class Config:
        orm_mode = True


class ExerciseBase(BaseModel):
    title: str
    difficulty: int
    is_corrected: bool
    source: str
    topic_id: int


class ExerciseCreate(ExerciseBase):
    content: Base64Str

    pass


class Exercise(ExerciseBase):
    id: int
    content: Optional[str]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_actionneur: bool
    is_admin: bool


class UserLogin(BaseModel):
    login: str
    password: str
