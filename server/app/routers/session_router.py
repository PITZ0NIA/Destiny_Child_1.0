import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from .. import models
from ..auth import SESSION_LIFETIME, get_current_session
from ..db import get_db
from ..schemas import ok

router = APIRouter()


@router.post("/api/session/validate")
def validate_session(
    session: models.Session = Depends(get_current_session),
    db: DbSession = Depends(get_db),
):
    """Mirrors SessionValidateRequest. Extends the session on each successful
    validation, matching the client's periodic revalidation behavior."""
    session.expires_at = datetime.datetime.utcnow() + SESSION_LIFETIME
    db.commit()
    return ok({"valid": True, "expiresAt": session.expires_at.isoformat() + "Z"})


@router.post("/api/session/logout")
def logout_session(
    session: models.Session = Depends(get_current_session),
    db: DbSession = Depends(get_db),
):
    """Mirrors SessionLogoutRequest."""
    db.delete(session)
    db.commit()
    return ok({"loggedOut": True})
