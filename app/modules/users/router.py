from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

from . import schemas
from . import service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schemas.APIResponse[schemas.UserResponse])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    created_user = service.create_user(db, user)
    return {
        "success": True,
        "message": "User created successfully",
        "data": created_user
    }

@router.post("/{user_uuid}/student-profile",
             response_model=schemas.APIResponse[schemas.StudentProfileResponse])
def create_student_profile(
    user_uuid: str,
    profile: schemas.StudentProfileCreate,
    db: Session = Depends(get_db)
):
    student_profile = service.create_student_profile(db, user_uuid, profile)

    return {
        "success": True,
        "message": "Student profile created successfully",
        "data": student_profile
    }

@router.post("/{user_uuid}/trainer-profile",
             response_model=schemas.APIResponse[schemas.TrainerProfileResponse])
def create_trainer_profile(
    user_uuid: str,
    profile: schemas.TrainerProfileCreate,
    db: Session = Depends(get_db)
):

    trainer_profile = service.create_trainer_profile(db, user_uuid, profile)

    return {
        "success": True,
        "message": "Trainer profile created successfully",
        "data": trainer_profile
    }

@router.get("/", response_model=schemas.APIResponse[list[schemas.UserResponse]])
def get_users(db: Session = Depends(get_db)):

    users = service.get_users(db)

    return {
        "success": True,
        "message": "Users fetched successfully",
        "data": users
    }


@router.get("/{user_uuid}", response_model=schemas.APIResponse[schemas.UserResponse])
def get_user(user_uuid: str, db: Session = Depends(get_db)):

    user = service.get_user_by_uuid(db, user_uuid)

    return {
        "success": True,
        "message": "User fetched successfully",
        "data": user
    }


@router.get("/{user_uuid}/student-profile",
            response_model=schemas.APIResponse[schemas.StudentProfileResponse])
def get_student_profile(user_uuid: str, db: Session = Depends(get_db)):

    profile = service.get_student_profile(db, user_uuid)

    return {
        "success": True,
        "message": "Student profile fetched successfully",
        "data": profile
    }


@router.get("/{user_uuid}/trainer-profile",
            response_model=schemas.APIResponse[schemas.TrainerProfileResponse])
def get_trainer_profile(user_uuid: str, db: Session = Depends(get_db)):

    profile = service.get_trainer_profile(db, user_uuid)

    return {
        "success": True,
        "message": "Trainer profile fetched successfully",
        "data": profile
    }

