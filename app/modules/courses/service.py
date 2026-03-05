from sqlalchemy.orm import Session
from . import repository


def create_course(db: Session, course):

    course_data = course.model_dump()
    prices = course_data.pop("prices")

    return repository.create_course(db, course_data, prices)


def get_courses(db: Session):

    return repository.get_courses(db)