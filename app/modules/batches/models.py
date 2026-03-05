import uuid
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


class Batch(Base):

    __tablename__ = "batches"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    course_id = Column(Integer, ForeignKey("courses.id"))

    trainer_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String(120))

    start_date = Column(Date)

    end_date = Column(Date)

    schedule = Column(String(100))

    timezone = Column(String(100))

    status = Column(String(50), default="upcoming")

    course = relationship("Course")

    trainer = relationship("User")

    students = relationship("BatchStudent", back_populates="batch")

class BatchStudent(Base):

    __tablename__ = "batch_students"

    id = Column(Integer, primary_key=True)

    batch_id = Column(Integer, ForeignKey("batches.id"))

    student_id = Column(Integer, ForeignKey("users.id"))

    batch = relationship("Batch", back_populates="students")

    student = relationship("User")