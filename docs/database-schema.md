# Database Schema (draft)

Two concerns, kept in separate table groups: **game content** (seeded once
from `data/wiki/`, effectively read-only at runtime) and **player state**
(written constantly by the server). SQL below is written in
SQLite-compatible syntax as a baseline — trivially portable to
Postgres/MySQL if the server ends up needing concurrent writers.

## Game content (seeded from `data/wiki/*.json`)

```sql
CREATE TABLE children (
    id              INTEGER PRIMARY KEY,
    wiki_page_id    INTEGER UNIQUE,        -- traceability back to data/wiki/children.json
    name            TEXT NOT NULL,          -- canonical name = wiki page title, e.g. "Isolde"
    rarity          INTEGER,                -- 1-5 stars
    element         TEXT,                   -- fire/water/wood/light/dark
    role            TEXT,                   -- attacker/defender/supporter/debuffer/healer
    profile_text    TEXT,                   -- mCaption / bio
    power           INTEGER, power_max      INTEGER,
    hp              INTEGER, hp_max         INTEGER,
    atk             INTEGER, atk_max        INTEGER,
    def             INTEGER, def_max        INTEGER,
    agl             INTEGER, agl_max        INTEGER,
    crt             INTEGER, crt_max        INTEGER
);

-- costume/tab variants (E-Rank, S-Rank, Pactmaker, Shop, Event, Spa, ...)
CREATE TABLE child_skins (
    id              INTEGER PRIMARY KEY,
    child_id        INTEGER NOT NULL REFERENCES children(id),
    tab_index       INTEGER NOT NULL,       -- 1..8, order as listed on the wiki page
    tab_label       TEXT,                   -- "E-Rank" / "S-Rank" / "Pactmaker" / "Shop" / "Event" / "Spa"
    variant_name    TEXT,
    image           TEXT,
    caption         TEXT
);

-- self-referential "related children" (dChild field, e.g. Lisa -> Mona, Davi)
CREATE TABLE child_relations (
    child_id        INTEGER NOT NULL REFERENCES children(id),
    related_child_id INTEGER NOT NULL REFERENCES children(id),
    PRIMARY KEY (child_id, related_child_id)
);

-- one row per skill slot per child; rank_from/rank_to capture the scaling
-- shown on the wiki (e.g. "Rank 1/1" -> "Rank 7/10"). NOT YET POPULATED —
-- the wiki scraper currently captures skill tables as generic rows
-- (see data/wiki/children.json[].tables); this table is the target shape
-- once that gets a dedicated parser.
CREATE TABLE skills (
    id              INTEGER PRIMARY KEY,
    child_id        INTEGER NOT NULL REFERENCES children(id),
    slot            TEXT NOT NULL,          -- auto / tap / slide / drive / leader
    skill_name      TEXT,
    rank_or_level   TEXT,                   -- e.g. "Rank 1/1", "Level 60+6"
    description     TEXT,
    damage_value    INTEGER                 -- nullable; not every skill deals direct damage
);

CREATE TABLE soul_carta (
    id              INTEGER PRIMARY KEY,
    wiki_page_id    INTEGER UNIQUE,
    name            TEXT NOT NULL,
    rarity          INTEGER,
    restriction     TEXT                    -- element restriction, or NULL if unrestricted
);

CREATE TABLE soul_carta_stats (
    soul_carta_id   INTEGER NOT NULL REFERENCES soul_carta(id),
    stat_name       TEXT NOT NULL,          -- ATK/HP/DEF/AGL/CRT (varies per item)
    base            INTEGER,
    max_lv          INTEGER,
    max_lv_uncaps   INTEGER,
    prism           INTEGER,
    PRIMARY KEY (soul_carta_id, stat_name)
);

CREATE TABLE soul_carta_enchantments (
    soul_carta_id   INTEGER NOT NULL REFERENCES soul_carta(id),
    enchant_level   TEXT NOT NULL,          -- Base / +1 / +2 / +3 / +4 / +5 / "Prism +5"
    effect_text     TEXT,
    PRIMARY KEY (soul_carta_id, enchant_level)
);

CREATE TABLE items (
    id              INTEGER PRIMARY KEY,
    wiki_page_id    INTEGER UNIQUE,
    name            TEXT NOT NULL,
    description     TEXT
);
```

`skills` / the exact stat-scaling curves are the biggest known gap: the
scraper stores raw `tables` (see `data/wiki/*.json`) for every page, but
turning those into the structured `skills` rows above needs a dedicated
per-section parser (skill headings look like `===Autoattack: Water
Attack===` followed by a two-row rank table). Worth doing before the server
needs to actually resolve combat — not needed just to stand up
login/roster/inventory.

## Player state (server-owned, empty at seed time)

```sql
CREATE TABLE accounts (
    id              INTEGER PRIMARY KEY,
    platform_id     TEXT UNIQUE NOT NULL,   -- maps to PlatformLoginRequest identity
    display_name    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE sessions (
    id              INTEGER PRIMARY KEY,
    account_id      INTEGER NOT NULL REFERENCES accounts(id),
    token           TEXT UNIQUE NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at      TEXT NOT NULL           -- driven by ApiServerSetting.sessionValidatePeriod
);

CREATE TABLE player_profile (
    account_id      INTEGER PRIMARY KEY REFERENCES accounts(id),
    level           INTEGER NOT NULL DEFAULT 1,
    exp             INTEGER NOT NULL DEFAULT 0,
    gold            INTEGER NOT NULL DEFAULT 0,
    gems            INTEGER NOT NULL DEFAULT 0
);

-- an owned copy of a child (players can own duplicates, each independently leveled)
CREATE TABLE player_children (
    id              INTEGER PRIMARY KEY,
    account_id      INTEGER NOT NULL REFERENCES accounts(id),
    child_id        INTEGER NOT NULL REFERENCES children(id),
    level           INTEGER NOT NULL DEFAULT 1,
    stars           INTEGER NOT NULL DEFAULT 1,
    exp             INTEGER NOT NULL DEFAULT 0,
    equipped_soul_carta_id INTEGER REFERENCES player_soul_carta(id),
    acquired_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE player_soul_carta (
    id              INTEGER PRIMARY KEY,
    account_id      INTEGER NOT NULL REFERENCES accounts(id),
    soul_carta_id   INTEGER NOT NULL REFERENCES soul_carta(id),
    level           INTEGER NOT NULL DEFAULT 1,
    enchant_level   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE player_items (
    account_id      INTEGER NOT NULL REFERENCES accounts(id),
    item_id         INTEGER NOT NULL REFERENCES items(id),
    quantity        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (account_id, item_id)
);

CREATE TABLE player_teams (
    id              INTEGER PRIMARY KEY,
    account_id      INTEGER NOT NULL REFERENCES accounts(id),
    slot            INTEGER NOT NULL,       -- team/formation slot number
    position        INTEGER NOT NULL,       -- position within the team
    player_child_id INTEGER REFERENCES player_children(id)
);
```

## Import path

`children` / `soul_carta` / `items` (+ their child tables) get populated by
a one-time import script reading `data/wiki/*.json` — not written yet.
Given ~40% of `children.json` entries are missing a parsed `infobox` (pages
that used a template shape the scraper doesn't handle, or genuine stubs),
the importer should skip/flag rows with no `hp`/`atk`/etc rather than
insert nulls silently.
