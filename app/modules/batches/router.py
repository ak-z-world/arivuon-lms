from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from . import schemas
from . import service

router = APIRouter(prefix="/batches", tags=["Batches"])


@router.post("/", response_model=schemas.BatchResponse)
def create_batch(batch: schemas.BatchCreate, db: Session = Depends(get_db)):

    return service.create_batch(db, batch)


@router.post("/{batch_uuid}/students")
def add_student_to_batch(batch_uuid: str, student: schemas.BatchStudentAdd, db: Session = Depends(get_db)):

    return service.add_student(db, batch_uuid, student.student_uuid)

@router.get("/", response_model=list[schemas.BatchResponse])
def list_batches(db: Session = Depends(get_db)):

    return service.list_batches(db)


@router.get("/{batch_uuid}", response_model=schemas.BatchResponse)
def get_batch(batch_uuid: str, db: Session = Depends(get_db)):

    return service.get_batch(db, batch_uuid)


@router.get("/{batch_uuid}/students")
def list_batch_students(batch_uuid: str, db: Session = Depends(get_db)):

    return service.get_batch_students(db, batch_uuid)