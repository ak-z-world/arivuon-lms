# app/modules/attendance/service.py

import random
import string
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import repository, schemas
from app.modules.sessions.repository import get_session_by_uuid
from app.modules.users.repository    import get_user_by_uuid


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _generate_pulse_code(length: int = 6) -> str:
    """Alphanumeric upper-case OTP, easy to read/type."""
    chars = string.ascii_uppercase + string.digits
    # Remove ambiguous chars (0 O I 1 L)
    chars = chars.replace("0","").replace("O","").replace("I","").replace("1","").replace("L","")
    return "".join(random.choices(chars, k=length))


def _build_session_response(
    db: Session,
    att_session,
) -> schemas.AttendanceSessionResponse:
    counts = repository.count_records_by_status(db, att_session.id)
    bs = att_session.batch_session
    bs_mini = None
    if bs:
        bs_mini = schemas.BatchSessionMini(
            id=bs.id, uuid=bs.uuid, title=bs.title,
            session_number=bs.session_number,
            session_date=str(bs.session_date),
        )
    opener_mini = None
    if att_session.opener:
        opener_mini = schemas.UserMini(
            id=att_session.opener.id, uuid=att_session.opener.uuid,
            name=att_session.opener.name, email=att_session.opener.email,
        )
    return schemas.AttendanceSessionResponse(
        id=att_session.id, uuid=att_session.uuid,
        pulse_code=att_session.pulse_code,
        is_open=att_session.is_open,
        pulse_expires_at=att_session.pulse_expires_at,
        opened_at=att_session.opened_at,
        closed_at=att_session.closed_at,
        note=att_session.note,
        batch_session=bs_mini,
        opener=opener_mini,
        total_present=counts.get("present", 0),
        total_absent=counts.get("absent", 0),
        total_late=counts.get("late", 0),
    )


# ─────────────────────────────────────────────
#  Open a Pulse (trainer / admin)
# ─────────────────────────────────────────────

def open_attendance_session(
    db: Session,
    payload: schemas.AttendanceSessionOpen,
    opened_by_uuid: str,
) -> schemas.AttendanceSessionResponse:

    batch_session = get_session_by_uuid(db, payload.batch_session_uuid)
    if not batch_session:
        raise HTTPException(status_code=404, detail="Batch session not found")

    opener = get_user_by_uuid(db, opened_by_uuid)
    if not opener:
        raise HTTPException(status_code=404, detail="Opener user not found")

    # Clamp window to 1–60 minutes
    minutes = max(1, min(60, payload.window_minutes))

    att = repository.create_attendance_session(db, {
        "batch_session_id": batch_session.id,
        "opened_by":        opener.id,
        "pulse_code":       _generate_pulse_code(),
        "pulse_expires_at": datetime.utcnow() + timedelta(minutes=minutes),
        "is_open":          True,
        "note":             payload.note,
    })

    # Reload with relationships
    att = repository.get_attendance_session_by_uuid(db, att.uuid)
    return _build_session_response(db, att)


# ─────────────────────────────────────────────
#  Close a Pulse
# ─────────────────────────────────────────────

def close_attendance_session(
    db: Session, att_uuid: str
) -> schemas.AttendanceSessionResponse:

    att = repository.get_attendance_session_by_uuid(db, att_uuid)
    if not att:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    att = repository.close_attendance_session(db, att)
    return _build_session_response(db, att)


# ─────────────────────────────────────────────
#  Student self-check-in
# ─────────────────────────────────────────────

def self_checkin(
    db: Session,
    att_session_uuid: str,
    student_uuid: str,
    pulse_code: str,
) -> schemas.AttendanceRecordResponse:

    att = repository.get_attendance_session_by_uuid(db, att_session_uuid)
    if not att:
        raise HTTPException(status_code=404, detail="Attendance session not found")
    if not att.is_open:
        raise HTTPException(status_code=400, detail="Attendance window is closed")
    if datetime.utcnow() > att.pulse_expires_at:
        raise HTTPException(status_code=400, detail="PULSE code has expired")
    if pulse_code.upper() != att.pulse_code:
        raise HTTPException(status_code=400, detail="Invalid PULSE code")

    student = get_user_by_uuid(db, student_uuid)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Idempotent — if already checked in, return existing record
    existing = repository.get_record(db, att.id, student.id)
    if existing:
        # Upgrade absent → present if they finally showed up
        if existing.status in ("absent", "late"):
            existing = repository.update_record(db, existing, {
                "status": "late" if existing.status == "absent" else existing.status,
                "checked_in_at": datetime.utcnow(),
            })
        return _record_response(existing)

    record = repository.create_record(db, {
        "attendance_session_id": att.id,
        "student_id":            student.id,
        "status":                "present",
        "marked_by_role":        "self",
        "marked_by_user_id":     student.id,
        "checked_in_at":         datetime.utcnow(),
    })
    return _record_response(record)


# ─────────────────────────────────────────────
#  Trainer / Admin manual mark
# ─────────────────────────────────────────────

def manual_mark(
    db: Session,
    att_session_uuid: str,
    payload: schemas.ManualMark,
    marker_uuid: str,
    marker_role: str,
) -> schemas.AttendanceRecordResponse:

    att = repository.get_attendance_session_by_uuid(db, att_session_uuid)
    if not att:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    student = get_user_by_uuid(db, payload.student_uuid)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    marker = get_user_by_uuid(db, marker_uuid)
    if not marker:
        raise HTTPException(status_code=404, detail="Marker not found")

    if payload.status not in ("present", "absent", "late", "excused"):
        raise HTTPException(status_code=422, detail="Invalid status value")

    existing = repository.get_record(db, att.id, student.id)
    if existing:
        record = repository.update_record(db, existing, {
            "status":            payload.status,
            "marked_by_role":    marker_role,
            "marked_by_user_id": marker.id,
            "note":              payload.note,
            "checked_in_at":     datetime.utcnow(),
        })
    else:
        record = repository.create_record(db, {
            "attendance_session_id": att.id,
            "student_id":            student.id,
            "status":                payload.status,
            "marked_by_role":        marker_role,
            "marked_by_user_id":     marker.id,
            "note":                  payload.note,
            "checked_in_at":         datetime.utcnow(),
        })
    return _record_response(record)


# ─────────────────────────────────────────────
#  Bulk mark (trainer marks everyone at once)
# ─────────────────────────────────────────────

def bulk_mark(
    db: Session,
    payload: schemas.BulkMark,
    marker_uuid: str,
    marker_role: str,
) -> list[schemas.AttendanceRecordResponse]:

    att = repository.get_attendance_session_by_uuid(db, payload.attendance_session_uuid)
    if not att:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    marker = get_user_by_uuid(db, marker_uuid)
    results = []
    for su in payload.student_uuids:
        student = get_user_by_uuid(db, su)
        if not student:
            continue
        existing = repository.get_record(db, att.id, student.id)
        data = {
            "status":            payload.status,
            "marked_by_role":    marker_role,
            "marked_by_user_id": marker.id if marker else None,
            "checked_in_at":     datetime.utcnow(),
        }
        if existing:
            record = repository.update_record(db, existing, data)
        else:
            data["attendance_session_id"] = att.id
            data["student_id"]            = student.id
            record = repository.create_record(db, data)
        results.append(_record_response(record))
    return results


# ─────────────────────────────────────────────
#  Queries
# ─────────────────────────────────────────────

def get_session_report(
    db: Session, att_session_uuid: str
) -> schemas.SessionAttendanceReport:

    att = repository.get_attendance_session_by_uuid(db, att_session_uuid)
    if not att:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    records = repository.get_records_for_session(db, att.id)
    return schemas.SessionAttendanceReport(
        attendance_session=_build_session_response(db, att),
        records=[_record_response(r) for r in records],
    )


def get_attendance_sessions_list(
    db: Session,
    batch_session_id: int | None = None,
    is_open: bool | None = None,
) -> list[schemas.AttendanceSessionResponse]:
    sessions = repository.list_attendance_sessions(
        db, batch_session_id=batch_session_id, is_open=is_open
    )
    return [_build_session_response(db, s) for s in sessions]


def get_student_history(
    db: Session, student_uuid: str
) -> list[schemas.AttendanceRecordResponse]:
    student = get_user_by_uuid(db, student_uuid)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    records = repository.get_records_for_student(db, student.id)
    return [_record_response(r) for r in records]


def get_student_summary(
    db: Session, student_uuid: str
) -> schemas.StudentAttendanceSummary:
    student = get_user_by_uuid(db, student_uuid)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    records = repository.get_records_for_student(db, student.id)
    total   = len(records)
    counts  = {"present": 0, "absent": 0, "late": 0, "excused": 0}
    for r in records:
        counts[r.status] = counts.get(r.status, 0) + 1

    pct = round((counts["present"] + counts["late"]) / total * 100, 1) if total else 0.0

    return schemas.StudentAttendanceSummary(
        student=schemas.UserMini(
            id=student.id, uuid=student.uuid,
            name=student.name, email=student.email,
        ),
        total_sessions=total,
        present=counts["present"],
        absent=counts["absent"],
        late=counts["late"],
        excused=counts["excused"],
        attendance_pct=pct,
    )


# ─────────────────────────────────────────────
#  Private serialiser
# ─────────────────────────────────────────────

def _record_response(r) -> schemas.AttendanceRecordResponse:
    return schemas.AttendanceRecordResponse(
        id=r.id, uuid=r.uuid, status=r.status,
        marked_by_role=r.marked_by_role,
        checked_in_at=r.checked_in_at,
        note=r.note,
        student=schemas.UserMini(
            id=r.student.id, uuid=r.student.uuid,
            name=r.student.name, email=r.student.email,
        ) if r.student else None,
        marker=schemas.UserMini(
            id=r.marker.id, uuid=r.marker.uuid,
            name=r.marker.name, email=r.marker.email,
        ) if r.marker else None,
    )