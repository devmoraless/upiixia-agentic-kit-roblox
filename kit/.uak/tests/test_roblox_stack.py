#!/usr/bin/env python3
"""The Roblox stack: `install.sh --stack roblox` places STACK.md, the stack-roblox skill, the smoke example and the Rojo
template; leaves out the web design chain (a game built in Studio has no browser to screenshot or landing to build);
sets no UI-Paths (done would ask for browser screenshots it cannot get); and git-ignores Rojo builds, Studio locks and
Wally packages. Real install.sh and real Git, never the network."""
import argparse
import tempfile
import time
from pathlib import Path

from test_hack import Runner, expect, resolve_binary
from test_skills_windows_clone import repo

WEB_SKILLS = ["frontend-design", "product-ui", "landing-story", "redesign-existing-projects", "webapp-testing",
              "vercel-react-best-practices"]


def install(r, d, mode):
    e = r.env.copy()
    e["UAK_EXTERNAL_SKILLS"] = "off"
    out = r.run([r.bash, str(r.package.parent / "install.sh"), "--mode", mode, "--stack", "roblox", str(d)], cwd=d, env=e)
    return out


def roblox_install_places_stack(r):
    for mode in ("sprint", "marathon"):
        d = repo(r, "roblox-" + mode)
        res = install(r, d, mode)
        tail = res.stdout[-600:]
        expect((d / ".uak/stacks/roblox/STACK.md").is_file(), mode + ": STACK.md placed: " + tail)
        expect((d / ".claude/skills/stack-roblox/SKILL.md").is_file(), mode + ": stack-roblox skill placed")
        expect((d / ".uak/bin/smoke-project.example").is_file(), mode + ": smoke example placed")
        tpl = d / ".uak/stacks/roblox/template"
        for f in ("default.project.json", "selene.toml", "src/shared/Theme.luau", "src/shared/Remotes.luau",
                  "tests/init.luau", "tests/score.spec.luau"):
            expect((tpl / f).is_file(), mode + ": template has " + f)
        expect((d / ".claude/skills/test-first/SKILL.md").is_file(), mode + ": the mode's own skills stay")
        overlay = d / ".uak/stacks/roblox/modes" / (mode + ".md")
        expect(overlay.is_file(), mode + ": the Roblox mode overlay is placed")
        expect(("modes/%s.md" % mode) in overlay.read_text(encoding="utf-8"), mode + ": the overlay names the mode it extends")
        agents = (d / "AGENTS.md").read_text(encoding="utf-8")
        expect(".uak/stacks/*/modes/<mode>.md" in agents, "AGENTS.md sends agents to the stack's mode overlay")
    return "sprint+marathon"


def roblox_install_drops_web_chain(r):
    d = repo(r, "roblox-web")
    install(r, d, "sprint")
    for s in WEB_SKILLS:
        expect(not (d / ".claude/skills" / s).exists(), "no web skill in a Roblox install: " + s)
    project = (d / ".uak/PROJECT.md").read_text(encoding="utf-8")
    expect("\nUI-Paths:" not in project, "no UI-Paths: the browser screenshot gate does not apply to Studio UI")
    ignore = (d / ".gitignore").read_text(encoding="utf-8").splitlines()
    for line in ("*.rbxl", "*.rbxlx", "*.rbxl.lock", "Packages/", "ServerPackages/"):
        expect(line in ignore, "git-ignores " + line)
    return "web chain out, ignores in"


def only_the_chosen_stack_and_update_keeps_it(r):
    d = repo(r, "roblox-update")
    install(r, d, "sprint")
    stacks = sorted(p.name for p in (d / ".uak/stacks").iterdir())
    expect(stacks == ["roblox"], "only the chosen stack is copied: %s" % stacks)
    r.g(d, "add", "-A")
    r.g(d, "commit", "-q", "-m", "kit")
    e = r.env.copy()
    e["UAK_EXTERNAL_SKILLS"] = "off"
    r.run([r.bash, str(r.package.parent / "install.sh"), "--mode", "sprint", "--update", str(d)], cwd=d, env=e)
    stacks = sorted(p.name for p in (d / ".uak/stacks").iterdir())
    expect(stacks == ["roblox"], "an --update without --stack keeps the project's stack: %s" % stacks)
    return "roblox only, kept on update"


TESTS = [roblox_install_places_stack, roblox_install_drops_web_chain, only_the_chosen_stack_and_update_keeps_it]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--case", action="append")
    args = parser.parse_args()
    fails = 0
    with tempfile.TemporaryDirectory(prefix="uak-roblox-") as tmp:
        runner = Runner(args.package.resolve(), Path(tmp), resolve_binary("bash"), resolve_binary("git"))
        for test in TESTS:
            if args.case and test.__name__ not in args.case:
                continue
            started = time.monotonic()
            try:
                note = test(runner)
                print("PASS %s (%s, %.2fs)" % (test.__name__, note, time.monotonic() - started))
            except Exception as exc:  # noqa: BLE001
                fails += 1
                print("FAIL %s (%s)" % (test.__name__, str(exc)[:2500]))
    print("ROBLOX_STACK_RESULT %s failed=%d" % ("PASS" if not fails else "FAIL", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
