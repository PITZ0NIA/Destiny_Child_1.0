from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from .. import models
from ..auth import get_current_session
from ..db import get_db
from ..schemas import ok

router = APIRouter()


def _child_summary(c: models.Child) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "rarity": c.rarity,
        "element": c.element,
        "role": c.role,
        "hp": c.hp,
        "atk": c.atk,
        "def": c.def_,
        "agl": c.agl,
        "crt": c.crt,
    }


@router.get("/api/catalog/children")
def catalog_children(db: DbSession = Depends(get_db)):
    """Master data - matches what GetTablesByDistributeIdRequest would have
    fetched in the original client. Seeded from data/wiki/children.json via
    scripts/import_wiki_data.py."""
    children = db.query(models.Child).order_by(models.Child.name).all()
    return ok([_child_summary(c) for c in children])


@router.get("/api/roster")
def roster(
    session: models.Session = Depends(get_current_session),
    db: DbSession = Depends(get_db),
):
    """The logged-in account's owned children."""
    owned = (
        db.query(models.PlayerChild)
        .filter_by(account_id=session.account_id)
        .all()
    )
    result = []
    for pc in owned:
        child = db.query(models.Child).get(pc.child_id)
        result.append({
            "playerChildId": pc.id,
            "level": pc.level,
            "stars": pc.stars,
            "exp": pc.exp,
            "child": _child_summary(child) if child else None,
        })
    return ok(result)
