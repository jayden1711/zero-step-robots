"""Prompt building, attempt directories and reply parsing/scoring.

    python -m zsr.attempt prompt  <task> <weights|controller> [--arm strict|named]   # print the prompt
    python -m zsr.attempt new     <id> <task> <weights|controller> --model M --interface I [--arm strict|named]
    python -m zsr.attempt score   <id>                                   # parse reply.md, score it, log everything

An attempt lives in results/attempts/<id>/ (git-ignored): prompt.md, meta.json, reply.md, parsed.*, score.json.
Failed parses and crashes are scored and logged like any other attempt; nothing is ever deleted.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .cpg import CPGPolicy
from .harness import PythonController, evaluate, limit_resources
from .policy import MLPPolicy, n_params, shapes
from .tasks import HIDDEN, TASKS

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from circuitc import compile_cpg  # noqa: E402
PROMPTS = ROOT / "prompts"
ARMS = {"strict": "v2", "named": "v1", "goal": "v2", "H0": "v3", "H1": "v3", "H2": "v3"}
# H0/H1/H2 = CPG track hint levels (docs/prereg-2026-11-09-cpg.md section 4), mode `cpgspec` only.
LEVELS = ("H0", "H1", "H2")
CPG_TASKS = ("hopper", "walker2d")
# `goal` = the strict prompt plus one sentence naming the goal (forward distance); hopper only.
ARM_TASKS = {"goal": ("hopper",), **{lv: CPG_TASKS for lv in LEVELS}}
PROMPT_TASKS = ("cartpole", "hopper")  # tasks with v1/v2 prompts; walker2d exists only in the CPG track (v3)
MODES = ("weights", "controller")  # v1/v2 modes; the CPG track uses mode "cpgspec"
ALL_MODES = MODES + ("cpgspec",)


def _read(name: str) -> str:
    return (PROMPTS / name).read_text()


def arm_valid(task: str, arm: str) -> bool:
    return task in ARM_TASKS.get(arm, PROMPT_TASKS)


def component_files(task: str, mode: str, arm: str) -> list:
    v = ARMS[arm]
    if arm in LEVELS:
        hints = [f"hint_{task}_H{k}_{v}.md" for k in range(1, int(arm[1]) + 1)]
        return [f"template_{v}.md", f"task_{task}_{v}.md", f"format_cpgspec_{v}.md", *hints]
    files = [f"template_{v}.md", f"task_{task}_{v}.md", f"format_{mode}_{v}.md"]
    if arm == "goal":
        files.append(f"goal_{task}_{v}.md")
    return files


def build_prompt_cpg(task: str, level: str) -> str:
    t, v = TASKS[task], ARMS[level]
    files = component_files(task, "cpgspec", level)
    fmt = _read(files[2])
    for k, val in {"{{OBS_DIM}}": t.obs_dim, "{{ACT_DIM}}": t.act_dim, "{{OBS_DIM_MAX}}": t.obs_dim - 1,
                   "{{ACT_LAST}}": f"a{t.act_dim - 1}"}.items():
        fmt = fmt.replace(k, str(val))
    hint = "\n\n".join(_read(f).strip() for f in files[3:])
    text = _read(files[0]).replace("{{TASK_SPEC}}", _read(files[1]).strip())
    text = text.replace("{{HINT}}", "\n" + hint + "\n" if hint else "")
    text = text.replace("{{OUTPUT_FORMAT}}", fmt.strip())
    assert "{{" not in text, "unfilled placeholder"
    return text.strip() + "\n"


def build_prompt(task: str, mode: str, arm: str = "strict") -> str:
    if not arm_valid(task, arm):
        raise ValueError(f"arm {arm!r} is not defined for task {task!r}")
    if (arm in LEVELS) != (mode == "cpgspec"):
        raise ValueError("mode 'cpgspec' goes with the hint levels H0/H1/H2 and only with them")
    if arm in LEVELS:
        return build_prompt_cpg(task, arm)
    t, sh = TASKS[task], shapes(task)
    v = ARMS[arm]
    fmt = _read(f"format_{mode}_{v}.md")
    subs = {"{{HIDDEN}}": HIDDEN, "{{OBS_DIM}}": t.obs_dim, "{{ACT_DIM}}": t.act_dim, "{{N_PARAMS}}": n_params(task),
            "{{W1_SHAPE}}": list(sh["W1"]), "{{B1_SHAPE}}": list(sh["b1"]), "{{W2_SHAPE}}": list(sh["W2"]),
            "{{B2_SHAPE}}": list(sh["b2"])}
    for k, val in subs.items():
        fmt = fmt.replace(k, str(val))
    spec = _read(f"task_{task}_{v}.md").strip()
    if arm == "goal":
        spec += "\n\n" + _read(f"goal_{task}_{v}.md").strip()
    text = _read(f"template_{v}.md").replace("{{TASK_SPEC}}", spec)
    text = text.replace("{{OUTPUT_FORMAT}}", fmt.strip())
    assert "{{" not in text, "unfilled placeholder"
    return text.strip() + "\n"


def prompt_hash(task: str, mode: str, arm: str = "strict") -> str:
    return hashlib.sha256(build_prompt(task, mode, arm).encode()).hexdigest()


def template_hashes(task: str, mode: str, arm: str) -> dict:
    return {f: hashlib.sha256((PROMPTS / f).read_bytes()).hexdigest() for f in component_files(task, mode, arm)}


def new_attempt(attempt_id: str, task: str, mode: str, model: str, interface: str, results: Path,
                arm: str = "strict", extra: dict = None) -> Path:
    d = results / "attempts" / attempt_id
    if d.exists():
        raise FileExistsError(f"{d} already exists; attempts are never overwritten")
    d.mkdir(parents=True)
    (d / "prompt.md").write_text(build_prompt(task, mode, arm))
    meta = {"id": attempt_id, "task": task, "mode": mode, "model": model, "interface": interface,
            "arm": arm, "prompt_version": ARMS[arm], "prompt_sha256": prompt_hash(task, mode, arm),
            "template_sha256": template_hashes(task, mode, arm),
            "created": datetime.now(timezone.utc).isoformat(), **(extra or {})}
    (d / "meta.json").write_text(json.dumps(meta, indent=1))
    return d


def extract_block(reply: str, lang: str):
    """Last fenced block tagged `lang`. The last one wins so that earlier drafts in the reply are ignored."""
    blocks = re.findall(r"```[ \t]*" + lang + r"[ \t]*\n(.*?)```", reply, flags=re.S | re.I)
    return blocks[-1] if blocks else None


def score_attempt(d: Path, episodes: int = 100) -> dict:
    meta = json.loads((d / "meta.json").read_text())
    task, mode = meta["task"], meta["mode"]
    reply = (d / "reply.md").read_text()
    out = {"id": meta["id"], "task": task, "mode": mode, "failure": None}
    pol = None
    try:
        if mode == "weights":
            block = extract_block(reply, "json")
            if block is None:
                raise ValueError("no ```json block in reply")
            (d / "parsed.weights.json").write_text(block)
            pol = MLPPolicy(task, json.loads(block))
        elif mode == "cpgspec":
            block = extract_block(reply, "json")
            if block is None:
                raise ValueError("no ```json block in reply")
            (d / "parsed.spec.json").write_text(block)
            spec = json.loads(block)
            t = TASKS[task]
            if isinstance(spec, dict) and (spec.get("obs_dim"), spec.get("act_dim"), spec.get("hidden")) != (
                    t.obs_dim, t.act_dim, HIDDEN):
                raise ValueError(f"spec dims {spec.get('obs_dim')}/{spec.get('act_dim')}/{spec.get('hidden')} do not "
                                 f"match the task ({t.obs_dim}/{t.act_dim}/{HIDDEN})")
            params, report = compile_cpg(spec)
            (d / "parsed.cpg.json").write_text(json.dumps(params, indent=1))
            (d / "compile_report.json").write_text(json.dumps(report, indent=1))
            pol = CPGPolicy(task, params)
        else:
            block = extract_block(reply, "python")
            if block is None:
                raise ValueError("no ```python block in reply")
            (d / "parsed.controller.py").write_text(block)
            pol = PythonController(task, d / "parsed.controller.py")
    except Exception as e:
        out["failure"] = f"{type(e).__name__}: {e}"
    if pol is not None:
        out.update(evaluate(task, pol, episodes))
    (d / "score.json").write_text(json.dumps(out, indent=1))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("task", choices=TASKS)
    p.add_argument("mode", choices=ALL_MODES)
    p.add_argument("--arm", choices=ARMS, default="strict", help="strict|named|goal, or H0|H1|H2 with mode cpgspec")
    n = sub.add_parser("new")
    n.add_argument("id")
    n.add_argument("task", choices=TASKS)
    n.add_argument("mode", choices=ALL_MODES)
    n.add_argument("--model", required=True)
    n.add_argument("--interface", required=True, help="e.g. 'subscription UI (pasted by hand)' or 'local gpu-run'")
    n.add_argument("--arm", choices=ARMS, default="strict", help="strict = prompt v2 (raw numbers), named = v1")
    n.add_argument("--results", default="results")
    s = sub.add_parser("score")
    s.add_argument("id")
    s.add_argument("--results", default="results")
    s.add_argument("--episodes", type=int, default=100)
    a = ap.parse_args(argv)
    if a.cmd == "prompt":
        sys.stdout.write(build_prompt(a.task, a.mode, a.arm))
    elif a.cmd == "new":
        print(new_attempt(a.id, a.task, a.mode, a.model, a.interface, Path(a.results), a.arm))
    else:
        d = Path(a.results) / "attempts" / a.id
        if json.loads((d / "meta.json").read_text())["mode"] == "controller":
            limit_resources()
        r = score_attempt(d, a.episodes)
        print(json.dumps({k: v for k, v in r.items() if k != "episodes"}, indent=1))


if __name__ == "__main__":
    main()
