import importlib.util
import json
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("run_pilot", ROOT / "scripts" / "run_pilot.py")
run_pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_pilot)

FAKE = "jane.doe+test@example.co.uk"


def test_redact_replaces_every_address():
    s = f"account {FAKE}, again {FAKE} and other@host.org."
    out = run_pilot.redact(s)
    assert "@" not in out
    assert out.count("[redacted-email]") == 3


def test_redact_leaves_other_text_alone():
    s = "obs[0] * w @ x, no address here"
    assert run_pilot.redact(s) == s


def test_write_redacted_writes_no_email(tmp_path):
    p = tmp_path / "reply.md"
    run_pilot.write_redacted(p, f"hello {FAKE}")
    assert FAKE not in p.read_text()
    run_pilot.assert_no_email(p)


def test_assert_no_email_fails_loudly(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(f"leak {FAKE}")
    with pytest.raises(SystemExit):
        run_pilot.assert_no_email(p)


def test_probe_output_is_redacted(tmp_path, monkeypatch):
    p = types.SimpleNamespace(returncode=0, stdout=json.dumps({"result": f"you are {FAKE}"}), stderr=f"warn {FAKE}")
    monkeypatch.setattr(run_pilot, "call_claude", lambda prompt, model: (["claude"], p, 0.1))
    monkeypatch.setattr(run_pilot, "claude_version", lambda: "test")
    run_pilot.probe(types.SimpleNamespace(results=str(tmp_path), model="m"))
    files = list(tmp_path.glob("claude_isolation_probe_*.json"))
    assert len(files) == 1
    txt = files[0].read_text()
    assert FAKE not in txt and "[redacted-email]" in txt


def _out(reply):
    return json.dumps({"result": reply})


def test_probe_verdict_ok():
    assert run_pilot.probe_verdict(_out("No tools.\nINSTRUCTION_FILES: none"))[0]


def test_probe_verdict_refuses_instruction_file():
    ok, why = run_pilot.probe_verdict(_out("I see CLAUDE.md\nINSTRUCTION_FILES: CLAUDE.md"))
    assert not ok and "instruction" in why


def test_probe_verdict_refuses_missing_verdict():
    assert not run_pilot.probe_verdict(_out("no tools, nothing"))[0]
    assert not run_pilot.probe_verdict("not json")[0]
    # an account email in the raw reply (Claude Code's session context) is not an instruction file: it is accepted
    # here and redacted before writing (write_redacted fails loudly if a written file still contains one)
    assert run_pilot.probe_verdict(_out(f"{FAKE}\nINSTRUCTION_FILES: none"))[0]


def test_claude_flags_exclude_user_settings():
    f = run_pilot.CLAUDE_FLAGS
    assert f[f.index("--setting-sources") + 1] == "project,local"


def test_run_cells_refuses_batch_when_probe_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(run_pilot, "probe", lambda a: (False, "probe reports an instruction file"))
    args = types.SimpleNamespace(cmd="claude", results=str(tmp_path), model="m", arms="strict", n=1, mode="weights",
                                 tag="t", suffix="", max_seconds=0, model_label="m")
    with pytest.raises(SystemExit):
        run_pilot.run_cells(args)
    assert not (tmp_path / "attempts").exists()
