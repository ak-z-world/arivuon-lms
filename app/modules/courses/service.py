# D:\arivuon-lms\app\modules\courses\service.py
from sqlalchemy.orm import Session
from . import repository


def create_category(db: Session, category):

    category_data = category.model_dump()

    return repository.create_category(db, category_data)


def get_categories(db: Session):

    return repository.get_categories(db)

def create_course(db: Session, course):

    course_data = course.model_dump()
    prices = course_data.pop("prices")

    return repository.create_course(db, course_data, prices)


def get_courses(db: Session):

    return repository.get_courses(db)