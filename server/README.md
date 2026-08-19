# Local server

Python + FastAPI + SQLite. Implements the subset of the client's API layer
documented in `../docs/network-protocol.md`: init, login/session, and a
read-only character catalog + roster.

## Setup

```
pip install -r requirements.txt
python scripts/import_wiki_data.py   # seeds children/soul_carta/items from ../data/wiki/*.json
python -m uvicorn app.main:app --reload
```

Server runs at `http://127.0.0.1:8000`. SQLite file is created at
`server/destiny_child.db` (gitignored — regenerate anytime by re-running the
import script; it upserts by wiki page id so it's safe to re-run).

## Endpoints implemented so far

| Endpoint | Mirrors | Auth |
|---|---|---|
| `GET /api/init` | `InitRequest` | none |
| `POST /api/login` | `RequestLogin` | none (no real platform auth - local server) |
| `POST /api/session/validate` | `SessionValidateRequest` | `X-Session-Token` header |
| `POST /api/session/logout` | `SessionLogoutRequest` | `X-Session-Token` header |
| `GET /api/catalog/children` | `GetTablesByDistributeIdRequest` (master data) | none |
| `GET /api/roster` | — (new, not from the original client) | `X-Session-Token` header |

Response envelope on every endpoint: `{"data": ..., "error": null,
"localTimeInfo": {...}}`, matching the `HttpResponseBody<T>` shape observed
in the client (see `../docs/network-protocol.md`).

Quick manual test:

```
curl -X POST http://127.0.0.1:8000/api/login -H "Content-Type: application/json" \
  -d '{"platform_id":"me","display_name":"Player"}'
# copy sessionToken from the response, then:
curl http://127.0.0.1:8000/api/roster -H "X-Session-Token: <token>"
```

## Not built yet

- Granting/leveling `player_children` (there's no endpoint to actually gain
  a character yet — roster will stay empty until one exists).
- `skills`, `soul_carta_stats`, `soul_carta_enchantments`,
  `child_relations`, `player_teams` (schema exists in
  `../docs/database-schema.md`, no ORM models/import logic yet).
- Anything matching the real client's exact request/response field names -
  the shapes above are our own best guess from the class structure, not
  confirmed against real traffic.
