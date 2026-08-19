# -*- coding: utf-8 -*-
"""
Scrapes destiny-child-for-kakao.fandom.com via the MediaWiki API to build
a structured JSON dataset (characters, equipment, items) for offline
private-server revival of Destiny Child. Personal preservation use.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import os

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://destiny-child-for-kakao.fandom.com/api.php"
UA = "DestinyChildArchiveBot/1.0 (personal offline-server revival project; contact: pitzonia124@gmail.com)"
OUT_DIR = r"C:\Destiny_Child\reports\wiki_data"
DELAY = 0.4  # seconds between requests, be polite

os.makedirs(OUT_DIR, exist_ok=True)


def api_get(params):
    params = dict(params)
    params["format"] = "json"
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_category_members(category, cmtype="page"):
    members = []
    cont = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": 500,
            "cmtype": cmtype,
        }
        if cont:
            params["cmcontinue"] = cont
        data = api_get(params)
        members.extend(data.get("query", {}).get("categorymembers", []))
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            break
        time.sleep(DELAY)
    return members


def get_wikitext(title):
    data = api_get({"action": "parse", "page": title, "prop": "wikitext"})
    if "error" in data:
        return None
    return data["parse"]["wikitext"]["*"]


TEMPLATE_RE = re.compile(r"\{\{(.*?)\n[ \t]*\}\}", re.DOTALL)
FIELD_RE = re.compile(r"^\s*\|\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$", re.MULTILINE)
TABLE_RE = re.compile(r"\{\|(.*?)\n\|\}", re.DOTALL)


def parse_infobox(wikitext):
    """Extract the first {{...}} template block's |key = value pairs."""
    if not wikitext:
        return {}
    m = TEMPLATE_RE.search(wikitext)
    if not m:
        return {}
    block = m.group(1)
    fields = {}
    for fm in FIELD_RE.finditer(block):
        key, val = fm.group(1), fm.group(2).strip()
        if val:
            fields[key] = val
    return fields


def _clean_cell(text):
    text = text.strip()
    # strip simple {{Template|arg}} -> arg, and [[Link|text]] -> text
    text = re.sub(r"\{\{[^{}|]*\|([^{}]*)\}\}", r"\1", text)
    text = re.sub(r"\{\{([^{}]*)\}\}", r"\1", text)
    text = re.sub(r"\[\[[^\[\]|]*\|([^\[\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\[\]]*)\]\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def parse_wikitables(wikitext):
    """Parse all {| ... |} wikitables into a list of row-dicts (header-keyed)
    when the table has a header row, or key/value pairs for 2-col tables."""
    if not wikitext:
        return []
    tables = []
    for tm in TABLE_RE.finditer(wikitext):
        body = tm.group(1)
        # drop the table attribute line (up to first newline)
        body = body.split("\n", 1)[1] if "\n" in body else ""
        rows = re.split(r"\n\|-", "\n" + body)
        parsed_rows = []
        for row in rows:
            row = row.strip()
            if not row:
                continue
            cells = []
            for line in row.split("\n"):
                line = line.strip()
                if line.startswith("!"):
                    for c in line[1:].split("!!"):
                        cells.append(("header", _clean_cell(c)))
                elif line.startswith("|") and not line.startswith("|-") and not line.startswith("|}"):
                    for c in line[1:].split("||"):
                        cells.append(("data", _clean_cell(c)))
            if cells:
                parsed_rows.append(cells)
        if parsed_rows:
            tables.append(parsed_rows)
    return tables


def scrape_category(category, out_filename, cmtype="page"):
    print(f"Fetching category members: {category}", flush=True)
    members = get_category_members(category, cmtype=cmtype)
    print(f"  {len(members)} pages found", flush=True)

    results = []
    for i, m in enumerate(members):
        title = m["title"]
        try:
            wikitext = get_wikitext(title)
        except Exception as e:
            print(f"  [{i+1}/{len(members)}] ERROR {title}: {e}", flush=True)
            wikitext = None
        fields = parse_infobox(wikitext) if wikitext else {}
        tables = parse_wikitables(wikitext) if wikitext else []
        results.append({
            "pageid": m.get("pageid"),
            "title": title,
            "infobox": fields,
            "tables": tables,
            "wikitext": wikitext,
        })
        if (i + 1) % 25 == 0 or (i + 1) == len(members):
            print(f"  [{i+1}/{len(members)}] {title}", flush=True)
        time.sleep(DELAY)

    out_path = os.path.join(OUT_DIR, out_filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved -> {out_path}", flush=True)
    return results


if __name__ == "__main__":
    scrape_category("Child", "children.json")
    scrape_category("Soul Carta", "soul_carta.json")
    scrape_category("Item", "items.json")
    print("DONE", flush=True)
