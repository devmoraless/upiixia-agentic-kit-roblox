---
name: stack-roblox
description: Conventions for the Roblox stack (Luau, Rojo, Lune tests, server authority, DataStores, mobile UI). Use when writing or reviewing any .luau file, a RemoteEvent, a DataStore call, UI built in code, or a test under tests/ in this repo.
---
# Roblox stack
Setup and structure: `.uak/stacks/roblox/STACK.md`.

| Rule | Why |
|---|---|
| One task = `src/{server,client,shared}/<f>/` + `tests/<f>.spec.luau`; never edit `default.project.json`, `Remotes.luau` or `Theme.luau` outside their owner task | disjoint claims; the Rojo tree is shared |
| `--!strict` on the first line of every module | luau-lsp catches nil and type bugs before a playtest |
| Game rules live in pure modules in `src/shared/<f>/`, services injected; Lune tests them | the merge gate has no Studio |
| The server is the authority: validate every RemoteEvent argument (type, range, rate, ownership) on the server; never trust the client for damage, currency, position or cooldowns | exploiters fire remotes with any values |
| Declare remotes only in `src/shared/Remotes.luau`; a new or changed remote is a contract change (`uak msg impact:ID --kind contract`) | consumers break silently |
| DataStore: every call in `pcall` with retries and backoff; save on `PlayerRemoving` and in `game:BindToClose`; version the schema (`data.version`) and migrate | data loss is the worst bug a game can ship |
| `task.wait`, `task.spawn`, `task.defer`; never `wait()`, `spawn()`, `delay()` | deprecated and throttled |
| No `while true do` without a yield; prefer events (`RunService.Heartbeat`, `Changed`, signals) to polling | frozen servers |
| Disconnect connections and destroy the instances you create (a Janitor/Trove per feature) | leaks in long-lived servers |
| Colors, fonts and sizes only from `Theme.luau`; UI sized with `Scale` + `UIScale`; touch targets ≥ 44 px; nothing under the mobile thumbstick or jump button | most players are on phones |
| `TextService:FilterStringAsync` for any player text shown to other players | Roblox policy: unfiltered text gets the game moderated |
| Never edit binary assets (`assets/*.rbxm`) or the map; ask the owner in `OWNERS.md` | binaries cannot be merged |
| Purchases (`MarketplaceService`), publishing a place and Open Cloud keys need explicit human authorization | AGENTS.md §1.3 |

```bash
bash .uak/bin/q selene src && stylua --check src tests && lune run tests <f>
```
