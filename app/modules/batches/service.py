from sqlalchemy.orm import Session
from . import repository
from app.modules.users.repository import get_user_by_uuid
from app.modules.courses.repository import get_course_by_uuid


def create_batch(db: Session, batch):

    batch_data = batch.model_dump()

    course = get_course_by_uuid(db, batch_data["course_uuid"])
    trainer = get_user_by_uuid(db, batch_data["trainer_uuid"])

    print("Trainer UUID:", batch_data["trainer_uuid"])
    print("Trainer:", trainer)

    batch_data["course_id"] = course.id
    batch_data["trainer_id"] = trainer.id

    del batch_data["course_uuid"]
    del batch_data["trainer_uuid"]

    return repository.create_batch(db, batch_data)


def add_student(db: Session, batch_uuid, student_uuid):

    batch = repository.get_batch_by_uuid(db, batch_uuid)

    student = get_user_by_uuid(db, student_uuid)

    return repository.add_student_to_batch(db, batch.id, student.id)

def list_batches(db: Session):

    return repository.list_batches(db)


def get_batch(db: Session, batch_uuid: str):

    return repository.get_batch_by_uuid(db, batch_uuid)


def get_batch_students(db: Session, batch_uuid: str):

    batch = repository.get_batch_by_uuid(db, batch_uuid)

    return repository.get_students_by_batch(db, batch.id)