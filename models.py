from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from database import Base


class Charbon(Base):
    __tablename__ = "charbon"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(500))
    datetime = Column(Integer)
    course_id = Column(String(4), ForeignKey("course.id"))
    duration = Column(Integer, nullable=True)
    replay_link = Column(String(100), nullable=True)

    actionneurs = relationship("CharbonHost", back_populates="charbon")
    course = relationship("Course", back_populates="charbons")


class Course(Base):
    __tablename__ = "course"
    id = Column(String(4), primary_key=True, index=True)
    type = Column(Enum("meca", "info", "elec", "math"))

    charbons = relationship("Charbon", back_populates="course")
    exercise_topics = relationship("ExerciseTopic", back_populates="course")


class CharbonHost(Base):
    __tablename__ = "charbon_host"
    charbon_id = Column(Integer, ForeignKey("charbon.id"), primary_key=True, index=True)
    actionneur_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)

    charbon = relationship("Charbon", back_populates="actionneurs")
    actionneur = relationship("User", back_populates="charbons")


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    email = Column(String(100))
    password_hash = Column(String(100))
    is_actionneur = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    charbons = relationship("CharbonHost", back_populates="actionneur")


class Announcement(Base):
    __tablename__ = "announcement"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(5000))
    datetime = Column(Integer)


class ExerciseTopic(Base):
    __tablename__ = "exercise_topic"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100))
    course_id = Column(String(4), ForeignKey("course.id"))

    course = relationship("Course", back_populates="exercise_topics")
    exercises = relationship("Exercise", back_populates="topic")


class Exercise(Base):
    __tablename__ = "exercise"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    difficulty = Column(Integer)
    is_corrected = Column(Boolean)
    source = Column(String(100))
    topic_id = Column(Integer, ForeignKey("exercise_topic.id"))
    content = Column(LargeBinary)

    topic = relationship("ExerciseTopic", back_populates="exercises")
