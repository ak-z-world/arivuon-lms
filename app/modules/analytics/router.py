# app/modules/analytics/router.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from . import schemas, service

router = APIRouter(prefix="/analytics", tags=["Analytics / Dashboard"])


# ── TRAINER ──────────────────────────────────────────
@router.get(
    "/dashboard/trainer/{trainer_uuid}",
    response_model=schemas.APIResponse[schemas.TrainerDashboard],
    summary="Trainer dashboard — batches, sessions, students, attendance",
)
def trainer_dashboard(trainer_uuid: str, db: Session = Depends(get_db)):
    data = service.get_trainer_dashboard(db, trainer_uuid)
    return {"success": True, "message": "OK", "data": data}


# ── STUDENT ──────────────────────────────────────────
@router.get(
    "/dashboard/student/{student_uuid}",
    response_model=schemas.APIResponse[schemas.StudentDashboard],
    summary="Student dashboard — enrolments, attendance, upcoming sessions",
)
def student_dashboard(student_uuid: str, db: Session = Depends(get_db)):
    data = service.get_student_dashboard(db, student_uuid)
    return {"success": True, "message": "OK", "data": data}


# ── ADMIN ─────────────────────────────────────────────
@router.get(
    "/dashboard/admin",
    response_model=schemas.APIResponse[schemas.AdminDashboard],
    summary="Admin dashboard — platform-wide stats",
)
def admin_dashboard(db: Session = Depends(get_db)):
    data = service.get_admin_dashboard(db)
    return {"success": True, "message": "OK", "data": data}