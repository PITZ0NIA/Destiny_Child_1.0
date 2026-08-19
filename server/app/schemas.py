"""Pydantic response envelope, matching the HttpResponseBody<T> shape
documented in docs/network-protocol.md (data / error / localTimeInfo)."""
from typing import Any, Optional
from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str


class Envelope(BaseModel):
    data: Optional[Any] = None
    error: Optional[ErrorBody] = None
    localTimeInfo: dict


def ok(data: Any) -> dict:
    import datetime
    return {
        "data": data,
        "error": None,
        "localTimeInfo": {"serverTime": datetime.datetime.utcnow().isoformat() + "Z"},
    }


def fail(code: str, message: str) -> dict:
    import datetime
    return {
        "data": None,
        "error": {"code": code, "message": message},
        "localTimeInfo": {"serverTime": datetime.datetime.utcnow().isoformat() + "Z"},
    }
