#!/usr/bin/env python3
"""design-lint on a Roblox (Rojo) project: Luau feature code under src/ that types its own Color3, font or emoji fails,
while src/**/Theme.luau, the UI kit (src/client/ui/kit/), specs and lines marked "design-lint: ok" pass. Without a
Theme.luau it is a skip; --file and --changed work as on the web. Why: the Roblox stack puts every color, font and size
in Theme.luau, and design-lint passed any Luau file before (it only read .ts/.tsx/.js)."""
import argparse
import tempfile
import time
from pathlib import Path

from test_hack import Runner, expect, resolve_binary
from test_v43 import push_main

THEME = "--!strict\nreturn { color = { accent = Color3.fromRGB(255, 176, 32) }, font = Enum.Font.GothamBold }\n"
CLEAN = "--!strict\nlocal Theme = require(script.Parent.Parent.Shared.Theme)\nlocal f = Instance.new('Frame')\nf.BackgroundColor3 = Theme.color.accent\n"


def project(r, name, files):
    t = r.scratch / ("dl-" + name)
    t.mkdir(parents=True)
    r.g(t, "init", "-q", "-b", "main")
    (t / "default.project.json").write_text('{"name": "Game", "tree": {"$className": "DataModel"}}\n', encoding="utf-8")
    for path, text in files.items():
        p = t / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return t


def lint(r, t, *args):
    return r.run([r.bash, str(r.package / ".uak/bin/design-lint"), *args], cwd=t, allowed=None)


def findings(out):
    return [l for l in out.stdout.splitlines() if l.startswith("DESIGN_LINT ")]


def luau_literals_fail(r):
    t = project(r, "fail", {
        "src/shared/Theme.luau": THEME,
        "src/client/ui/kit/Button.luau": "local c = Color3.fromRGB(1, 2, 3)\nlocal f = Enum.Font.Gotham\n",
        "src/client/ui/shop/init.luau": "--!strict\nlocal b = Instance.new('TextButton')\nb.BackgroundColor3 = Color3.fromRGB(200, 40, 40)\n"
                                        "b.Font = Enum.Font.Arcade\nb.Text = 'Buy \U0001F525'\nb.TextColor3 = Color3.new(1, 1, 1) -- design-lint: ok (contrast test)\n",
        "src/shared/score/score.spec.luau": "local c = Color3.fromRGB(0, 0, 0)\n",
    })
    out = lint(r, t)
    lines = findings(out)
    expect(out.returncode == 1 and "DESIGN_LINT_FAIL 3 finding(s)" in out.stdout, "3 findings in feature code: %s" % out.stdout)
    expect(any("shop/init.luau:3 · Color3 literal" in l and "Theme.luau" in l for l in lines), "the Color3 names the theme: %s" % lines)
    expect(any("shop/init.luau:4 · font in feature code" in l for l in lines), "the font: %s" % lines)
    expect(any("shop/init.luau:5 · emoji" in l for l in lines), "the emoji: %s" % lines)
    expect(not any("kit/" in l or "Theme.luau:" in l or ".spec.luau" in l for l in lines), "kit, theme and specs are exempt: %s" % lines)
    return "3 findings, exemptions hold"


def luau_clean_passes_and_no_theme_skips(r):
    t = project(r, "clean", {"src/shared/Theme.luau": THEME, "src/client/ui/hud/init.luau": CLEAN})
    out = lint(r, t)
    expect(out.returncode == 0 and "DESIGN_LINT_PASS" in out.stdout, "theme-only code passes: %s" % out.stdout)
    t2 = project(r, "notheme", {"src/client/ui/hud/init.luau": "local c = Color3.fromRGB(1, 2, 3)\n"})
    o2 = lint(r, t2)
    expect(o2.returncode == 0 and "DESIGN_LINT_SKIP" in o2.stdout and "Theme.luau" in o2.stdout, "no theme yet is a skip: %s" % o2.stdout)
    return "pass and skip"


def luau_file_and_changed(r):
    t = project(r, "scoped", {"src/shared/Theme.luau": THEME, "src/client/ui/old/init.luau": "local c = Color3.fromRGB(9, 9, 9)\n"})
    r.g(t, "add", "-A")
    r.g(t, "-c", "user.name=a", "-c", "user.email=a@example.invalid", "commit", "-q", "-m", "base")
    r.g(t, "update-ref", "refs/remotes/origin/main", "HEAD")
    (t / "src/client/ui/new").mkdir(parents=True)
    (t / "src/client/ui/new/init.luau").write_text("local c = Color3.fromHex('#ff0000')\n", encoding="utf-8")
    r.g(t, "add", "-A")   # done runs after the agent's commits: git diff sees tracked files only
    one = lint(r, t, "--file", "src/client/ui/new/init.luau")
    expect(one.returncode == 1 and all("new/init.luau" in l for l in findings(one)) and findings(one), "--file reads one file: %s" % one.stdout)
    ch = lint(r, t, "--changed", "main")
    lines = findings(ch)
    expect(ch.returncode == 1 and len(lines) == 1 and "new/init.luau:1" in lines[0], "--changed keeps only added lines: %s" % ch.stdout)
    return "--file and --changed"


def the_hook_lints_luau_after_an_edit(r):
    """The post-edit hook runs design-lint on a .luau file an agent writes, and points to stack-roblox."""
    import json
    f = r.fixture("dl-luau-hook", paths={"HACK-001": "src/client/ui/a/"}, count=1)
    push_main(f, {"default.project.json": '{"name": "Game", "tree": {"$className": "DataModel"}}\n',
                  "src/shared/Theme.luau": THEME}, "rojo tree and theme")
    w = f.worktrees[0]
    r.g(w, "merge", "-q", "origin/main")
    (w / ".uak-env").write_text("UAK_AGENT=agent-1\nUAK_TASK=HACK-001\n", encoding="utf-8")
    view = w / "src/client/ui/a/init.luau"
    view.parent.mkdir(parents=True, exist_ok=True)
    view.write_text("local c = Color3.fromRGB(10, 20, 30)\n", encoding="utf-8")
    payload = {"session_id": "s1", "hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": str(view)}}
    (w / ".git-payload.json").write_text(json.dumps(payload), encoding="utf-8")
    tick = r.run([r.bash, "-c", "bash .uak/bin/hook tick < .git-payload.json"], cwd=w, env={"UAK_NOW": "1000100"}, allowed=None)
    expect("UAK design-lint on init.luau" in tick.stdout and "Color3 literal" in tick.stdout and "stack-roblox" in tick.stdout,
           "the agent hears it after the edit: " + tick.stdout)
    view.write_text("local Theme = require(script.Parent)\nlocal c = Theme.color.accent\n", encoding="utf-8")
    clean = r.run([r.bash, "-c", "bash .uak/bin/hook tick < .git-payload.json"], cwd=w, env={"UAK_NOW": "1000101"}, allowed=None)
    expect("design-lint" not in clean.stdout, "a clean file says nothing: " + clean.stdout)
    return "hook"


TESTS = [luau_literals_fail, luau_clean_passes_and_no_theme_skips, luau_file_and_changed, the_hook_lints_luau_after_an_edit]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--case", action="append")
    args = parser.parse_args()
    fails = 0
    with tempfile.TemporaryDirectory(prefix="uak-dlint-luau-") as tmp:
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
    print("DESIGN_LINT_LUAU_RESULT %s failed=%d" % ("PASS" if not fails else "FAIL", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
