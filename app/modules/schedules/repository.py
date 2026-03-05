from sqlalchemy.orm import Session
from . import models


def create_session(db: Session, data):

    session = models.BatchSession(**data)

    db.add(session)

    db.commit()

    db.refresh(session)

    return session


def get_sessions_by_batch(db: Session, batch_id):

    return db.query(models.BatchSession).filter(
        models.BatchSession.batch_id == batch_id
    ).all()


def get_session_by_uuid(db: Session, uuid):

    return db.query(models.BatchSession).filter(
        models.BatchSession.uuid == uuid
    ).first()


def mark_attendance(db: Session, data):

    attendance = models.SessionAttendance(**data)

    db.add(attendance)

    db.commit()

    return attendance


def add_resource(db: Session, data):

    resource = models.SessionResource(**data)

    db.add(resource)

    db.commit()

    return resource