import datetime
import secrets

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session as DbSession

from . import models
from .db import get_db

SESSION_LIFETIME = datetime.timedelta(minutes=30)  # matches ApiServerSetting.sessionValidatePeriod intent


def new_token() -> str:
    return secrets.token_hex(24)


def get_current_session(
    x_session_token: str | None = Header(None, alias="X-Session-Token"),
    db: DbSession = Depends(get_db),
) -> models.Session:
    if x_session_token is None:
        raise HTTPException(status_code=401, detail="missing session token")
    session = db.query(models.Session).filter_by(token=x_session_token).first()
    if session is None:
        raise HTTPException(status_code=401, detail="invalid session token")
    if session.expires_at < datetime.datetime.utcnow():
        raise HTTPException(status_code=401, detail="session expired")
    return session
