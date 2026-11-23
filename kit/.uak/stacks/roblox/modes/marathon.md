# Marathon on Roblox · a live game

Read after `.uak/modes/marathon.md`. This file replaces its web parts for a Roblox game with real players; everything
else there still applies (specs, ADRs, protected main, humans merge, security reviews, conventional commits).

## What replaces what
| marathon.md says | On Roblox |
|---|---|
| NFRs: p95, availability, bundle budget | NFRs: server heartbeat ≥ 55 FPS with a full server, client memory budget on a low-end phone, join-to-play time, DataStore request budget per player, zero data-loss incidents |
| Validate at the edge (schemas), authorize per resource | Validate every RemoteEvent on the server (types, ranges, rate limit per player, ownership); the client is hostile |
| Migrations: expand → migrate → contract | Player data has `version`; every schema change ships a migration function and a Lune test that loads every old version |
| Deploy from day one (`uak deploy`), staging redeploys on merge | Two places: a **test place** gets every merge (a human publishes, or CI with Open Cloud once a human set it up); the **live place** gets a tested build on a release, by a human |
| Feature flags, rollback in `docs/runbook.md` | Flags in a config module (or a DataStore/MemoryStore-backed config); rollback = republish the previous place version from the version history, written in `docs/runbook.md` |
| Observability: logs, health, metrics | `AnalyticsService` funnels (join → first round → second session), error reporting from `ScriptContext.Error`, and the Creator Dashboard retention and performance pages, reviewed weekly |
| Frontend screens, design critic | UI built from `Theme.luau` and the UI kit; every screen checked on a phone, a tablet and a console layout (gamepad navigation) before release |

## Data (the worst bug a live game can ship)
1. One module owns player data. It uses `UpdateAsync` (never read-modify-write with `SetAsync`), a session lock so two
   servers never write the same profile, retries with backoff, and saves on `PlayerRemoving` and `BindToClose`.
2. Every change to the profile shape is a spec with a migration, its test, and a rollback note. Never delete a field
   in the same release that stops writing it.
3. Purchases: `ProcessReceipt` is idempotent (records the `PurchaseId` before granting) and returns `NotProcessedYet`
   on any failure. Its tests cover a duplicate receipt and a failed save.

## Security and policy (mandatory)
1. The `security-reviewer` subagent reviews every PR that adds or changes a remote, currency, inventory, trading,
   purchases or player text. A HIGH finding blocks the merge.
2. Rate-limit every remote per player; kick or flag on impossible values instead of trusting them.
3. Player-to-player text goes through `TextService` filtering; respect `PolicyService` (paid random items, social
   links, chat) per player. Experience Guidelines and age rating changes are a human `uak decision`.
4. Monetization (Game Passes, Developer Products, prices, subscriptions) is created and priced only by a human.

## Releases
1. A release = a tag + `CHANGELOG.md` + a playtest checklist run on the test place with 2+ players and a phone.
2. Live-ops changes (events, limited items, balance numbers) live in config modules with their own PRs, so they can be
   rolled back without a code change.
3. After each release, a human checks the Creator Dashboard for crash rate, server FPS and retention within 24 h and
   files regressions as tasks.
