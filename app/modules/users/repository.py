from sqlalchemy.orm import Session
from . import models


def create_user(db: Session, user_data):

    user = models.User(**user_data)

    db.add(user)

    db.commit()

    db.refresh(user)

    return user

def get_users(db: Session):

    return db.query(models.User).all()


def get_student_profile_by_user_id(db: Session, user_id: int):

    return db.query(models.StudentProfile).filter(
        models.StudentProfile.user_id == user_id
    ).first()


def get_trainer_profile_by_user_id(db: Session, user_id: int):

    return db.query(models.TrainerProfile).filter(
        models.TrainerProfile.user_id == user_id
    ).first()

def get_user_by_email(db: Session, email: str):

    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_uuid(db: Session, uuid: str):

    return db.query(models.User).filter(models.User.uuid == uuid).first()

def create_student_profile(db: Session, profile_data):

    profile = models.StudentProfile(**profile_data)

    db.add(profile)

    db.commit()

    db.refresh(profile)

    return profile


def create_trainer_profile(db: Session, profile_data):

    profile = models.TrainerProfile(**profile_data)

    db.add(profile)

    db.commit()

    db.refresh(profile)

    return profile