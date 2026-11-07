"""Label the round-2 Claude attempts that ran with an unrelated /tmp/CLAUDE.md loaded as project instructions:
Sonnet controller arm, and every Opus arm (weights and controller). Adds `contaminated` to their meta.json (nothing
else is changed, nothing is deleted). Idempotent. Attempts from the isolated rerun (ids ending _iso2) are never marked.
usage: python scripts/mark_contaminated.py RESULTS_DIR [--dry-run]"""
import glob
import json
import sys
from pathlib import Path

LABEL = "/tmp/CLAUDE.md"
R = Path(sys.argv[1])
dry = "--dry-run" in sys.argv
n = 0
for f in sorted(glob.glob(str(R / "attempts/*/meta.json"))):
    m = json.load(open(f))
    if m["id"].endswith("_iso2"):
        continue
    sonnet_controller = m["model"] == "claude-sonnet-5-5" and m["mode"] == "controller"
    if (sonnet_controller or m["model"] == "claude-opus-5-5") and m.get("contaminated") != LABEL:
        m["contaminated"] = LABEL
        if not dry:
            Path(f).write_text(json.dumps(m, indent=1))
        n += 1
print(f"{'would mark' if dry else 'marked'} {n} attempts")
