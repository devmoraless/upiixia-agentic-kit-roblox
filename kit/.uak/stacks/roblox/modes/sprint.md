# Sprint on Roblox · game jams

Read after `.uak/modes/sprint.md`. This file replaces its web parts for a Roblox game; everything else there still
applies (clock, freeze, test-first, merge as soon as approved, at most 2 agents per human).

## What replaces what
| sprint.md says | On Roblox |
|---|---|
| Win the rubric with a demo; the frontend IS the product | Win with a game people want to replay: the **core loop** IS the product |
| Wow moment within 90 s, visible at 1280×720 | The core loop is playable within **30 s of joining**, with no tutorial wall, on PC and on a phone |
| T0+2h: walking skeleton **deployed** (`uak deploy`) | T0+2h: the core loop playable end to end in Studio, then **published by a human to a private test place**; every merge after that is a new playtest build |
| `/uak-design-lock`: 3 visual directions, `web/DESIGN.md` | Design lock = `Theme.luau`, the HUD shell and the UI kit (`src/client/ui/kit/`), plus a one-page art direction in `IDEA.md` (palette, mood, 3 reference games). No browser screenshots |
| Landing page, `landing-story`, `product-ui` | None. The game's icon, thumbnails and description are a human task in the last hour |
| Mocks with `demo_data: true` | Placeholder parts and free-model stand-ins are fine, labeled `PLACEHOLDER` in their name; never ship an unlabeled one |
| Plan-B video at T-50% | Plan-B video of a full round at T-50% (Studio recording) in case the servers or the place fail during judging |

## Plan
1. Every P0 maps to the jam's theme or a rubric criterion; if a player never sees it in the first round, it is not P0.
2. Wave 1 (one task per agent, no hard dependency):
   - **contracts**: `Remotes.luau` with every remote the loop needs, and the shared types;
   - **player data**: the profile module (pure, tested) and its DataStore adapter with a session lock;
   - **core loop rules**: the pure module that decides scoring, rounds, win/lose (tested with Lune);
   - **map blockout**: a human or the asset owner in Studio, with spawn points named as the code expects;
   - **spike**: the riskiest engine feature (physics, pathfinding, many NPCs) proven in a throwaway place.
3. Wave 2: server feature modules, client feedback (sound, VFX, camera shake: game feel), the HUD.
4. Tasks take 60 min or less with disjoint `src/*/<f>/` Paths. The map and every `.rbxm` have one owner.

## Playtest instead of browser checks
1. Every merged wave gets a **playtest**: Test → Start Server with 2+ players in Studio, then a phone in the Device
   emulator. One human owns it and writes the findings as `uak msg all --kind contract` or new tasks.
2. Before `done` on a gameplay task: Lune tests green, the task's Verify, and one line of evidence from a local
   playtest ("2 players, round ended, scores replicated"). A task an agent cannot playtest says so in its evidence and
   asks the human: `uak msg human "playtest ID: what to try"`.
3. Game feel is part of done: every player action has feedback (sound, animation or VFX) within 100 ms.

## Last hours
1. Freeze: only bug fixes from the playtest. No new mechanics.
2. T-1h: a human publishes the final build, sets the place public (or as the jam asks), checks it on a phone and saves the link.
3. Never let an agent publish, change place settings, or add Developer Products / Game Passes: those are human steps.
