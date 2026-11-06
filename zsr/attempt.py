"""Prompt building, attempt directories and reply parsing/scoring.

    python -m zsr.attempt prompt  <task> <weights|controller>            # print the prompt
    python -m zsr.attempt new     <id> <task> <weights|controller> --model M --interface I
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

from .harness import PythonController, evaluate, limit_resources
from .policy import MLPPolicy, n_params, shapes
from .tasks import HIDDEN, TASKS

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
VERSION = "v1"
MODES = ("weights", "controller")


def _read(name: str) -> str:
    return (PROMPTS / name).read_text()


def component_files(task: str, mode: str) -> list:
    return [f"template_{VERSION}.md", f"task_{task}_{VERSION}.md", f"format_{mode}_{VERSION}.md"]


def build_prompt(task: str, mode: str) -> str:
    t, sh = TASKS[task], shapes(task)
    fmt = _read(f"format_{mode}_{VERSION}.md")
    subs = {"{{HIDDEN}}": HIDDEN, "{{OBS_DIM}}": t.obs_dim, "{{ACT_DIM}}": t.act_dim, "{{N_PARAMS}}": n_params(task),
            "{{W1_SHAPE}}": list(sh["W1"]), "{{B1_SHAPE}}": list(sh["b1"]), "{{W2_SHAPE}}": list(sh["W2"]),
            "{{B2_SHAPE}}": list(sh["b2"])}
    for k, v in subs.items():
        fmt = fmt.replace(k, str(v))
    text = _read(f"template_{VERSION}.md").replace("{{TASK_SPEC}}", _read(f"task_{task}_{VERSION}.md").strip())
    text = text.replace("{{OUTPUT_FORMAT}}", fmt.strip())
    assert "{{" not in text, "unfilled placeholder"
    return text.strip() + "\n"


def prompt_hash(task: str, mode: str) -> str:
    return hashlib.sha256(build_prompt(task, mode).encode()).hexdigest()


def template_hashes(task: str, mode: str) -> dict:
    return {f: hashlib.sha256((PROMPTS / f).read_bytes()).hexdigest() for f in component_files(task, mode)}


def new_attempt(attempt_id: str, task: str, mode: str, model: str, interface: str, results: Path) -> Path:
    d = results / "attempts" / attempt_id
    if d.exists():
        raise FileExistsError(f"{d} already exists; attempts are never overwritten")
    d.mkdir(parents=True)
    (d / "prompt.md").write_text(build_prompt(task, mode))
    meta = {"id": attempt_id, "task": task, "mode": mode, "model": model, "interface": interface,
            "prompt_version": VERSION, "prompt_sha256": prompt_hash(task, mode),
            "template_sha256": template_hashes(task, mode),
            "created": datetime.now(timezone.utc).isoformat()}
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
    p.add_argument("mode", choices=MODES)
    n = sub.add_parser("new")
    n.add_argument("id")
    n.add_argument("task", choices=TASKS)
    n.add_argument("mode", choices=MODES)
    n.add_argument("--model", required=True)
    n.add_argument("--interface", required=True, help="e.g. 'subscription UI (pasted by hand)' or 'local gpu-run'")
    n.add_argument("--results", default="results")
    s = sub.add_parser("score")
    s.add_argument("id")
    s.add_argument("--results", default="results")
    s.add_argument("--episodes", type=int, default=100)
    a = ap.parse_args(argv)
    if a.cmd == "prompt":
        sys.stdout.write(build_prompt(a.task, a.mode))
    elif a.cmd == "new":
        print(new_attempt(a.id, a.task, a.mode, a.model, a.interface, Path(a.results)))
    else:
        d = Path(a.results) / "attempts" / a.id
        if json.loads((d / "meta.json").read_text())["mode"] == "controller":
            limit_resources()
        r = score_attempt(d, a.episodes)
        print(json.dumps({k: v for k, v in r.items() if k != "episodes"}, indent=1))


if __name__ == "__main__":
    main()
