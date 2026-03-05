from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from typing import Generic, TypeVar

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T

class UserBase(BaseModel):

    name: str

    email: EmailStr

    phone: Optional[str]

    role: Optional[str]


class UserCreate(UserBase):

    password: str = Field(..., min_length=6, max_length=72)


class UserResponse(UserBase):

    id: int
    uuid: str
    is_active: bool

    is_verified: bool

    class Config:

        from_attributes = True


class StudentProfileBase(BaseModel):

    dob: Optional[date]

    gender: Optional[str]

    whatsapp: Optional[str]

    address: Optional[str]

    city: Optional[str]

    state: Optional[str]

    country: Optional[str]

    pincode: Optional[str]

    highest_qualification: Optional[str]

    degree: Optional[str]

    college: Optional[str]

    yop: Optional[int]

    technical_background: Optional[str]

    technologies_known: Optional[str]

    course_selection: Optional[str]

    training_mode: Optional[str]

    course_fee: Optional[float]

    amount_paid: Optional[float]


class StudentProfileCreate(StudentProfileBase):

    pass


class StudentProfileResponse(StudentProfileBase):

    id: int
    uuid: str
    user_id: int

    class Config:

        from_attributes = True


class TrainerProfileBase(BaseModel):

    expertise: Optional[str]

    technologies: Optional[str]

    experience_years: Optional[int]

    bio: Optional[str]

    linkedin: Optional[str]

    github: Optional[str]


class TrainerProfileCreate(TrainerProfileBase):

    pass


class TrainerProfileResponse(TrainerProfileBase):

    id: int
    uuid: str
    user_id: int

    class Config:

        from_attributes = True