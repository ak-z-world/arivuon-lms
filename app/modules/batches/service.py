from sqlalchemy.orm import Session
from . import repository
from app.modules.users.repository import get_user_by_uuid
from app.modules.courses.repository import get_course_by_uuid
from fastapi import HTTPException
from app.modules.users.models import TrainerProfile, StudentProfile

def create_batch(db: Session, batch):

    batch_data = batch.model_dump()

    # Get Course
    course = get_course_by_uuid(db, batch_data["course_uuid"])
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    trainer_uuid = batch_data["trainer_uuid"]

    # Step 1: Try getting trainer as USER
    trainer = get_user_by_uuid(db, trainer_uuid)

    # Step 2: If not found, try TRAINER PROFILE
    if not trainer:
        trainer_profile = db.query(TrainerProfile).filter(
            TrainerProfile.uuid == trainer_uuid
        ).first()

        if not trainer_profile:
            raise HTTPException(status_code=404, detail="Trainer not found")

        trainer = trainer_profile.user

    # Step 3: Validate role
    if trainer.role != "trainer":
        raise HTTPException(status_code=400, detail="User is not a trainer")

    # Assign IDs
    batch_data["course_id"] = course.id
    batch_data["trainer_id"] = trainer.id

    # Cleanup
    del batch_data["course_uuid"]
    del batch_data["trainer_uuid"]

    return repository.create_batch(db, batch_data)

def add_student(db: Session, batch_uuid, student_uuid):

    batch = repository.get_batch_by_uuid(db, batch_uuid)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Step 1: Try as USER UUID
    student = get_user_by_uuid(db, student_uuid)

    # Step 2: If not found, try STUDENT PROFILE UUID
    if not student:
        student_profile = db.query(StudentProfile).filter(
            StudentProfile.uuid == student_uuid
        ).first()

        if not student_profile:
            raise HTTPException(status_code=404, detail="Student not found")

        student = student_profile.user

    # Step 3: Validate role
    if student.role != "student":
        raise HTTPException(status_code=400, detail="User is not a student")

    return repository.add_student_to_batch(db, batch.id, student.id)

def list_batches(db: Session):

    return repository.list_batches(db)


def get_batch(db: Session, batch_uuid: str):

    return repository.get_batch_by_uuid(db, batch_uuid)


def get_batch_students(db: Session, batch_uuid: str):

    batch = repository.get_batch_by_uuid(db, batch_uuid)

    return repository.get_students_by_batch(db, batch.id)