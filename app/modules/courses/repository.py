from sqlalchemy.orm import Session
from . import models


def create_course(db: Session, course_data, prices):

    course = models.Course(**course_data)

    db.add(course)
    db.flush()

    for price in prices:

        p = models.CoursePrice(
            course_id=course.id,
            country=price["country"],
            currency=price["currency"],
            price=price["price"]
        )

        db.add(p)

    db.commit()
    db.refresh(course)

    return course


def get_courses(db: Session):

    return db.query(models.Course).all()


def get_course_by_uuid(db: Session, uuid: str):

    return db.query(models.Course).filter(models.Course.uuid == uuid).first()