"""Render the CPG feedback-arm clips fixed in docs/addendum-2026-11-11-cpg-clips.md (5 designs x seeds 10000-10002).

usage: FFMPEG=<ffmpeg with libx264> PYTHONPATH=. sim-run <python> scripts/make_cpg_clips.py RESULTS_DIR
Software EGL (no GPU), single-threaded encoder. Replays existing compiled cpg-v1 weights; no training, no LLM call.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MUJOCO_GL", "egl")
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
os.environ.setdefault("__EGL_VENDOR_LIBRARY_FILENAMES", "/usr/share/glvnd/egl_vendor.d/50_mesa.json")
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")

import gymnasium as gym  # noqa: E402
import mujoco  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from circuitc import compile_cpg  # noqa: E402
from zsr.cpg import CPGPolicy  # noqa: E402
from zsr.harness import evaluate  # noqa: E402
from zsr.tasks import TASKS  # noqa: E402

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
W, H, STEPS, EVERY, FPS = 640, 480, 1000, 4, 31
SEEDS = (10000, 10001, 10002)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def load(p):
    return json.loads(Path(p).read_text())


def select(R: Path):
    A = R / "attempts"
    walk = []
    for d in sorted(A.glob("fb-claude-opus-5-5_walker2d_H2_[0-9][0-9]")):
        s = load(d / "r5" / "score.json")
        dv = 0.0 if s.get("failure") or "mean_distance_healthy" not in s else s["mean_distance_healthy"]
        walk.append((dv, d.name))
    walk.sort()
    if len(walk) != 10:
        raise SystemExit(f"expected 10 Opus walker2d feedback attempts, found {len(walk)}")
    w_id = walk[4][1]  # lower median: 5th lowest of 10 (ties by id via the tuple sort)
    return [
        {"key": "hopper_opus_fb08_r5", "task": "hopper", "id": "fb-claude-opus-5-5_hopper_H2_08 round 5",
         "why": "passing LLM design (feedback arm)", "cpg": A / "fb-claude-opus-5-5_hopper_H2_08" / "r5" / "parsed.cpg.json",
         "score": A / "fb-claude-opus-5-5_hopper_H2_08" / "r5" / "score.json"},
        {"key": "hopper_opus_fb03_r5", "task": "hopper", "id": "fb-claude-opus-5-5_hopper_H2_03 round 5",
         "why": "passing LLM design (feedback arm; passed at round 0)",
         "cpg": A / "fb-claude-opus-5-5_hopper_H2_03" / "r5" / "parsed.cpg.json",
         "score": A / "fb-claude-opus-5-5_hopper_H2_03" / "r5" / "score.json"},
        {"key": "walker2d_opus_fb_lowermedian_r5", "task": "walker2d", "id": f"{w_id} round 5",
         "why": "failing LLM design: lower median of Opus walker2d feedback attempts (rank rule)",
         "cpg": A / w_id / "r5" / "parsed.cpg.json", "score": A / w_id / "r5" / "score.json",
         "rank_list": [{"id": i, "heldout_mean_d": v} for v, i in walk]},
        {"key": "hopper_tuned_cpg", "task": "hopper", "id": "hopper search-tuned CPG (baseline)",
         "why": "baseline: structure by hand, parameters by search on dev seeds",
         "spec": R / "cpg" / "baselines" / "hopper" / "tuned_cpg.spec.json",
         "score": R / "cpg" / "baselines" / "hopper" / "tuned_cpg.score.json"},
        {"key": "walker2d_tuned_cpg", "task": "walker2d", "id": "walker2d search-tuned CPG (baseline)",
         "why": "baseline: structure by hand, parameters by search on dev seeds",
         "spec": R / "cpg" / "baselines" / "walker2d" / "tuned_cpg.spec.json",
         "score": R / "cpg" / "baselines" / "walker2d" / "tuned_cpg.score.json"},
    ]


def policy(c):
    params = load(c["cpg"]) if "cpg" in c else compile_cpg(load(c["spec"]))[0]
    return CPGPolicy(c["task"], params)


def caption(frame, top, bottom, font):
    img = Image.fromarray(frame)
    dr = ImageDraw.Draw(img)
    for lines, y0 in ((top, 4), (bottom, H - 4 - 16 * len(bottom))):
        dr.rectangle([0, y0 - 2, W, y0 + 16 * len(lines)], fill=(0, 0, 0))
        for k, t in enumerate(lines):
            dr.text((6, y0 + 16 * k), t, fill=(255, 255, 255), font=font)
    return img


def render(c, seed, out_mp4, sc):
    pol = policy(c)
    env_id = TASKS[c["task"]].env_id
    env = gym.make(env_id, max_episode_steps=STEPS, render_mode="rgb_array", width=W, height=H, camera_name="track")
    obs, _ = env.reset(seed=seed)
    pol.reset()
    font = ImageFont.truetype(FONT, 13)
    top = [f"SIMULATION (MuJoCo {mujoco.__version__}, Gymnasium {env_id}; no real robot)", c["id"], c["why"],
           f"held-out score (100 eps, seeds 10000-10099): mean d {sc['mean_distance_healthy']:.2f} m, "
           f"{sc['n_clean_3m']}/100 eps >= 3 m"]
    x0 = float(env.unwrapped.data.qpos[0])
    x_h = x0
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-threads", "1", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out_mp4)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    state, step, last = None, 0, env.render()
    for i in range(STEPS):
        live = state is None
        if live:
            obs, _, term, trunc, _ = env.step(np.asarray(pol.act(obs), np.float32))
            step = i + 1
            if not term:
                x_h = float(env.unwrapped.data.qpos[0])
            if term:
                state = f"FELL at step {step} (episode ended)"
            elif trunc:
                state = "1000 steps reached without a fall"
        if i % EVERY == 0:
            if live:
                last = env.render()
            bottom = [f"episode seed {seed} | step {step:4d}/1000 | distance to last healthy step {x_h - x0:6.2f} m",
                      state or "running"]
            enc.stdin.write(np.asarray(caption(last, top, bottom, font)).tobytes())
    env.close()
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {out_mp4}")
    return {"seed": seed, "steps": step, "fell": bool(state and state.startswith("FELL")), "d": x_h - x0}


def main():
    R = Path(sys.argv[1])
    out = R / "clips_cpg"
    out.mkdir(parents=True, exist_ok=True)
    sel = select(R)
    info = []
    for c in sel:
        sc = load(c["score"])
        # check: the replayed weights reproduce the stored held-out score on these seeds
        chk = evaluate(c["task"], policy(c), n_episodes=3)
        stored = sc.get("episodes", [])[:3]
        if stored and any(abs(a["distance_healthy"] - b["distance_healthy"]) > 1e-9
                          for a, b in zip(chk["episodes"], stored)):
            raise SystemExit(f"replay mismatch for {c['key']}")
        eps = [render(c, s, out / f"{c['key']}_seed{s}.mp4", sc) for s in SEEDS]
        info.append({**{k: str(v) for k, v in c.items() if k not in ("rank_list",)},
                     "rank_list": c.get("rank_list"), "heldout_mean_d": sc["mean_distance_healthy"],
                     "heldout_n_clean_3m": sc["n_clean_3m"], "episodes": eps})
        print(c["key"], [(e["seed"], round(e["d"], 2), e["steps"]) for e in eps], flush=True)
    (out / "selection.json").write_text(json.dumps({"addendum": "docs/addendum-2026-11-11-cpg-clips.md",
                                                    "mujoco": mujoco.__version__, "seeds": SEEDS, "clips": info},
                                                   indent=1))


if __name__ == "__main__":
    main()
