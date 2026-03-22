# app/modules/attendance/repository.py

from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from . import models


# ─────────────────────────────────────────────
#  AttendanceSession CRUD
# ─────────────────────────────────────────────

def create_attendance_session(db: Session, data: dict) -> models.AttendanceSession:
    obj = models.AttendanceSession(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_attendance_session_by_uuid(
    db: Session, uuid: str
) -> models.AttendanceSession | None:
    return (
        db.query(models.AttendanceSession)
        .options(
            joinedload(models.AttendanceSession.batch_session),
            joinedload(models.AttendanceSession.opener),
            joinedload(models.AttendanceSession.records)
            .joinedload(models.AttendanceRecord.student),
        )
        .filter(models.AttendanceSession.uuid == uuid)
        .first()
    )


def get_attendance_session_by_batch_session_id(
    db: Session, batch_session_id: int
) -> models.AttendanceSession | None:
    return (
        db.query(models.AttendanceSession)
        .filter(
            models.AttendanceSession.batch_session_id == batch_session_id
        )
        .order_by(models.AttendanceSession.opened_at.desc())
        .first()
    )


def get_open_session_by_pulse_code(
    db: Session, pulse_code: str
) -> models.AttendanceSession | None:
    return (
        db.query(models.AttendanceSession)
        .filter(
            models.AttendanceSession.pulse_code == pulse_code,
            models.AttendanceSession.is_open == True,
            models.AttendanceSession.pulse_expires_at > datetime.utcnow(),
        )
        .first()
    )


def list_attendance_sessions(
    db: Session,
    batch_id:         int | None = None,
    batch_session_id: int | None = None,
    is_open:          bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[models.AttendanceSession]:
    q = db.query(models.AttendanceSession).options(
        joinedload(models.AttendanceSession.batch_session),
        joinedload(models.AttendanceSession.opener),
    )
    if batch_session_id:
        q = q.filter(
            models.AttendanceSession.batch_session_id == batch_session_id
        )
    if is_open is not None:
        q = q.filter(models.AttendanceSession.is_open == is_open)
    return q.order_by(models.AttendanceSession.opened_at.desc()).offset(skip).limit(limit).all()


def close_attendance_session(
    db: Session, session: models.AttendanceSession
) -> models.AttendanceSession:
    session.is_open   = False
    session.closed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


# ─────────────────────────────────────────────
#  AttendanceRecord CRUD
# ─────────────────────────────────────────────

def get_record(
    db: Session,
    attendance_session_id: int,
    student_id: int,
) -> models.AttendanceRecord | None:
    return (
        db.query(models.AttendanceRecord)
        .filter(
            models.AttendanceRecord.attendance_session_id == attendance_session_id,
            models.AttendanceRecord.student_id == student_id,
        )
        .first()
    )


def create_record(db: Session, data: dict) -> models.AttendanceRecord:
    obj = models.AttendanceRecord(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_record(
    db: Session,
    record: models.AttendanceRecord,
    update: dict,
) -> models.AttendanceRecord:
    for k, v in update.items():
        setattr(record, k, v)
    db.commit()
    db.refresh(record)
    return record


def get_records_for_session(
    db: Session, attendance_session_id: int
) -> list[models.AttendanceRecord]:
    return (
        db.query(models.AttendanceRecord)
        .options(
            joinedload(models.AttendanceRecord.student),
            joinedload(models.AttendanceRecord.marker),
        )
        .filter(
            models.AttendanceRecord.attendance_session_id == attendance_session_id
        )
        .all()
    )


def get_records_for_student(
    db: Session, student_id: int, limit: int = 100
) -> list[models.AttendanceRecord]:
    return (
        db.query(models.AttendanceRecord)
        .options(
            joinedload(models.AttendanceRecord.attendance_session)
            .joinedload(models.AttendanceSession.batch_session),
        )
        .filter(models.AttendanceRecord.student_id == student_id)
        .order_by(models.AttendanceRecord.checked_in_at.desc())
        .limit(limit)
        .all()
    )


def count_records_by_status(
    db: Session, attendance_session_id: int
) -> dict:
    from sqlalchemy import func
    rows = (
        db.query(
            models.AttendanceRecord.status,
            func.count(models.AttendanceRecord.id).label("cnt"),
        )
        .filter(
            models.AttendanceRecord.attendance_session_id == attendance_session_id
        )
        .group_by(models.AttendanceRecord.status)
        .all()
    )
    return {r.status: r.cnt for r in rows}