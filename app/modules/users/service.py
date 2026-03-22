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
    print("UUID RECEIVED:", user_uuid)
    user = repository.get_user_by_uuid(db, user_uuid)
    print(f"user: {user}")
    if not user:
        return None
    profile = repository.get_student_profile_by_user_id(db, user.id)
    print(f"profile: {profile}")
    return profile


def get_trainer_profile(db: Session, user_uuid: str):

    user = repository.get_user_by_uuid(db, user_uuid)

    if not user:
        return None

    return repository.get_trainer_profile_by_user_id(db, user.id)

def update_user_service(db, user_uuid: str, data):
    from . import repository
    user = repository.get_user_by_uuid(db, user_uuid)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
    return repository.update_user(db, user, update_dict)
 
 
def update_student_profile_service(db, user_uuid: str, profile_data):
    from . import repository
    user    = repository.get_user_by_uuid(db, user_uuid)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    profile = repository.get_student_profile_by_user_id(db, user.id)
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student profile not found")
    update_dict = {k: v for k, v in profile_data.model_dump().items() if v is not None}
    return repository.update_student_profile(db, profile, update_dict)
 
 
def update_trainer_profile_service(db, user_uuid: str, profile_data):
    from . import repository
    user    = repository.get_user_by_uuid(db, user_uuid)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    profile = repository.get_trainer_profile_by_user_id(db, user.id)
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Trainer profile not found")
    update_dict = {k: v for k, v in profile_data.model_dump().items() if v is not None}
    return repository.update_trainer_profile(db, profile, update_dict)


