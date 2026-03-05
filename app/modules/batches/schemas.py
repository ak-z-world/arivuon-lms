from pydantic import BaseModel
from datetime import date
from typing import List


class BatchBase(BaseModel):

    course_uuid: str
    trainer_uuid: str
    name: str
    start_date: date
    end_date: date
    schedule: str
    timezone: str


class BatchCreate(BatchBase):
    pass


class BatchStudentAdd(BaseModel):

    student_uuid: str


class BatchResponse(BaseModel):

    uuid: str
    name: str
    start_date: date
    end_date: date
    schedule: str

    class Config:
        from_attributes = True