from pydantic import BaseModel
from datetime import date, time
from typing import Optional


class SessionCreate(BaseModel):

    batch_uuid: str
    trainer_uuid: str
    title: str
    session_number: int
    session_date: date
    start_time: time
    end_time: time
    meeting_link: Optional[str]


class SessionResponse(BaseModel):

    uuid: str
    title: str
    session_number: int
    session_date: date
    start_time: time
    end_time: time
    status: str

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):

    student_uuid: str
    status: str


class ResourceCreate(BaseModel):

    title: str
    resource_type: str
    url: str