# Native Windows client (Phase 1: login + roster)

Destiny Child never had an official PC client - it was Android/iOS only. This
is a from-scratch Windows client that talks to `../server`, reusing the
scripts here. Phase 1 only proves the pipeline works: login against the
local server, then list the character catalog. No combat/gacha/assets yet.

The UI is built **entirely at runtime by code** (`Bootstrap.cs`) rather than
as a hand-authored `.unity` scene - that was a deliberate choice so this
folder can just contain plain C# files instead of fragile, hard-to-diff
Unity scene/meta files that only make sense once opened in the Editor.

## 1. Install Unity

You need to do this part yourself - it requires signing into a Unity
account, which isn't something that can be scripted from a terminal.

1. Install **Unity Hub**: https://unity.com/download
2. In Unity Hub, install Editor version **2019.4.40f1** (LTS) - matches the
   original game's Unity version, which matters later if we start pulling
   in the extracted assets (materials/shaders are version-sensitive).
3. When installing, make sure the **Windows Build Support (IL2CPP/Mono)**
   module is checked.

## 2. Create the project

1. In Unity Hub: New Project -> **3D (Built-In Render Pipeline)** template
   (not URP/HDRP - keeps things simple and matches the original's render
   pipeline) -> name it whatever you like, e.g. `DestinyChildClient`.
2. Once it opens, close the sample scene it creates, or just work in it -
   doesn't matter, Phase 1 doesn't use any scene content.

## 3. Drop in the scripts

Copy the contents of this folder's `Assets/Scripts/` into your new
project's `Assets/Scripts/` (e.g. drag the `Scripts` folder from
`client/Assets/Scripts` into `<YourProject>/Assets/` in Windows Explorer,
or into the Project window inside Unity). Unity will auto-generate `.meta`
files for them on import - that's normal and expected.

## 4. Wire up the scene

1. In the open scene, create an empty GameObject (right-click Hierarchy ->
   Create Empty), rename it `Bootstrap`.
2. Add the `Bootstrap` component to it (drag `Bootstrap.cs` onto it, or
   Add Component -> search "Bootstrap").
3. That's it - `Bootstrap.Start()` builds the Canvas/EventSystem/UI itself.

## 5. Run it

1. Start the local server first (see `../server/README.md`):
   ```
   cd ../server
   python -m uvicorn app.main:app
   ```
2. Press Play in the Unity Editor.
3. Type any Player ID (this is a local server - `platform_id` is trusted
   as given, no real platform auth) and click Login.
4. You should see the character catalog load from
   `GET /api/catalog/children` - 299 entries with real stats from the
   community wiki dataset.

If login fails with a connection error, double check the server is running
on `http://127.0.0.1:8000` (`ApiClient.BaseUrl` in
`Assets/Scripts/Api/ApiClient.cs` if you need to point it elsewhere).

## What's next (not built yet)

- Pulling in the actual extracted character art/portraits instead of a
  plain text list (needs deciding how to get assets from
  `apk_desmantelada/resources/assetpack/` into the Unity project without
  just re-importing copyrighted bundles wholesale).
- A real roster (currently `/api/roster` is always empty - there's no
  "acquire a character" endpoint on the server yet).
- Everything else: combat, gacha, story, etc.
