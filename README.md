<div align="center">

# UPIIXIA Agentic Kit · Roblox

### Build Roblox games with a team of AI coding agents, in parallel, without chaos.

**Multi-agent coordination for Claude Code, Codex, Cursor and Gemini CLI, set up for Roblox: Rojo, Luau, Lune, selene
and StyLua.** Agents claim tasks, write tests first, review each other and merge through a gate. It works for several
humans and machines with **no server**: everything lives on a Git branch, and the engine needs only Bash and Git.

**`sprint`** for game jams · **`marathon`** for a live game with players

![license](https://img.shields.io/badge/license-MIT-blue)
![deps](https://img.shields.io/badge/runtime_deps-bash_%2B_git-success)
![stack](https://img.shields.io/badge/stack-Rojo_·_Luau_·_Lune-00A2FF)

</div>

---

> Fork of [UPIIXIA Agentic Kit](https://github.com/JoahanMorales/upiixia-agentic-kit), a hackathon harness for web apps.
> This fork drops the web stacks and adds the Roblox stack, game-specific modes, a Luau design lint and a
> human-only place publisher. The coordination engine is unchanged.

## Quick start

You need:
- Git and Bash (on Windows, Git Bash);
- Roblox Studio;
- [Rokit](https://github.com/rojo-rbx/rokit) to install the pinned toolchain.

```bash
git clone --depth 1 https://github.com/devmoraless/upiixia-agentic-kit-roblox ~/.uak-kit
cd my-game && git init -b main
bash ~/.uak-kit/install.sh --mode sprint --stack roblox .     # or --mode marathon for a live game
bash .uak/bin/uak start                                       # every step to the first claim, in order
```
Other options:
- `--harness claude,codex`: only the folders of the tools you use;
- `--solo`: you are the only human on the GitHub repo;
- `--no-mcp`: CLI only;
- `--update`: refresh the engine later.

The first task copies `.uak/stacks/roblox/template/` and installs the tools. Run `rojo serve`, then in Studio click
the Rojo plugin's **Connect** button. The full setup is in [STACK.md](kit/.uak/stacks/roblox/STACK.md).

You can also install it as a Claude Code plugin:
1. Run `/plugin marketplace add devmoraless/upiixia-agentic-kit-roblox`.
2. Run `/plugin install uak@upiixia-agentic-kit`.
3. Run `/uak:setup`.

## How a game is laid out

The game is plain `.luau` files that Rojo syncs into Studio. Because of that, Git, worktrees, reviews and the merge
gate work the same way they do for any code. A `.rbxl` place file is a build output, never the source of truth.

```text
default.project.json      Rojo tree (owner: setup)
src/server/<feature>/     ServerScriptService: one feature per task
src/client/<feature>/     StarterPlayerScripts
src/shared/<feature>/     pure game rules, tested with Lune
src/shared/Remotes.luau   every RemoteEvent/RemoteFunction (one owner: the contracts task)
src/shared/Theme.luau     every Color3, font and UI size (one owner: the design lock)
tests/<feature>.spec.luau Lune specs
assets/*.rbxm             binary models: one owner each, never merged
```

A task reserves the folders of its feature, so two agents never edit the same files. Map edits in Studio stay a human
step.

## What the kit adds for Roblox

| Piece | What it does |
|---|---|
| `--stack roblox` | Installs the Rojo template, the `stack-roblox` skill, the product smoke and the `.gitignore` entries. Web design skills are not installed. |
| [Modes](kit/.uak/stacks/roblox/modes/) | `sprint.md` is for game jams: the core loop playable first, a playtest build at every merge, a freeze before the deadline. `marathon.md` is for a live game: DataStore safety, server authority, the test place before live. |
| Product smoke | Runs `selene`, then `stylua --check`, then `lune run tests`, then `rojo build`. It runs in the merge gate's clean clone without Studio. |
| `uak design-lint` (Luau) | Flags `Color3`, fonts and emoji in feature code. They belong in `Theme.luau` or the UI kit. It runs after every edit and at `uak done`. |
| design-critic | Judges a UI task from Studio screenshots on PC (1280×720) and phone (390×844). |
| `uak deploy --write` | Creates `scripts/publish-place.sh`, which publishes through Open Cloud. It targets the test place by default, and `--live` asks you to type the place ID. The script refuses to run as an agent. |

**Agents never publish a place.** Publishing is a human step. `ROBLOX_API_KEY` stays in your shell or in CI secrets,
never in git.

## Two modes, one engine

The human picks the mode in `.uak/PROJECT.md`, and agents never change it.

| | sprint (game jam) | marathon (live game) |
|---|---|---|
| Goal | A playable game by the deadline | A game players keep coming back to |
| Merge | As soon as another agent approves | A human merges; CI required |
| Data | A profile module with a session lock | Versioned DataStores, session locks, migrations |
| Publish | A private test place, by a human | Test place, then live, by a human |

## How it works

- **Claims and leases.** A task is claimed on the `claims` branch, and a lease expires if its agent dies, so nothing
  stays locked.
- **Test-first.** `uak red` records a failing Lune spec before the code exists, and `uak done` refuses weakened tests.
- **Review and merge gate.** Another agent reviews the exact commit. The gate rebuilds in a clean clone and runs the
  product smoke before merging.
- **Bounded loops.** `uak loop` runs verify → fix and stops when nothing improves.
- **Task graph.** `uak graph` orders tasks into waves, and `uak next` hands out the next free one.
- **Tokens and pacing.** `uak tokens` shows real spend per task, and `uak pace` spreads use over the plan's windows.
- **Dashboard.** `uak dash` shows the board, reviews and timelines.

## Docs

- [AGENTS.md](kit/AGENTS.md): the rules every agent follows
- [Roblox stack](kit/.uak/stacks/roblox/STACK.md) and [stack-roblox skill](kit/.uak/stacks/roblox/skills/stack-roblox/SKILL.md)
- [CLI](kit/.uak/docs/CLI.md): every command
- [Protocol](kit/.uak/docs/PROTOCOL.md): claims, leases, reviews, merges
- [Orchestration](kit/.uak/docs/ORCHESTRATION.md): which model does what
- [Costs](kit/.uak/docs/COSTS.md) · [Loops](kit/.uak/docs/LOOPS.md) · [Graph](kit/.uak/docs/GRAPH.md) · [Security](kit/.uak/docs/SECURITY.md)
- [Why each rule exists](kit/.uak/docs/WHY.md)
- [Architecture](docs/ARCHITECTURE.md): where to change what in the engine

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). The rules:
- every engine change ships with a test that fails without it;
- every new rule gets a row in `WHY.md`;
- code and docs are in English.

## License

MIT. Third-party skills keep their own licenses ([SOURCES.md](kit/.uak/skills/SOURCES.md)).
