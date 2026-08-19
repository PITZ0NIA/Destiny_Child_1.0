# Destiny Child 1.0

Fan preservation project to bring up a local/private server for **Destiny
Child** (Shift Up), a gacha RPG whose official servers shut down globally
on 2023-09-21. Personal-use revival, built from client analysis and
community-sourced data — no official assets or proprietary source are
included in this repository (see `docs/data-sources.md`).

Destiny Child was Android/iOS only - there was never an official PC client.
Rather than run the original APK through an Android emulator, `client/` is a
from-scratch native Windows client (new Unity project, our own code) that
talks to `server/`'s API.

## Status

- [x] Identify engine/build (Unity 2019.4.40f1, IL2CPP) and package
      (`com.ta.dcdw.gl`)
- [x] Map the client's network-layer class structure (`docs/network-protocol.md`)
- [x] Recover production/QA server hostnames from embedded client strings
- [x] Source a character/equipment/item stat dataset from the community wiki
      (`data/wiki/`)
- [x] Design the local server's database schema (`docs/database-schema.md`)
- [x] Scaffold the local server (init, login/session, catalog, roster —
      see `server/README.md`), verified working end-to-end
- [x] Scaffold a native Windows client, Phase 1: login + character catalog
      (`client/README.md`) - written, not yet build-verified (needs Unity
      installed, which is a manual/interactive step)
- [ ] Endpoints for actually granting/leveling characters, teams, gacha
- [ ] Pull extracted character art into the native client
- [ ] Fill remaining protocol gaps (exact JSON shapes, any request signing)

## Layout

```
docs/            Our own written analysis and design notes
  network-protocol.md   what we learned about the client's API layer
  data-sources.md        attribution / provenance for data/
  database-schema.md     (WIP) local server DB design
scripts/         Tools used to extract data (not game content itself)
  extract_urls.py         pulls URL-like strings out of a Unity asset bundle
  explore_bundle.py       lists object types/names in a Unity AssetBundle
  list_monoscripts.py     lists MonoScript class names in a bundle
  scrape_wiki.py          scrapes the community wiki via its MediaWiki API
data/wiki/       Character/equipment/item stats scraped from the community
                 wiki (CC BY-SA, see docs/data-sources.md)
server/          Local server (Python/FastAPI/SQLite) - see server/README.md
client/          Native Windows client, from scratch (Unity) - see client/README.md
```

Not in this repo (kept local only — see `.gitignore` and
`docs/data-sources.md` for why): the original APK, JADX decompile output,
the IL2CPP dump, and extracted game art/audio/model assets. All of that is
either the copyrighted game binary itself or reverse-engineered proprietary
code, not something we wrote.

## Legal note

This project is for personal offline play of a game whose official service
has been fully discontinued. It does not host, distribute, or link to the
original game client, its assets, or any decompiled/reverse-engineered
source code — only our own server code, our own analysis notes, and a
community-maintained stats dataset (attributed, CC BY-SA).
