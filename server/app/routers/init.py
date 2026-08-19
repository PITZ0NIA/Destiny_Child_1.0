import datetime

from fastapi import APIRouter

from ..schemas import ok

router = APIRouter()


@router.get("/api/init")
def init():
    """Mirrors InitRequest : HttpRequest<InitResponse, InitResponseExtraData>."""
    return ok({
        "serverStatus": "ok",
        "maintenance": False,
        "minClientVersion": "2.15.2",
        "serverTime": datetime.datetime.utcnow().isoformat() + "Z",
    })
