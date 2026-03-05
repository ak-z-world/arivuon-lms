from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from . import schemas
from . import service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=schemas.SessionResponse)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):

    return service.create_session(db, session)


@router.get("/batch/{batch_uuid}", response_model=list[schemas.SessionResponse])
def list_batch_sessions(batch_uuid: str, db: Session = Depends(get_db)):

    return service.get_batch_sessions(db, batch_uuid)


@router.post("/{session_uuid}/attendance")
def mark_attendance(session_uuid: str, attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):

    return service.mark_attendance(
        db,
        session_uuid,
        attendance.student_uuid,
        attendance.status
    )


@router.post("/{session_uuid}/resources")
def add_resource(session_uuid: str, resource: schemas.ResourceCreate, db: Session = Depends(get_db)):

    return service.add_resource(db, session_uuid, resource)