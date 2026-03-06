from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

from . import schemas
from . import service


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):

    tokens = service.login_user(db, payload.email, payload.password)

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer"
    }