# app/modules/attendance/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from typing import Generic, TypeVar

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data:    T


# ─────────────────────────────────────────────
#  Nested mini-schemas for display
# ─────────────────────────────────────────────
class UserMini(BaseModel):
    id:    int
    uuid:  str
    name:  str
    email: str

    class Config:
        from_attributes = True


class BatchSessionMini(BaseModel):
    id:             int
    uuid:           str
    title:          str
    session_number: int
    session_date:   str        # kept as str for easy JSON transport

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
#  AttendanceSession
# ─────────────────────────────────────────────
class AttendanceSessionOpen(BaseModel):
    """Trainer / admin sends this to open a pulse."""
    batch_session_uuid: str
    # minutes before the pulse window closes (1–60)
    window_minutes:     int = 15
    note:               Optional[str] = None


class AttendanceSessionResponse(BaseModel):
    id:              int
    uuid:            str
    pulse_code:      str
    is_open:         bool
    pulse_expires_at: datetime
    opened_at:       datetime
    closed_at:       Optional[datetime]
    note:            Optional[str]
    batch_session:   Optional[BatchSessionMini]
    opener:          Optional[UserMini]
    total_present:   int = 0
    total_absent:    int = 0
    total_late:      int = 0

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
#  AttendanceRecord
# ─────────────────────────────────────────────
class SelfCheckIn(BaseModel):
    """Student submits to check themselves in."""
    pulse_code: str          # the 6-digit code
    # student_uuid comes from the auth token in production;
    # kept here for dev/admin convenience
    student_uuid: Optional[str] = None


class ManualMark(BaseModel):
    """Trainer / admin manually marks a student."""
    student_uuid:  str
    status:        str   # present | absent | late | excused
    note:          Optional[str] = None


class BulkMark(BaseModel):
    """Mark all students in a batch session at once."""
    attendance_session_uuid: str
    student_uuids:           List[str]
    status:                  str   # present | absent | late | excused


class AttendanceRecordResponse(BaseModel):
    id:             int
    uuid:           str
    status:         str
    marked_by_role: str
    checked_in_at:  Optional[datetime]
    note:           Optional[str]
    student:        Optional[UserMini]
    marker:         Optional[UserMini]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
#  Report / summary
# ─────────────────────────────────────────────
class StudentAttendanceSummary(BaseModel):
    student:          UserMini
    total_sessions:   int
    present:          int
    absent:           int
    late:             int
    excused:          int
    attendance_pct:   float


class SessionAttendanceReport(BaseModel):
    attendance_session: AttendanceSessionResponse
    records:            List[AttendanceRecordResponse]