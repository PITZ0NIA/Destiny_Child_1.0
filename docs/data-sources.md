# Data Sources

## Community wiki dataset (`data/wiki/`)

Scraped from **Destiny Child for Kakao Wiki**
(https://destiny-child-for-kakao.fandom.com), via its public MediaWiki API,
on 2026-08-19. Fandom wiki content is published under **CC BY-SA** unless a
page states otherwise — keep attribution to the wiki and its editors when
this data is reused or redistributed.

- `children.json` — 456 pages, category `Child` (playable summons).
- `soul_carta.json` — 65 pages, category `Soul Carta` (equipment).
- `items.json` — 37 pages, category `Item` (materials).

Each entry contains:
- `infobox` — parsed `{{...}}` template key/value fields (stats, rarity,
  element, type, skill text, etc.) where the page used that template
  format (~66% of character pages).
- `tables` — parsed `{| ... |}` wikitables (used by equipment/item pages
  for stat-by-level tables, enchantments, etc.), as a nested list of
  `[kind, text]` cells per row.
- `wikitext` — the raw original wikitext for every page, kept so the
  dataset can be re-parsed or manually corrected without re-scraping.

This is **Kakao-region community data**, not extracted from the Global
client — treat numeric balance values as a strong reference, not a
guaranteed match to the exact Global 2.15.2 build.

Scraper: `scripts/scrape_wiki.py` (polite: 0.4s delay between requests,
identifies itself via User-Agent).

## Leaked source code (not incorporated)

A RaGEZone forum thread claims to share the original client + server
(Erlang) source, leaked out of China after the 2023 shutdown:
https://forum.ragezone.com/threads/destiny-child-client-source-code-server-source-code-development-documentation.1229955/

Not used here. Community replies in that thread flag real credibility
concerns (password-protected Baidu mirrors, some files reportedly Java
instead of the claimed Erlang, at least one fake MediaFire mirror reported).
Worth revisiting as a lead, but nothing from it should be merged into this
repo without first independently verifying it against what we've derived
from the client ourselves.

## Client analysis (kept local, not in this repo)

- `apk/` — the original APK. Never commit: exceeds GitHub's 100MB limit and
  redistributes Shift Up's copyrighted binary.
- `apk_desmantelada/` — JADX decompile output, the IL2CPP dump
  (`Il2CppDumper`), and extracted Unity asset bundles. Never commit: this is
  either decompiled/reverse-engineered proprietary code or copyrighted game
  art/audio/models, not our own work product. `docs/network-protocol.md`
  captures the useful findings from it in our own words instead.
