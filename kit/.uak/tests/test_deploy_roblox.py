#!/usr/bin/env python3
"""uak deploy on a Rojo project (the Roblox stack): it says the place is published with Open Cloud and names the
variables (never their values); --write creates scripts/publish-place.sh and an opt-in CI example, never over an
existing file; the script refuses to run as an agent, and --live sends nothing unless a human types the place ID.
Real bash and Git, never the network (every case stops before rojo or curl). Why: the generic deploy proposed nothing
for a game ("no known stack"), and publishing a place is the one deploy step that must stay a human's."""
import argparse
import tempfile
import time
from pathlib import Path

from test_hack import Runner, expect, resolve_binary


def project(r, name):
    t = r.scratch / ("dr-" + name)
    t.mkdir(parents=True)
    r.g(t, "init", "-q", "-b", "main")
    (t / "default.project.json").write_text('{"name": "Game", "tree": {"$className": "DataModel"}}\n', encoding="utf-8")
    return t


def deploy(r, t, *args):
    return r.run([r.bash, str(r.package / ".uak/bin/deploy"), *args], cwd=t, allowed=None)


def plan_names_the_place_and_the_variables(r):
    t = project(r, "plan")
    out = deploy(r, t)
    expect(out.returncode == 0 and "DEPLOY roblox" in out.stdout and "Open Cloud" in out.stdout, out.stdout + out.stderr)
    for v in ("ROBLOX_API_KEY", "ROBLOX_TEST_PLACE_ID", "ROBLOX_LIVE_PLACE_ID"):
        expect(v in out.stdout, "names " + v)
    expect("universe:publish" in out.stdout, "the key's permission is named")
    expect(not (t / "scripts").exists() and not (t / "render.yaml").exists() and not (t / "Dockerfile").exists(),
           "without --write nothing is created, and no web deploy files ever")
    return "plan"


def write_creates_files_and_keeps_yours(r):
    t = project(r, "write")
    out = deploy(r, t, "--write")
    script = t / "scripts/publish-place.sh"
    wf = t / ".github/workflows/roblox-publish-test.yml.example"
    expect(out.returncode == 0 and script.is_file() and wf.is_file(), out.stdout)
    body = script.read_text(encoding="utf-8")
    expect("apis.roblox.com/assets/v1/assets/" in body and "x-api-key" in body and 'published' in body and 'assetType' in body, "Open Cloud Assets API")
    expect("rojo build" in body and "ROBLOX_TEST_PLACE_ID" in body and "--live" in body, "builds, test place by default")
    expect(r.run([r.bash, "-n", str(script)], cwd=t, allowed=None).returncode == 0, "the script parses")
    expect("ROBLOX_LIVE_PLACE_ID" not in wf.read_text(encoding="utf-8"), "CI publishes only the test place")
    script.write_text("# mine\n", encoding="utf-8")
    again = deploy(r, t, "--write")
    expect(script.read_text(encoding="utf-8") == "# mine\n" and (t / "scripts/publish-place.sh.uak-new").is_file(),
           "an existing script is kept; the proposal goes beside it: " + again.stdout)
    return "files"


def the_script_refuses_agents_and_unconfirmed_live(r):
    t = project(r, "guard")
    deploy(r, t, "--write")
    env = {"ROBLOX_API_KEY": "test-not-a-key", "ROBLOX_TEST_PLACE_ID": "1", "ROBLOX_LIVE_PLACE_ID": "2"}
    agent = r.run([r.bash, "scripts/publish-place.sh"], cwd=t, env=dict(env, UAK_AGENT="agent-1"), allowed=None)
    expect(agent.returncode == 3 and "human step" in agent.stderr, "an agent is refused: %d %s" % (agent.returncode, agent.stderr))
    (t / ".uak-env").write_text("UAK_AGENT=agent-1\nUAK_TASK=HACK-001\n", encoding="utf-8")
    wt = r.run([r.bash, "scripts/publish-place.sh"], cwd=t, env=env, allowed=None)
    expect(wt.returncode == 3, "an agent's worktree is refused too: %d %s" % (wt.returncode, wt.stderr))
    (t / ".uak-env").unlink()
    no_key = r.run([r.bash, "scripts/publish-place.sh"], cwd=t, env={"ROBLOX_API_KEY": "", "UAK_HUMAN": "ana"}, allowed=None)
    expect(no_key.returncode != 0 and "ROBLOX_API_KEY" in no_key.stderr, "no key, no call: " + no_key.stderr)
    live = r.run([r.bash, "-c", "echo 999 | bash scripts/publish-place.sh --live"], cwd=t, env=dict(env, UAK_HUMAN="ana"), allowed=None)
    expect(live.returncode == 1 and "not confirmed" in live.stderr and not (t / "build").exists(),
           "live without the right place ID sends and builds nothing: %d %s" % (live.returncode, live.stderr))
    return "guards"


TESTS = [plan_names_the_place_and_the_variables, write_creates_files_and_keeps_yours, the_script_refuses_agents_and_unconfirmed_live]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--case", action="append")
    args = parser.parse_args()
    fails = 0
    with tempfile.TemporaryDirectory(prefix="uak-deploy-roblox-") as tmp:
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
    print("DEPLOY_ROBLOX_RESULT %s failed=%d" % ("PASS" if not fails else "FAIL", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
