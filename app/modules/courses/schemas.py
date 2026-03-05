from pydantic import BaseModel
from typing import Optional, List


class CoursePriceBase(BaseModel):

    country: str
    currency: str
    price: float


class CoursePriceCreate(CoursePriceBase):
    pass


class CoursePriceResponse(CoursePriceBase):

    id: int

    class Config:
        from_attributes = True


class CourseBase(BaseModel):

    title: str
    description: Optional[str]
    level: Optional[str]
    duration: Optional[str]
    category: Optional[str]


class CourseCreate(CourseBase):

    prices: List[CoursePriceCreate]


class CourseResponse(CourseBase):

    uuid: str
    thumbnail: Optional[str]

    prices: List[CoursePriceResponse]

    class Config:
        from_attributes = True