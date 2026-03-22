# D:\arivuon-lms\app\modules\courses\schemas.py
from pydantic import BaseModel
from typing import Optional, List


class CategoryBase(BaseModel):

    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):

    uuid: str

    class Config:
        from_attributes = True

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
    slug: str
    description: Optional[str]
    level: Optional[str]
    duration: Optional[str]
    thumbnail: Optional[str] = None
    category_id: int
    is_active: Optional[str] = "true"


class CourseCreate(CourseBase):

    prices: List[CoursePriceCreate]


class CourseResponse(CourseBase):

    uuid: str
    thumbnail: Optional[str]

    prices: List[CoursePriceResponse]

    class Config:
        from_attributes = True