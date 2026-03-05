from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
import uuid
from app.database.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)

    name = Column(String(120), nullable=False)

    email = Column(String(150), unique=True, index=True, nullable=False)

    phone = Column(String(20))

    password_hash = Column(String(255), nullable=False)

    role = Column(String(50), default="student")

    is_active = Column(Boolean, default=True)

    is_verified = Column(Boolean, default=False)

    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)

    trainer_profile = relationship("TrainerProfile", back_populates="user", uselist=False)


class StudentProfile(Base):

    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    dob = Column(Date)

    gender = Column(String(20))

    whatsapp = Column(String(20))

    address = Column(Text)

    city = Column(String(100))

    state = Column(String(100))

    country = Column(String(100))

    pincode = Column(String(20))

    highest_qualification = Column(String(100))

    degree = Column(String(100))

    college = Column(String(200))

    yop = Column(Integer)

    technical_background = Column(String(200))

    technologies_known = Column(Text)

    course_selection = Column(String(200))

    training_mode = Column(String(50))

    course_fee = Column(Float)

    amount_paid = Column(Float)

    notes = Column(Text)

    user = relationship("User", back_populates="student_profile")


class TrainerProfile(Base):

    __tablename__ = "trainer_profiles"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    expertise = Column(String(200))

    technologies = Column(Text)

    experience_years = Column(Integer)

    bio = Column(Text)

    linkedin = Column(String(200))

    github = Column(String(200))

    user = relationship("User", back_populates="trainer_profile")