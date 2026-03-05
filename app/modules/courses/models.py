import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Course(Base):

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    title = Column(String(200), nullable=False)

    slug = Column(String(200), unique=True)

    description = Column(Text)

    level = Column(String(50))  # beginner / intermediate / advanced

    duration = Column(String(50))

    thumbnail = Column(String(300))  # course image URL

    category = Column(String(100))

    is_active = Column(String(10), default="true")

    prices = relationship("CoursePrice", back_populates="course")


class CoursePrice(Base):

    __tablename__ = "course_prices"

    id = Column(Integer, primary_key=True)

    course_id = Column(Integer, ForeignKey("courses.id"))

    country = Column(String(100))

    currency = Column(String(10))

    price = Column(Float)

    course = relationship("Course", back_populates="prices")