from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Time, DateTime
from sqlalchemy.orm import relationship
import uuid
from app.database.base import Base


class BatchSession(Base):

    __tablename__ = "batch_sessions"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    batch_id = Column(Integer, ForeignKey("batches.id"))

    trainer_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String(200))

    session_number = Column(Integer)

    session_date = Column(Date)

    start_time = Column(Time)

    end_time = Column(Time)

    meeting_link = Column(Text)

    recording_link = Column(Text)

    status = Column(String(50), default="scheduled")

    batch = relationship("Batch")

    trainer = relationship("User")

    attendances = relationship("SessionAttendance", back_populates="session")

    resources = relationship("SessionResource", back_populates="session")


class SessionAttendance(Base):

    __tablename__ = "session_attendance"

    id = Column(Integer, primary_key=True)

    session_id = Column(Integer, ForeignKey("batch_sessions.id"))

    student_id = Column(Integer, ForeignKey("users.id"))

    status = Column(String(20))

    joined_at = Column(DateTime)

    left_at = Column(DateTime)

    session = relationship("BatchSession", back_populates="attendances")

    student = relationship("User")


class SessionResource(Base):

    __tablename__ = "session_resources"

    id = Column(Integer, primary_key=True)

    session_id = Column(Integer, ForeignKey("batch_sessions.id"))

    title = Column(String(200))

    resource_type = Column(String(50))

    url = Column(Text)

    session = relationship("BatchSession", back_populates="resources")