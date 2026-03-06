from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.users import repository

from .security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):

    try:
        payload = decode_token(token)

        user_uuid = payload.get("sub")

        if user_uuid is None:
            raise HTTPException(status_code=401)

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = repository.get_user_by_uuid(db, user_uuid)

    if not user:
        raise HTTPException(status_code=401)

    return user