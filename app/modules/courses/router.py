# D:\arivuon-lms\app\modules\courses\router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from . import schemas
from . import service

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/category/", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):

    return service.create_category(db, category)


@router.get("/category", response_model=list[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):

    return service.get_categories(db)

@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):

    return service.create_course(db, course)


@router.get("/", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):

    return service.get_courses(db)