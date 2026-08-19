import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from .. import models
from ..auth import SESSION_LIFETIME, new_token
from ..db import get_db
from ..schemas import ok

router = APIRouter()


class LoginRequest(BaseModel):
    platform_id: str
    display_name: str | None = None


@router.post("/api/login")
def login(body: LoginRequest, db: DbSession = Depends(get_db)):
    """Mirrors RequestLogin : HttpRequest<LoginResponse, LoginExtraData>.

    No real platform auth here (this is a local/offline server) - platform_id
    is trusted as given by the client, matching how a real Google Play Games
    / platform token would already have been validated upstream in the
    original architecture (PlatformLoginRequest)."""
    account = db.query(models.Account).filter_by(platform_id=body.platform_id).first()
    if account is None:
        account = models.Account(platform_id=body.platform_id, display_name=body.display_name or body.platform_id)
        db.add(account)
        db.flush()
        db.add(models.PlayerProfile(account_id=account.id))

    session = models.Session(
        account_id=account.id,
        token=new_token(),
        expires_at=datetime.datetime.utcnow() + SESSION_LIFETIME,
    )
    db.add(session)
    db.commit()

    profile = db.query(models.PlayerProfile).filter_by(account_id=account.id).first()

    return ok({
        "accountId": account.id,
        "displayName": account.display_name,
        "sessionToken": session.token,
        "expiresAt": session.expires_at.isoformat() + "Z",
        "profile": {
            "level": profile.level,
            "exp": profile.exp,
            "gold": profile.gold,
            "gems": profile.gems,
        },
    })
