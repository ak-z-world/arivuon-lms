from enum import Enum


class UserRole(str, Enum):

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TRAINER = "trainer"
    STUDENT = "student"


class Gender(str, Enum):

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class TrainingMode(str, Enum):

    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"