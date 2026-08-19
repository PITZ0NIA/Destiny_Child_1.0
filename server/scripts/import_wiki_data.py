# -*- coding: utf-8 -*-
"""Seeds the game-content tables (children, child_skins, soul_carta, items)
from data/wiki/*.json. Safe to re-run: upserts by wiki_page_id."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.db import Base, SessionLocal, engine
from app.models import Child, ChildSkin, Item, SoulCarta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WIKI_DATA_DIR = os.path.join(REPO_ROOT, "data", "wiki")

TEMPLATE_ARG_RE = re.compile(r"\{\{[^{}|]*\|([^{}]*)\}\}")
INT_RE = re.compile(r"^-?\d+$")


def extract_template_arg(s):
    if not s:
        return None
    m = TEMPLATE_ARG_RE.search(s)
    if m:
        return m.group(1).strip()
    return s.strip() or None


def parse_int(s):
    if not s:
        return None
    s = s.strip().replace(",", "")
    return int(s) if INT_RE.match(s) else None


def load(fname):
    with open(os.path.join(WIKI_DATA_DIR, fname), encoding="utf-8") as f:
        return json.load(f)


def import_children(db):
    entries = load("children.json")
    imported, skipped = 0, 0
    for e in entries:
        infobox = e.get("infobox") or {}
        hp = parse_int(infobox.get("hp"))
        if hp is None:
            skipped += 1
            continue  # no usable stats parsed for this page - don't insert a hollow row

        child = db.query(Child).filter_by(wiki_page_id=e["pageid"]).first()
        if child is None:
            child = Child(wiki_page_id=e["pageid"])
            db.add(child)

        child.name = e["title"]
        child.rarity = parse_int(extract_template_arg(infobox.get("rarity")))
        child.element = extract_template_arg(infobox.get("attribute"))
        child.role = extract_template_arg(infobox.get("type"))
        child.profile_text = infobox.get("mCaption")
        child.power = parse_int(infobox.get("power"))
        child.power_max = parse_int(infobox.get("power_max"))
        child.hp = hp
        child.hp_max = parse_int(infobox.get("hp_max"))
        child.atk = parse_int(infobox.get("atk"))
        child.atk_max = parse_int(infobox.get("atk_max"))
        child.def_ = parse_int(infobox.get("def"))
        child.def_max = parse_int(infobox.get("def_max"))
        child.agl = parse_int(infobox.get("agl"))
        child.agl_max = parse_int(infobox.get("agl_max"))
        child.crt = parse_int(infobox.get("crt"))
        child.crt_max = parse_int(infobox.get("crt_max"))
        db.flush()

        db.query(ChildSkin).filter_by(child_id=child.id).delete()
        for i in range(1, 9):
            tab_key = "tab1" if i == 1 else f"tab{i}"
            if tab_key not in infobox:
                continue
            suffix = "" if i == 1 else str(i)
            db.add(ChildSkin(
                child_id=child.id,
                tab_index=i,
                tab_label=infobox.get(tab_key),
                variant_name=infobox.get(f"title{suffix}"),
                image=infobox.get(f"image{suffix}"),
                caption=infobox.get(f"caption{suffix}"),
            ))
        imported += 1
    db.commit()
    print(f"children: {imported} imported, {skipped} skipped (no parsed stats)")


def _table_row_labels(row):
    return [cell[1] for cell in row]


def parse_equipment_tables(tables):
    """Shared shape for soul_carta.json / items.json pages: a Rarity/
    Restriction key-value table, a Stats grid, and an Enchantments table."""
    rarity = None
    restriction = None
    for table in tables:
        if not table:
            continue
        if all(len(r) == 2 for r in table) and len(table) <= 3:
            for r in table:
                key, val = r[0][1], r[1][1]
                if key.lower() == "rarity":
                    rarity = parse_int(val)
                elif key.lower() == "restriction":
                    restriction = None if val.lower() == "none" else val
    return rarity, restriction


def import_soul_carta(db):
    entries = load("soul_carta.json")
    imported = 0
    for e in entries:
        rarity, restriction = parse_equipment_tables(e.get("tables") or [])
        sc = db.query(SoulCarta).filter_by(wiki_page_id=e["pageid"]).first()
        if sc is None:
            sc = SoulCarta(wiki_page_id=e["pageid"])
            db.add(sc)
        sc.name = e["title"]
        sc.rarity = rarity
        sc.restriction = restriction
        imported += 1
    db.commit()
    print(f"soul_carta: {imported} imported")


def import_items(db):
    entries = load("items.json")
    imported = 0
    for e in entries:
        item = db.query(Item).filter_by(wiki_page_id=e["pageid"]).first()
        if item is None:
            item = Item(wiki_page_id=e["pageid"])
            db.add(item)
        item.name = e["title"]
        # best-effort flavor text: first non-empty line before any wiki markup block
        wt = e.get("wikitext") or ""
        desc = None
        for line in wt.split("\n"):
            line = line.strip()
            if line and not line.startswith(("{{", "{|", "[[File", "<")):
                desc = line
                break
        item.description = desc
        imported += 1
    db.commit()
    print(f"items: {imported} imported")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        import_children(session)
        import_soul_carta(session)
        import_items(session)
    finally:
        session.close()
