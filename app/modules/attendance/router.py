# app/modules/attendance/router.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from . import schemas, service

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# ═══════════════════════════════════════════════════
#  PULSE SESSION  — trainer / admin manages windows
# ═══════════════════════════════════════════════════

@router.post(
    "/sessions/open",
    response_model=schemas.APIResponse[schemas.AttendanceSessionResponse],
    summary="Open a PULSE attendance window for a batch session",
)
def open_pulse(
    payload:        schemas.AttendanceSessionOpen,
    opened_by_uuid: str = Query(..., description="UUID of the trainer / admin opening the pulse"),
    db: Session = Depends(get_db),
):
    """
    Trainer calls this before / at the start of a class.
    Returns a 6-digit PULSE code students enter to check in.
    """
    att = service.open_attendance_session(db, payload, opened_by_uuid)
    return {"success": True, "message": "PULSE opened", "data": att}


@router.post(
    "/sessions/{att_session_uuid}/close",
    response_model=schemas.APIResponse[schemas.AttendanceSessionResponse],
    summary="Close the attendance window (no more self check-ins)",
)
def close_pulse(
    att_session_uuid: str,
    db: Session = Depends(get_db),
):
    att = service.close_attendance_session(db, att_session_uuid)
    return {"success": True, "message": "PULSE closed", "data": att}


@router.get(
    "/sessions",
    response_model=schemas.APIResponse[list[schemas.AttendanceSessionResponse]],
    summary="List attendance sessions (admin / trainer dashboard)",
)
def list_sessions(
    batch_session_id: Optional[int]  = Query(None),
    is_open:          Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    data = service.get_attendance_sessions_list(
        db, batch_session_id=batch_session_id, is_open=is_open
    )
    return {"success": True, "message": "OK", "data": data}


@router.get(
    "/sessions/{att_session_uuid}/report",
    response_model=schemas.APIResponse[schemas.SessionAttendanceReport],
    summary="Full attendance report for one session",
)
def session_report(
    att_session_uuid: str,
    db: Session = Depends(get_db),
):
    report = service.get_session_report(db, att_session_uuid)
    return {"success": True, "message": "OK", "data": report}


# ═══════════════════════════════════════════════════
#  STUDENT SELF CHECK-IN
# ═══════════════════════════════════════════════════

@router.post(
    "/sessions/{att_session_uuid}/checkin",
    response_model=schemas.APIResponse[schemas.AttendanceRecordResponse],
    summary="Student checks in using the PULSE code",
)
def student_checkin(
    att_session_uuid: str,
    payload:          schemas.SelfCheckIn,
    student_uuid:     str = Query(..., description="UUID of the student checking in"),
    db: Session = Depends(get_db),
):
    record = service.self_checkin(
        db,
        att_session_uuid=att_session_uuid,
        student_uuid=student_uuid,
        pulse_code=payload.pulse_code,
    )
    return {"success": True, "message": "Checked in successfully", "data": record}


# ═══════════════════════════════════════════════════
#  MANUAL MARK  — trainer or admin
# ═══════════════════════════════════════════════════

@router.post(
    "/sessions/{att_session_uuid}/mark",
    response_model=schemas.APIResponse[schemas.AttendanceRecordResponse],
    summary="Trainer / Admin manually marks a student's attendance",
)
def manual_mark(
    att_session_uuid: str,
    payload:          schemas.ManualMark,
    marker_uuid:      str = Query(...),
    marker_role:      str = Query("trainer", description="trainer | admin"),
    db: Session = Depends(get_db),
):
    record = service.manual_mark(
        db, att_session_uuid, payload, marker_uuid, marker_role
    )
    return {"success": True, "message": "Attendance marked", "data": record}


@router.post(
    "/sessions/{att_session_uuid}/bulk-mark",
    response_model=schemas.APIResponse[list[schemas.AttendanceRecordResponse]],
    summary="Mark multiple students at once",
)
def bulk_mark(
    att_session_uuid: str,
    payload:          schemas.BulkMark,
    marker_uuid:      str = Query(...),
    marker_role:      str = Query("trainer"),
    db: Session = Depends(get_db),
):
    # Ensure payload targets the right session
    payload.attendance_session_uuid = att_session_uuid
    records = service.bulk_mark(db, payload, marker_uuid, marker_role)
    return {"success": True, "message": f"Marked {len(records)} students", "data": records}


# ═══════════════════════════════════════════════════
#  STUDENT QUERIES
# ═══════════════════════════════════════════════════

@router.get(
    "/students/{student_uuid}/history",
    response_model=schemas.APIResponse[list[schemas.AttendanceRecordResponse]],
    summary="Full attendance history for a student",
)
def student_history(
    student_uuid: str,
    db: Session = Depends(get_db),
):
    data = service.get_student_history(db, student_uuid)
    return {"success": True, "message": "OK", "data": data}


@router.get(
    "/students/{student_uuid}/summary",
    response_model=schemas.APIResponse[schemas.StudentAttendanceSummary],
    summary="Attendance summary / percentage for a student",
)
def student_summary(
    student_uuid: str,
    db: Session = Depends(get_db),
):
    data = service.get_student_summary(db, student_uuid)
    return {"success": True, "message": "OK", "data": data}

