from sqlalchemy.orm import Session
from . import models


def create_batch(db: Session, data):

    batch = models.Batch(**data)

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return batch


def add_student_to_batch(db: Session, batch_id, student_id):

    batch_student = models.BatchStudent(
        batch_id=batch_id,
        student_id=student_id
    )

    db.add(batch_student)
    db.commit()

    return batch_student


def get_batch_by_uuid(db: Session, uuid: str):

    return db.query(models.Batch).filter(models.Batch.uuid == uuid).first()


def list_batches(db: Session):

    return db.query(models.Batch).all()


def get_students_by_batch(db: Session, batch_id: int):

    return db.query(models.BatchStudent).filter(
        models.BatchStudent.batch_id == batch_id
    ).all()