# Stack · Roblox (Luau, Rojo, Lune)

Setup for the first task and structure reference. Conventions: the `stack-roblox` skill.
The game lives as `.luau` text files synced into Studio by Rojo, so Git, worktrees, Paths and reviews work as in any
other stack. A `.rbxl`/`.rbxlx` place file is a build output, never the source of truth.

## Structure

```text
default.project.json            # owner: setup (Rojo tree); nobody edits it after
rokit.toml · wally.toml         # single owner (setup): pinned toolchain and packages
selene.toml · stylua.toml       # single owner (setup)
src/server/<f>/                 # ServerScriptService.Server.<f>: one feature per task
src/client/<f>/                 # StarterPlayerScripts.Client.<f>
src/shared/<f>/                 # ReplicatedStorage.Shared.<f>: pure logic, types, config (tested with Lune)
src/shared/Remotes.luau         # owner: the contracts task. Every RemoteEvent/RemoteFunction is declared here
src/shared/Theme.luau           # owner: design lock. Every Color3, font and UI size comes from here
src/client/ui/<f>/              # UI built in code for screen <f>
assets/<name>.rbxm              # binary models/maps exported from Studio: ONE owner each (OWNERS.md), never merged
tests/<f>.spec.luau             # Lune tests for src/shared/<f>
```
A task reserves `src/server/<f>/`, `src/client/<f>/`, `src/shared/<f>/` and `tests/<f>.spec.luau`.
Binary assets (`.rbxm`, `.rbxl`) cannot be merged: list each in `.uak/OWNERS.md` and edit it only in its owner's task.
Agents cannot edit the map in Studio; a task that needs map changes says so, and a human (or the asset owner) does them.

## UI paths
Roblox UI is not checked by the web screenshot gate (there is no browser), so the installer leaves `UI-Paths` empty.
A UI task attaches Studio screenshots (PC 1280×720 and a phone 390×844 from the Device emulator) to its PR when a human
can take them.
| What | Where | Owner |
|---|---|---|
| Theme tokens | `src/shared/Theme.luau` | design lock |
| UI kit (buttons, panels) | `src/client/ui/kit/` | design lock |
| HUD shell | `src/client/ui/hud/` | design lock |

## Setup (~10 min, once per machine)

```bash
# Rokit installs the pinned tools listed in rokit.toml (https://github.com/rojo-rbx/rokit)
rokit init && rokit add rojo-rbx/rojo && rokit add UpliftGames/wally && rokit add Kampfkarren/selene \
  && rokit add JohnnyMorganz/StyLua && rokit add JohnnyMorganz/luau-lsp && rokit add lune-org/lune
cp -r .uak/stacks/roblox/template/. .          # Rojo tree, lint config, Theme, Remotes, a sample module and its test
wally install                                  # only if wally.toml lists packages
rojo plugin install                            # once: the Studio plugin
rojo serve                                     # then in Studio: Rojo plugin → Connect
```
The installer git-ignores `*.rbxl`, `*.rbxlx`, `*.rbxl.lock`, `Packages/` and `ServerPackages/`: never commit them.

## Product smoke

```bash
bash .uak/bin/uak init-smoke --command "selene src && stylua --check src tests && lune run tests && rojo build -o /tmp/uak-game.rbxl"
```
No Studio needed: lint, format, the Lune tests of `src/shared` and a Rojo build that proves the tree is valid in the
merge gate's clean clone. Engine behavior (physics, replication, UI feel) is checked by a human playtest, not the gate.

## Test-first
Put game rules in pure modules under `src/shared/<f>/` (no `game:GetService` at require time; pass services in).
Lune runs them: `lune run tests` executes `tests/init.luau`, which runs every `tests/*.spec.luau` (or `lune run tests <f>`
for one). `uak red` needs a spec that fails on an assertion. Server and client glue stays thin and is covered by the
playtest.

## Run
`rojo serve --port $UAK_PORT` (each worktree its own port; point the Studio plugin at it), then Test → Start Server with
2 players to playtest replication.

## Publish
Publishing a place is outward-facing: only a human does it, or authorizes it explicitly (AGENTS.md §1.3). Keep a private
test place apart from the live one. With Open Cloud: `rojo build -o game.rbxl`, then upload it with an API key kept in
`.env` (`ROBLOX_API_KEY`, never committed, never read by agents).
