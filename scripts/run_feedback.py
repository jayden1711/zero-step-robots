"""CPG feedback arm runner (docs/prereg-2026-11-10-cpg-feedback.md). One model x task x level, attempts in order.

    python scripts/run_feedback.py --model claude-opus-5-5 --task hopper --level H2 --n 10 --results RESULTS

Attempt dir RESULTS/attempts/fb-<model>_<task>_<level>_NN/ holds meta.json and r0..r5/: prompt.md, run.json,
reply.md, parsed.spec.json, feedback.txt / feedback.json (dev seeds 0..9), parsed.cpg.json, score.json (held-out
scoring seeds; never shown to the model). The attempt's score.json is round 5's. Resumable: a round with a reply.md is
not called again. Transport failures (no reply) are repeated once; the failed try is kept as rK_try1/.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from run_pilot import (CLAUDE_FLAGS, ISOLATION_ROOT, assert_no_email, call_claude, claude_version,  # noqa: E402
                       preflight, probe, redact, write_redacted)
from zsr.attempt import PROMPTS, extract_block  # noqa: E402
from zsr.tasks import TASKS  # noqa: E402

ROUNDS = 6  # round 0 + 5 revisions
PY = sys.executable
SIM_RUN = str(Path.home() / "projects" / "bin" / "sim-run")
DEADLINE = datetime(2026, 11, 24, 0, 0, tzinfo=timezone.utc)  # 2026-11-23 18:00 CST


def files(task, level):
    hints = [f"hint_{task}_H{k}_v3.md" for k in range(1, int(level[1]) + 1)]
    return ["template_v4fb.md", f"task_{task}_v3.md", "format_cpgspec_v3.md", *hints,
            "feedback_history_v4fb.md", "feedback_revise_v4fb.md", "feedback_final_v4fb.md"]


def read(name):
    return (PROMPTS / name).read_text()


def round0_prompt(task, level):
    """Same assembly as zsr.attempt.build_prompt_cpg, with the feedback template."""
    t = TASKS[task]
    fmt = read("format_cpgspec_v3.md")
    for k, v in {"{{OBS_DIM}}": t.obs_dim, "{{ACT_DIM}}": t.act_dim, "{{OBS_DIM_MAX}}": t.obs_dim - 1,
                 "{{ACT_LAST}}": f"a{t.act_dim - 1}"}.items():
        fmt = fmt.replace(k, str(v))
    hint = "\n\n".join(read(f).strip() for f in files(task, level)[3:-3])
    text = read("template_v4fb.md").replace("{{TASK_SPEC}}", read(f"task_{task}_v3.md").strip())
    text = text.replace("{{HINT}}", "\n" + hint + "\n" if hint else "")
    text = text.replace("{{OUTPUT_FORMAT}}", fmt.strip())
    assert "{{" not in text
    return text.strip() + "\n"


def round_prompt(task, level, history, k):
    """history: list of (reply, summary) for rounds 0..k-1."""
    p = round0_prompt(task, level)
    if k == 0:
        return p
    blocks = [read("feedback_history_v4fb.md").strip().replace("{{J}}", str(j)).replace("{{REPLY}}", r.strip())
              .replace("{{SUMMARY}}", s.strip()) for j, (r, s) in enumerate(history)]
    rev = read("feedback_revise_v4fb.md").strip().replace("{{K}}", str(k))
    rev = rev.replace("{{FINAL}}", read("feedback_final_v4fb.md") if k == ROUNDS - 1 else "")
    return p + "\n" + "\n\n".join(blocks) + "\n\n" + rev + "\n"


def parse_reply(reply):
    block = extract_block(reply, "json")
    if block is None:
        return {"error": "no ```json block in reply"}
    try:
        spec = json.loads(block)
    except ValueError as e:
        return {"error": f"the json block is not valid JSON ({e})"}
    return spec if isinstance(spec, dict) else {"error": "the json block is not a JSON object"}


def run_round_call(rd: Path, prompt, model, timeout):
    rd.mkdir(parents=True, exist_ok=True)
    write_redacted(rd / "prompt.md", prompt)
    run = {"started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
    reply = ""
    try:
        cmd, p, dt = call_claude(prompt, model, timeout=timeout)
        run.update(cli_version=claude_version(), command=cmd, returncode=p.returncode, seconds=dt, timeout_s=timeout,
                   stderr=p.stderr[-2000:], raw_stdout=p.stdout)
        try:
            j = json.loads(p.stdout)
            reply = j.get("result") or ""
            run.update(model_reported=list(j.get("modelUsage", {})), usage=j.get("usage"), is_error=j.get("is_error"),
                       stop_reason=j.get("stop_reason"))
        except json.JSONDecodeError:
            pass
    except Exception as e:
        run["error"] = f"{type(e).__name__}: {e}"
    write_redacted(rd / "run.json", json.dumps(run, indent=1))
    write_redacted(rd / "reply.md", reply)
    for f in rd.iterdir():
        if f.is_file():
            write_redacted(f, f.read_text())
            assert_no_email(f)
    ok = not run.get("error") and run.get("returncode", 0) == 0 and reply.strip()
    return (rd / "reply.md").read_text(), bool(ok), run


def feedback(task, rd: Path, spec):
    (rd / "parsed.spec.json").write_text(json.dumps(spec, indent=1))
    subprocess.run([SIM_RUN, PY, "-m", "zsr.feedback", task, str(rd / "parsed.spec.json"), str(rd / "feedback.txt"),
                    "--json", str(rd / "feedback.json"), "--cpg-out", str(rd / "parsed.cpg.json")],
                   cwd=ROOT, env={**__import__("os").environ, "PYTHONPATH": str(ROOT)}, check=True,
                   stdout=subprocess.DEVNULL)
    return (rd / "feedback.txt").read_text()


def score(task, rd: Path):
    if not (rd / "parsed.cpg.json").exists():
        fb = json.loads((rd / "feedback.json").read_text())
        (rd / "score.json").write_text(json.dumps({"failure": fb.get("error", "no controller")}, indent=1))
        return
    subprocess.run([SIM_RUN, PY, "-m", "zsr.harness", task, "--cpg", str(rd / "parsed.cpg.json"), "--out",
                    str(rd / "score.json")], cwd=ROOT, env={**__import__("os").environ, "PYTHONPATH": str(ROOT)},
                   check=True, stdout=subprocess.DEVNULL)


def run_attempt(args, i):
    aid = f"fb-{args.model}_{args.task}_{args.level}_{i:02d}"
    d = Path(args.results) / "attempts" / aid
    if not d.exists():
        d.mkdir(parents=True)
        meta = {"id": aid, "task": args.task, "mode": "cpgspec-feedback", "arm": args.level, "level": args.level,
                "model": args.model, "attempt_index": i, "rounds": ROUNDS, "prompt_version": "v4fb",
                "prompt_files_sha256": {f: hashlib.sha256((PROMPTS / f).read_bytes()).hexdigest()
                                        for f in files(args.task, args.level)},
                "claude_flags": ["claude", *CLAUDE_FLAGS, "--model", args.model],
                "claude_env_extra": {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"},
                "interface": f"claude -p (subscription CLI), fresh empty cwd under {ISOLATION_ROOT}, no tools, no MCP",
                "prereg": "docs/prereg-2026-11-10-cpg-feedback.md",
                "created": datetime.now(timezone.utc).isoformat()}
        (d / "meta.json").write_text(json.dumps(meta, indent=1))
    history = []
    for k in range(ROUNDS):
        rd = d / f"r{k}"
        if not (rd / "reply.md").exists():
            if datetime.now(timezone.utc) >= DEADLINE:
                raise SystemExit("past the prereg stop time: no new LLM calls")
            prompt = round_prompt(args.task, args.level, history, k)
            reply, ok, run = run_round_call(rd, prompt, args.model, args.timeout)
            if not ok:  # transport failure: keep it, repeat once
                print(aid, f"r{k}", "transport failure, repeating once:", redact(run.get("error", "")), flush=True)
                shutil.move(str(rd), str(d / f"r{k}_try1"))
                reply, ok, run = run_round_call(rd, prompt, args.model, args.timeout)
            print(aid, f"r{k}", "reply chars:", len(reply), "ok" if ok else "NO REPLY", flush=True)
        reply = (rd / "reply.md").read_text()
        if not (rd / "feedback.txt").exists():
            spec = parse_reply(reply) if reply.strip() else {"error": "no reply was received"}
            feedback(args.task, rd, spec)
        history.append((reply, (rd / "feedback.txt").read_text()))
    for k in range(ROUNDS):
        if not (d / f"r{k}" / "score.json").exists():
            score(args.task, d / f"r{k}")
    shutil.copy(d / f"r{ROUNDS - 1}" / "score.json", d / "score.json")
    s = json.loads((d / "score.json").read_text())
    print(aid, "final (round 5) held-out mean d:", s.get("mean_distance_healthy", s.get("failure")), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--task", required=True, choices=("hopper", "walker2d"))
    ap.add_argument("--level", default="H2", choices=("H2", "H0"))
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--results", required=True)
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    preflight(ISOLATION_ROOT)
    ok, why = probe(argparse.Namespace(results=args.results, model=args.model))
    if not ok:
        raise SystemExit(f"isolation probe FAILED for {args.model}, refusing the batch: {why}")
    for i in range(args.n):
        run_attempt(args, i)


if __name__ == "__main__":
    main()
