from sqlalchemy.orm import Session

from . import repository
from app.modules.batches.repository import get_batch_by_uuid
from app.modules.users.repository import get_user_by_uuid


def create_session(db: Session, session):

    session_data = session.model_dump()

    batch = get_batch_by_uuid(db, session_data["batch_uuid"])
    trainer = get_user_by_uuid(db, session_data["trainer_uuid"])

    session_data["batch_id"] = batch.id
    session_data["trainer_id"] = trainer.id

    del session_data["batch_uuid"]
    del session_data["trainer_uuid"]

    return repository.create_session(db, session_data)


def get_batch_sessions(db: Session, batch_uuid):

    batch = get_batch_by_uuid(db, batch_uuid)

    return repository.get_sessions_by_batch(db, batch.id)


def mark_attendance(db: Session, session_uuid, student_uuid, status):

    session = repository.get_session_by_uuid(db, session_uuid)

    student = get_user_by_uuid(db, student_uuid)

    data = {
        "session_id": session.id,
        "student_id": student.id,
        "status": status
    }

    return repository.mark_attendance(db, data)


def add_resource(db: Session, session_uuid, resource):

    session = repository.get_session_by_uuid(db, session_uuid)

    resource_data = resource.model_dump()

    resource_data["session_id"] = session.id

    return repository.add_resource(db, resource_data)