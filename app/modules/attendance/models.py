# app/modules/attendance/models.py
"""
LUMINA PULSE Attendance System
─────────────────────────────────────────────────────────────────────
Flow:
  1. Trainer opens an AttendanceSession → system generates a 6-digit PULSE code
  2. Code is valid for a configurable window (default 15 min)
  3. Students self-check-in by submitting the code
  4. Trainer / Admin can manually mark / override any record
  5. AttendanceRecord stores every entry with source (self | trainer | admin)
─────────────────────────────────────────────────────────────────────
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class AttendanceSession(Base):
    """
    One AttendanceSession per class session.
    Holds the PULSE code and open/closed state.
    """
    __tablename__ = "attendance_sessions"

    id         = Column(Integer, primary_key=True, index=True)
    uuid       = Column(String(36), unique=True, index=True,
                        default=lambda: str(uuid.uuid4()))

    # Link to the scheduled class session
    batch_session_id = Column(Integer, ForeignKey("batch_sessions.id"),
                               nullable=False)

    # Who opened the pulse (trainer / admin)
    opened_by  = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 6-digit OTP students enter
    pulse_code = Column(String(10), nullable=False)

    # When the pulse window closes
    pulse_expires_at = Column(DateTime, nullable=False)

    # Whether students can currently check in
    is_open    = Column(Boolean, default=True, nullable=False)

    # Timestamps
    opened_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at  = Column(DateTime, nullable=True)

    # Optional note (e.g. "Late-start session")
    note       = Column(Text, nullable=True)

    # Relationships
    batch_session = relationship("BatchSession")
    opener        = relationship("User", foreign_keys=[opened_by])
    records       = relationship(
        "AttendanceRecord",
        back_populates="attendance_session",
        cascade="all, delete-orphan",
    )


class AttendanceRecord(Base):
    """
    One record per student per AttendanceSession.
    """
    __tablename__ = "attendance_records"

    id         = Column(Integer, primary_key=True, index=True)
    uuid       = Column(String(36), unique=True, index=True,
                        default=lambda: str(uuid.uuid4()))

    attendance_session_id = Column(
        Integer, ForeignKey("attendance_sessions.id"), nullable=False
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # present | absent | late | excused
    status     = Column(String(20), default="present", nullable=False)

    # self  → student used pulse code
    # trainer → manually marked by trainer
    # admin   → manually marked / overridden by admin
    marked_by_role = Column(String(20), default="self", nullable=False)

    # UUID of the user who made the entry (student or staff)
    marked_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    checked_in_at = Column(DateTime, nullable=True)
    note          = Column(Text, nullable=True)

    # Relationships
    attendance_session = relationship(
        "AttendanceSession", back_populates="records"
    )
    student  = relationship("User", foreign_keys=[student_id])
    marker   = relationship("User", foreign_keys=[marked_by_user_id])

