# app/modules/analytics/schemas.py
"""
Dashboard schemas — one response shape per role.
All three dashboards are served from this single analytics module.
"""

from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional, List, Generic, TypeVar

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data:    T


# ──────────────────────────────────────────
#  Shared mini-shapes
# ──────────────────────────────────────────

class UserMini(BaseModel):
    id:   int
    uuid: str
    name: str
    email: str

    class Config:
        from_attributes = True


class CourseMini(BaseModel):
    id:    int
    uuid:  str
    title: str
    level: Optional[str]

    class Config:
        from_attributes = True


class BatchMini(BaseModel):
    id:         int
    uuid:       str
    name:       str
    status:     str
    start_date: Optional[date]
    end_date:   Optional[date]
    course:     Optional[CourseMini]

    class Config:
        from_attributes = True


class UpcomingSession(BaseModel):
    uuid:           str
    title:          str
    session_number: int
    session_date:   date
    start_time:     Optional[time]
    end_time:       Optional[time]
    status:         str
    meeting_link:   Optional[str]
    batch_name:     Optional[str]
    course_title:   Optional[str]

    class Config:
        from_attributes = True


class AttendanceStat(BaseModel):
    total:   int
    present: int
    absent:  int
    late:    int
    pct:     float   # percentage present+late / total


# ──────────────────────────────────────────
#  TRAINER Dashboard
# ──────────────────────────────────────────

class TrainerBatchSummary(BaseModel):
    batch:           BatchMini
    student_count:   int
    session_count:   int
    completed_sessions: int
    progress_pct:    float
    attendance_avg:  float


class TrainerDashboard(BaseModel):
    trainer:              UserMini
    total_batches:        int
    active_batches:       int
    total_students:       int
    total_sessions:       int
    sessions_today:       int
    upcoming_sessions:    List[UpcomingSession]   # next 5
    batch_summaries:      List[TrainerBatchSummary]
    overall_attendance:   AttendanceStat
    recent_sessions:      List[UpcomingSession]   # last 5 completed


# ──────────────────────────────────────────
#  STUDENT Dashboard
# ──────────────────────────────────────────

class StudentCourseProgress(BaseModel):
    batch:             BatchMini
    sessions_attended: int
    total_sessions:    int
    attendance_pct:    float
    last_session_date: Optional[date]


class StudentDashboard(BaseModel):
    student:              UserMini
    enrolled_batches:     int
    sessions_attended:    int
    total_sessions:       int
    attendance_pct:       float
    course_progress:      List[StudentCourseProgress]
    upcoming_sessions:    List[UpcomingSession]
    recent_attendance:    List[dict]   # last 10 attendance records


# ──────────────────────────────────────────
#  ADMIN Dashboard
# ──────────────────────────────────────────

class AdminDashboard(BaseModel):
    total_students:     int
    total_trainers:     int
    total_courses:      int
    total_batches:      int
    active_batches:     int
    sessions_today:     int
    overall_attendance: AttendanceStat
    revenue_collected:  float
    revenue_pending:    float
    recent_users:       List[UserMini]   # last 10 registered
    upcoming_sessions:  List[UpcomingSession]