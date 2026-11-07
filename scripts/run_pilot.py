"""Pilot runner: one model, all (task, arm) cells, N attempts each, weights or controller mode.

    python scripts/run_pilot.py claude  --results R [--n 10] [--model claude-sonnet-5-5] [--mode weights|controller]
    python scripts/run_pilot.py local   --results R --name qwen3-coder-30b --port 8089 [--n 10] [--mode weights|controller]
    python scripts/run_pilot.py probe   --results R          # isolation probe for claude -p

`claude` calls `claude -p` once per attempt in a fresh empty dir under /var/tmp, with all tools disabled,
no MCP servers, no session persistence, `--setting-sources project,local` (the user-level ~/.claude settings and
CLAUDE.md are not loaded). Per call, a check refuses to run if the cwd or any ancestor holds CLAUDE.md, CLAUDE.local.md
or .claude. Per batch, the isolation probe runs first and the batch is refused if the probe reports any instruction
file or its output contains an email address. `--arms strict,named,goal` picks the prompt arms
(goal = hopper only); `--suffix _iso2` is appended to attempt ids. `local` talks to a llama.cpp server on 127.0.0.1 (started via gpu-run by
the caller). No hosted-model API, no keys. Replies are saved raw; scoring is done afterwards by zsr.attempt score.
Attempts are never overwritten: an existing attempt directory with reply.md is skipped.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zsr.attempt import new_attempt  # noqa: E402

CELLS = [(t, a) for t in ("cartpole", "hopper") for a in ("strict", "named")]
CLAUDE_FLAGS = ["-p", "--tools", "", "--strict-mcp-config", "--no-session-persistence", "--disable-slash-commands",
                "--setting-sources", "project,local", "--output-format", "json"]
PROBE_PROMPT = ("Before anything else: list every tool you can call (names only, or say none), and list any files, "
                "directories, repository contents, memory, user or project instructions (e.g. CLAUDE.md) that you can see "
                "or that were given to you in this conversation. Then state the name of your current working "
                "directory if you know it. Be exact and brief. Finish with a last line that is exactly "
                "`INSTRUCTION_FILES: none` if you were given no instruction file of any kind, otherwise "
                "`INSTRUCTION_FILES: ` followed by their names.")
PROBE_OK_LINE = "INSTRUCTION_FILES: none"

# Sampling settings for local models: the model vendors' recommended values, fixed for every attempt.
LOCAL_SAMPLING = {
    "gpt-oss-20b": {"temperature": 1.0, "top_p": 1.0, "max_tokens": 24000},
    "qwen3-coder-30b": {"temperature": 0.7, "top_p": 0.8, "top_k": 20, "repeat_penalty": 1.05, "max_tokens": 16000},
}


def claude_env():
    env = dict(os.environ)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    return env


def claude_version() -> str:
    return subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
REDACTION = "[redacted-email]"


def redact(text):
    return EMAIL_RE.sub(REDACTION, text) if isinstance(text, str) else text


def write_redacted(path, text) -> None:
    """Every file holding Claude output goes to disk through here: email addresses are replaced first."""
    Path(path).write_text(redact(text))


def assert_no_email(path) -> None:
    if EMAIL_RE.search(Path(path).read_text()):
        raise SystemExit(f"redaction FAILED: {path} still contains an email address; delete it by hand and investigate")


ISOLATION_ROOT = "/var/tmp"
INSTRUCTION_NAMES = ("CLAUDE.md", "CLAUDE.local.md", ".claude")


def preflight(cwd) -> None:
    """Refuse to run claude -p if a project instruction file could be loaded: one in cwd or any ancestor.
    (The user-level ~/.claude/CLAUDE.md is excluded by --setting-sources project,local and checked by the probe.)"""
    cwd = Path(cwd).resolve()
    found = [str(a / n) for a in (cwd, *cwd.parents) for n in INSTRUCTION_NAMES if os.path.lexists(a / n)]
    if found:
        raise SystemExit("isolation pre-flight FAILED, refusing to run claude -p. Instruction files visible from "
                         f"{cwd}: {found}")


def call_claude(prompt: str, model: str, timeout: int = 900):
    """Run one claude -p call in a fresh empty directory under /var/tmp (re-checked every call)."""
    with tempfile.TemporaryDirectory(prefix="zsr_claude_", dir=ISOLATION_ROOT) as cwd:
        if os.listdir(cwd):
            raise SystemExit(f"{cwd} is not empty")
        preflight(cwd)
        cmd = ["claude", *CLAUDE_FLAGS, "--model", model]
        t0 = time.time()
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=cwd, env=claude_env(), timeout=timeout)
        dt = time.time() - t0
    return cmd, p, dt


def probe_verdict(stdout: str):
    """(ok, why) for a probe call: ok only if the reply's last line is the 'none' line and no email is in the output."""
    if EMAIL_RE.search(stdout):
        return False, "probe output contains an email address"
    try:
        reply = (json.loads(stdout).get("result") or "").strip()
    except json.JSONDecodeError:
        return False, "probe output is not JSON"
    last = reply.splitlines()[-1].strip().strip("`") if reply else ""
    if last != PROBE_OK_LINE:
        return False, f"probe reports an instruction file or gave no verdict (last line: {redact(last)!r})"
    return True, ""


def call_local(prompt: str, name: str, port: int, seed: int, timeout: int = 3600):
    s = dict(LOCAL_SAMPLING[name])
    body = {"messages": [{"role": "user", "content": prompt}], "seed": seed, "stream": False, **s}
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = json.loads(r.read())
    return {**s, "seed": seed}, raw, time.time() - t0


def run_cells(args):
    res = Path(args.results)
    t_start = time.time()
    if args.cmd == "claude":
        preflight(ISOLATION_ROOT)
        ok, why = probe(argparse.Namespace(results=args.results, model=args.model))
        if not ok:
            raise SystemExit(f"isolation probe FAILED for {args.model}, refusing the batch: {why}")
    arms = args.arms.split(",")
    for task, arm in CELLS + [("hopper", "goal")]:
        if arm not in arms:
            continue
        for i in range(args.n):
            aid = f"{args.tag}_{task}_{arm}_{args.mode}_{i:02d}{args.suffix}"
            d = res / "attempts" / aid
            if (d / "reply.md").exists():
                continue
            if args.max_seconds and time.time() - t_start > args.max_seconds:
                print("time budget reached; rerun to resume", flush=True)
                return
            if d.exists():
                raise SystemExit(f"{d} exists without reply.md; inspect it (attempts are never deleted)")
            interface = (f"claude -p (subscription CLI), fresh empty cwd under {ISOLATION_ROOT}, no tools, no MCP"
                         if args.cmd == "claude"
                         else "local llama.cpp server via gpu-run, /v1/chat/completions on 127.0.0.1")
            extra = {"attempt_index": i}
            if args.cmd == "claude":
                extra["isolation"] = (f"fresh empty dir under {ISOLATION_ROOT}; pre-flight: no CLAUDE.md / CLAUDE.local.md / "
                                      ".claude in cwd or any ancestor; batch pre-flight = isolation probe reported no instruction "
                                      "file and no email")
                extra["claude_flags"] = ["claude", *CLAUDE_FLAGS, "--model", args.model]
                extra["claude_env_extra"] = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
            new_attempt(aid, task, args.mode, args.model_label, interface, res, arm, extra)
            prompt = (d / "prompt.md").read_text()
            run = {"started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
            try:
                if args.cmd == "claude":
                    cmd, p, dt = call_claude(prompt, args.model)
                    run.update(cli_version=claude_version(), command=cmd, returncode=p.returncode, seconds=dt,
                               stderr=p.stderr[-2000:], raw_stdout=p.stdout)
                    try:
                        j = json.loads(p.stdout)
                        reply = j.get("result") or ""
                        run.update(model_reported=list(j.get("modelUsage", {})), usage=j.get("usage"),
                                   is_error=j.get("is_error"), stop_reason=j.get("stop_reason"))
                    except json.JSONDecodeError:
                        reply = ""
                else:
                    sampling, raw, dt = call_local(prompt, args.name, args.port, seed=1000 + i)
                    msg = raw["choices"][0]["message"]
                    reply = msg.get("content") or ""
                    run.update(sampling=sampling, seconds=dt, usage=raw.get("usage"), model_reported=raw.get("model"),
                               finish_reason=raw["choices"][0].get("finish_reason"),
                               reasoning_content=msg.get("reasoning_content"), server_timings=raw.get("timings"))
            except Exception as e:
                reply = ""
                run["error"] = f"{type(e).__name__}: {e}"
            write_redacted(d / "run.json", json.dumps(run, indent=1))
            write_redacted(d / "reply.md", reply)
            for f in d.iterdir():
                if f.is_file():
                    write_redacted(f, f.read_text())
                    assert_no_email(f)
            print(aid, "reply chars:", len(reply), redact(run.get("error", "")), flush=True)


def probe(args):
    """Run the isolation probe, write its (redacted) JSON, return (ok, why)."""
    res = Path(args.results)
    res.mkdir(parents=True, exist_ok=True)
    cmd, p, dt = call_claude(PROBE_PROMPT, args.model)
    out = res / f"claude_isolation_probe_{args.model}_{time.strftime('%Y%m%dT%H%M%S')}.json"
    write_redacted(out, json.dumps({"cli_version": claude_version(), "command": cmd, "env_extra": {
        "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}, "cwd": f"fresh empty tempfile.TemporaryDirectory under {ISOLATION_ROOT}",
        "prompt": PROBE_PROMPT, "seconds": dt, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr},
        indent=1))
    assert_no_email(out)
    print(out)
    return probe_verdict(p.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("claude", "local", "probe"))
    ap.add_argument("--results", required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--mode", choices=("weights", "controller"), default="weights")
    ap.add_argument("--tag", help="attempt id prefix; default: 'claude' for claude-sonnet-5-5 (pilot naming), else the model id")
    ap.add_argument("--arms", default="strict,named", help="comma list from strict,named,goal (goal = hopper only)")
    ap.add_argument("--suffix", default="", help="appended to attempt ids, e.g. _iso2 for the isolated rerun")
    ap.add_argument("--name", help="local model key: gpt-oss-20b | qwen3-coder-30b")
    ap.add_argument("--port", type=int, default=8089)
    ap.add_argument("--max-seconds", type=float, default=0, help="stop starting new attempts after this long (resumable chunks)")
    args = ap.parse_args()
    if args.cmd == "claude":
        args.tag = args.tag or ("claude" if args.model == "claude-sonnet-5-5" else args.model)
        args.model_label = args.model
    elif args.cmd == "local":
        args.tag, args.model_label = args.name, args.name
    if args.cmd == "probe":
        ok, why = probe(args)
        if not ok:
            raise SystemExit(f"isolation probe FAILED: {why}")
    else:
        run_cells(args)


if __name__ == "__main__":
    main()
