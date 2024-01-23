from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Charbon(Base):
    __tablename__ = "charbon"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    datetime = Column(Integer)
    duration = Column(Integer)
    course_id = Column(String, ForeignKey("course.id"))
    actionneurs = relationship("CharbonHost", back_populates="charbon")


class Course(Base):
    __tablename__ = "course"
    id = Column(String, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("course_type.id"))


class CourseType(Base):
    __tablename__ = "course_type"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)


class CharbonHost(Base):
    __tablename__ = "charbon_host"
    charbon_id = Column(Integer, ForeignKey("charbon.id"), primary_key=True, index=True)
    actionneur_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)

    charbon = relationship("Charbon", back_populates="actionneurs")
    actionneur = relationship("User", back_populates="charbons")


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    actionneur = Column(Boolean)
    admin = Column(Boolean)

    charbons = relationship("CharbonHost", back_populates="actionneur")


class Announcement(Base):
    __tablename__ = "announcement"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    datetime = Column(Integer)
