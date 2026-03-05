from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from . import schemas
from . import service

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):

    return service.create_course(db, course)


@router.get("/", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):

    return service.get_courses(db)