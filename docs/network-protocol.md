# Network Protocol Notes

Findings from analyzing the Global client (`destiny-child-defense-war-2-15-2.apk`,
package `com.ta.dcdw.gl`, Unity 2019.4.40f1 / IL2CPP). These are our own notes
written from observing the client's class structure and embedded strings —
not a redistribution of decompiled source.

## Engine / build

- Unity 2019.4.40f1, IL2CPP scripting backend.
- Game logic lives natively in `lib/armeabi-v7a/libil2cpp.so`, typed via
  `assets/bin/Data/Managed/Metadata/global-metadata.dat`.
- The Android Java/Kotlin layer (`com.ta.dcdw.gl`) is just the Unity
  activity shell; it carries no gameplay logic.

## Server environments

`ApiServerSetting.EApiServer` (enum found in the IL2CPP metadata) lists the
known deploy targets:

| Name | Value | Host (from embedded strings) |
|---|---|---|
| Sandbox1/2/3 | 0/1/2 | `d-sg-sb1/2/3.skeinglobe.com` |
| Branch1/2/3 | 10/20/30 | `d-sg-br1/2/3.skeinglobe.com` |
| SG_QA1/2 | 50/60 | — |
| EX1-4 | 70-73 | `d-ex1-4.skeinglobe.com` |
| Grinder | 115 | `d-sg-grinder.skeinglobe.com` |
| Box14 | 114 | `box14.skeinglobe.com` |
| Box24 | 118 | `box24.skeinglobe.com` |
| DCDW_QA | 116 | `qa-child-api01.thumbage.net` |
| DCDW_Live | 117 | `child-api.thumbage.net` (production) |

Patch/CDN host: `destiny-child-defense-war.thumbage.co.kr` — **still resolves
in DNS** as of 2026-08-19 (61.100.186.142/141), answers plain HTTP with a
generic 404 on `/`. Not explored further (no path brute-forcing against a
third-party host without deciding that deliberately first).

`child-api.thumbage.net` and the `skeinglobe.com` hosts no longer resolve.

## Request/response shape (from IL2CPP class layout)

Requests follow a generic pattern:

```
HttpRequest<TResponse, TExtraData>
├── InitRequest : HttpRequest<InitResponse, InitResponseExtraData>
├── PlatformLoginRequest : HttpRequest<PlatformLoginResponse, ExtraDataBase>
├── PlatformSignUpRequest : HttpRequest<PlatformSignUpResponse, ExtraDataBase>
├── RequestLogin : HttpRequest<LoginResponse, LoginExtraData>
├── SessionValidateRequest : HttpSessionRequest<SessionValidateResponse, ExtraDataBase>
├── SessionLogoutRequest : HttpSessionRequest<SessionValidateResponse, ExtraDataBase>
└── GetTablesByDistributeIdRequest : HttpRequestForJsonData
```

Responses are wrapped generically:

```
HttpResponseBody<T>
├── Error<T>
├── LocalTimeInfo<T>
└── ExtraData<T>

HttpResponseBody<T, TE>  (adds a typed extra-data payload TE)
```

This implies a JSON envelope shape roughly like:

```json
{
  "data": { /* T */ },
  "error": { /* present on failure */ },
  "localTimeInfo": { /* server clock sync */ },
  "extraData": { /* TE, request-specific */ }
}
```

`HttpSessionValidator` + `ApiServerSetting.sessionValidatePeriod` /
`sessionValidateRetryPeriod` imply the client periodically re-validates its
session token on an interval, with a separate retry interval on failure.

`GetTablesByDistributeIdRequest` (`HttpRequestForJsonData`) is the most
likely candidate for how master/balance data (card stats, drop tables,
gacha rates) was fetched — **confirmed not present anywhere in the shipped
client assets** (see `docs/database-schema.md` for what we had to source
from the community wiki instead).

## Possible realtime layer (unconfirmed)

The dump also contains `AsyncTcpSession`, `SslStreamTcpSession`,
`SocketAsyncEventArgs` — these match the shape of the open-source
**SuperSocket.ClientEngine** library rather than custom protocol code, so
they may just be a bundled dependency and not proof of a raw TCP gameplay
protocol. `EventSource : IProtocol, IHeartbeat` suggests a Server-Sent
Events client for push/notification delivery over HTTP. Neither has been
investigated further yet — flagging as a follow-up if we need realtime
(PVP/raid) support.

## What's still unknown

- Exact request/response JSON field names and encoding (any custom
  encryption, compression, or signing on top of HTTPS) — not yet reversed
  at the instruction level (would require disassembling the relevant
  IL2CPP functions in Ghidra using the generated `script.json`).
- Auth flow details (`PlatformLoginRequest` vs `RequestLogin` — likely
  first authenticates against a platform, e.g. Google Play Games, then
  exchanges for a game session).
