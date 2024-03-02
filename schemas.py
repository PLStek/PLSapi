from enum import Enum
from typing import List, Optional

from pydantic import Base64Str, BaseModel, validator


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
    actionneurs: List[str]

    @validator("actionneurs", pre=True)
    def actionneurs_to_str(cls, v):
        return [str(a) for a in v] if isinstance(v, list) else v


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


class ActionneurCreate(BaseModel):
    id: str
    username: str

    @validator("id", pre=True)
    def id_to_str(cls, v):
        return str(v) if isinstance(v, int) else v


class Actionneur(ActionneurCreate):
    is_admin: bool

    class Config:
        from_attributes = True


class User(BaseModel):
    id: str
    is_actionneur: bool
    is_admin: bool

    class Config:
        from_attributes = True


class DiscordUser(BaseModel):
    id: str
    global_name: str


class TokenCreate(BaseModel):
    code: str
    redirect_uri: str


class TokenData(BaseModel):
    token: str
    exp_time: int
