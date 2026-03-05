from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import repository
from . import schemas


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    password = password[:72]
    return pwd_context.hash(password)


def create_user(db: Session, user: schemas.UserCreate):

    hashed = hash_password(user.password)

    user_data = user.model_dump()

    user_data["password_hash"] = hashed

    del user_data["password"]

    return repository.create_user(db, user_data)


def create_student_profile(db: Session, user_uuid: str, profile: schemas.StudentProfileCreate):

    user = repository.get_user_by_uuid(db, user_uuid)

    if not user:
        raise ValueError("User not found")

    profile_data = profile.model_dump()

    profile_data["user_id"] = user.id   # convert uuid → internal id

    return repository.create_student_profile(db, profile_data)


def create_trainer_profile(db: Session, user_uuid: str, profile: schemas.TrainerProfileCreate):

    user = repository.get_user_by_uuid(db, user_uuid)

    if not user:
        raise ValueError("User not found")

    profile_data = profile.model_dump()

    profile_data["user_id"] = user.id

    return repository.create_trainer_profile(db, profile_data)

def get_users(db: Session):

    return repository.get_users(db)


def get_user_by_uuid(db: Session, user_uuid: str):

    return repository.get_user_by_uuid(db, user_uuid)


def get_student_profile(db: Session, user_uuid: str):

    user = repository.get_user_by_uuid(db, user_uuid)

    if not user:
        return None

    return repository.get_student_profile_by_user_id(db, user.id)


def get_trainer_profile(db: Session, user_uuid: str):

    user = repository.get_user_by_uuid(db, user_uuid)

    if not user:
        return None

    return repository.get_trainer_profile_by_user_id(db, user.id)

