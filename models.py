from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import relationship

from database import Base


class Charbon(Base):
    __tablename__ = "charbon"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    datetime = Column(Integer, nullable=False)
    course_id = Column(
        String(4),
        ForeignKey("course.id", onupdate="CASCADE"),
        nullable=False,
    )
    duration = Column(Integer)
    replay_link = Column(String(100))

    actionneurs = relationship(
        "CharbonHost", back_populates="charbon", cascade="all, delete"
    )
    course = relationship("Course", back_populates="charbons")


class Course(Base):
    __tablename__ = "course"
    id = Column(String(4), primary_key=True, nullable=False)
    type = Column(Enum("meca", "info", "elec", "math"), nullable=False)

    charbons = relationship("Charbon", back_populates="course")
    exercise_topics = relationship("ExerciseTopic", back_populates="course")


class CharbonHost(Base):
    __tablename__ = "charbon_host"
    charbon_id = Column(
        Integer,
        ForeignKey("charbon.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        nullable=False,
    )
    actionneur_id = Column(
        BigInteger,
        ForeignKey("actionneur.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        nullable=False,
    )

    charbon = relationship("Charbon", back_populates="actionneurs")
    actionneur = relationship("Actionneur", back_populates="charbons")


class Actionneur(Base):
    __tablename__ = "actionneur"
    id = Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)
    username = Column(String(50), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    charbons = relationship("CharbonHost", back_populates="actionneur")


class Announcement(Base):
    __tablename__ = "announcement"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(5000), nullable=False)
    datetime = Column(Integer, nullable=False)


class ExerciseTopic(Base):
    __tablename__ = "exercise_topic"
    id = Column(Integer, primary_key=True, nullable=False)
    topic = Column(String(100), nullable=False)
    course_id = Column(
        String(4), ForeignKey("course.id", onupdate="CASCADE"), nullable=False
    )

    course = relationship("Course", back_populates="exercise_topics")
    exercises = relationship("Exercise", back_populates="topic")


class Exercise(Base):
    __tablename__ = "exercise"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(100), nullable=False)
    difficulty = Column(Integer, nullable=False)
    is_corrected = Column(Boolean, nullable=False)
    source = Column(String(100), nullable=False)
    topic_id = Column(
        Integer,
        ForeignKey("exercise_topic.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    copyright = Column(Boolean, default=False, nullable=False)
    content = Column(LargeBinary, nullable=False)

    topic = relationship("ExerciseTopic", back_populates="exercises")
