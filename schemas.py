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
        from_attributes = True


class CourseBase(BaseModel):
    id: str
    type: str


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    class Config:
        from_attributes = True


class AnnouncementBase(BaseModel):
    title: str
    content: str
    datetime: int


class AnnouncementCreate(AnnouncementBase):
    pass


class Announcement(AnnouncementBase):
    id: int

    class Config:
        from_attributes = True


class ExerciseTopicBase(BaseModel):
    topic: str
    course_id: str


class ExerciseTopicCreate(ExerciseTopicBase):
    pass


class ExerciseTopic(ExerciseTopicBase):
    course_type: CourseType
    id: int

    class Config:
        from_attributes = True


class ExerciseBase(BaseModel):
    title: str
    difficulty: int
    is_corrected: bool
    source: str
    topic_id: int
    copyright: bool


class ExerciseCreate(ExerciseBase):
    content: Base64Str

    pass


class Exercise(ExerciseBase):
    id: int
    content: Optional[str]

    class Config:
        from_attributes = True


class Actionneur(BaseModel):
    id: int


class User(BaseModel):
    id: int
    is_actionneur: bool
    is_admin: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    login: str
    password: str


class UserChangePassword(BaseModel):
    password: str
    new_password: str


class DiscordUser(BaseModel):
    id: int
    global_name: str


class TokenCreate(BaseModel):
    code: str


class TokenData(BaseModel):
    token: str
    exp_time: int
