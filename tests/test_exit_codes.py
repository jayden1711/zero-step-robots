"""A wrapper must exit non-zero when its inner job failed (no masked failures)."""
import argparse
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_pilot  # noqa: E402


def _fake_py(tmp_path, code):
    p = tmp_path / "fakepy"
    p.write_text(f"#!/usr/bin/env bash\nexit {code}\n")
    p.chmod(p.stat().st_mode | stat.S_IEXEC)
    return str(p)


def _results_with_pending(tmp_path):
    d = tmp_path / "res" / "attempts" / "a1"
    d.mkdir(parents=True)
    (d / "reply.md").write_text("x")
    return tmp_path / "res"


def test_score_pending_fails_when_scorer_fails(tmp_path):
    res = _results_with_pending(tmp_path)
    r = subprocess.run(["bash", str(ROOT / "scripts/score_pending.sh"), str(res)],
                       env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home()), "PY": _fake_py(tmp_path, 1)},
                       capture_output=True, text=True)
    assert r.returncode != 0


def test_score_pending_fails_when_no_score_written(tmp_path):
    res = _results_with_pending(tmp_path)
    r = subprocess.run(["bash", str(ROOT / "scripts/score_pending.sh"), str(res)],
                       env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home()), "PY": _fake_py(tmp_path, 0)},
                       capture_output=True, text=True)
    assert r.returncode != 0


def test_run_pilot_exits_nonzero_when_model_call_fails(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise ConnectionRefusedError("server down")
    monkeypatch.setattr(run_pilot, "call_local", boom)
    args = argparse.Namespace(results=str(tmp_path), n=1, tag="fake", cmd="local", model_label="fake",
                              name="gpt-oss-20b", port=1, arms="strict,named", mode="weights",
                              suffix="", max_seconds=0)
    with pytest.raises(SystemExit) as e:
        run_pilot.run_cells(args)
    assert e.value.code not in (0, None)
