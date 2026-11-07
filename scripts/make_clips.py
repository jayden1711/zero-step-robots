"""Render two hopper clips from existing attempts (no training, no new attempts) into RESULTS/clips/.

  (a) the best-scoring Claude hopper weights attempt, (b) the median-scoring attempt of the same model/task/mode/arm.
Same camera, same episode seed (first evaluation seed, not chosen), same length (1000 steps, 250 frames).
Every frame carries a caption: rank among all scored hopper attempts, model, mode, arm, seed, score, "SIMULATION".
Attempts labelled `contaminated` in their meta.json (unrelated project file in context) are never selected or ranked.
Selection rule (fixed here, before looking at any clip): best = max stock mean return over Claude hopper weights
attempts; median = the attempt in that cell whose mean return is closest to the cell median (ties: lower index).
usage: sim-run python scripts/make_clips.py RESULTS_DIR   (env FFMPEG = path to an ffmpeg binary with libx264)
Software EGL (Mesa llvmpipe) is forced so the GPU is never touched; the encoder is single-threaded."""
import glob
import json
import os
import statistics as st
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MUJOCO_GL", "egl")
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
os.environ.setdefault("__EGL_VENDOR_LIBRARY_FILENAMES", "/usr/share/glvnd/egl_vendor.d/50_mesa.json")
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")

import gymnasium as gym  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from zsr.policy import load_weights  # noqa: E402
from zsr.tasks import EVAL_SEED0  # noqa: E402

R = Path(sys.argv[1])
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
W, H, STEPS, EVERY, FPS = 640, 480, 1000, 4, 31
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def load_attempts():
    out = {}
    for f in sorted(glob.glob(str(R / "attempts/*/score.json"))):
        s = json.load(open(f))
        m = json.load(open(Path(f).parent / "meta.json"))
        if m.get("contaminated"):
            continue
        out[m["id"]] = {"meta": m, "score": s}
    return out


def select(att):
    hop = {i: a for i, a in att.items() if a["meta"]["task"] == "hopper"}
    scored = {i: a for i, a in hop.items() if not a["score"].get("failure") and "mean_return" in a["score"]}
    order = sorted(scored, key=lambda i: (-scored[i]["score"]["mean_return"], i))
    rank = {i: k + 1 for k, i in enumerate(order)}
    claude = [i for i in scored if scored[i]["meta"]["mode"] == "weights" and scored[i]["meta"]["model"].startswith("claude")]
    best = max(claude, key=lambda i: (scored[i]["score"]["mean_return"], i))
    bm = scored[best]["meta"]
    cell_all = [i for i, a in hop.items() if (a["meta"]["model"], a["meta"]["mode"], a["meta"]["arm"]) ==
                (bm["model"], bm["mode"], bm["arm"])]
    cell = sorted(i for i in cell_all if i in scored)
    med = st.median(scored[i]["score"]["mean_return"] for i in cell)
    median = min(cell, key=lambda i: (abs(scored[i]["score"]["mean_return"] - med), i))
    cell_rank = {i: k + 1 for k, i in enumerate(sorted(cell, key=lambda i: (-scored[i]["score"]["mean_return"], i)))}
    return scored, rank, best, median, cell, cell_all, cell_rank, med, len(hop)


def caption(frame, lines_top, lines_bottom):
    im = Image.fromarray(frame)
    d = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(FONT, 13)
    h = 18 * len(lines_top) + 8
    d.rectangle([0, 0, W, h], fill=(0, 0, 0, 170))
    for k, t in enumerate(lines_top):
        d.text((8, 5 + 18 * k), t, font=f, fill=(255, 255, 255, 255))
    hb = 18 * len(lines_bottom) + 8
    d.rectangle([0, H - hb, W, H], fill=(0, 0, 0, 170))
    for k, t in enumerate(lines_bottom):
        d.text((8, H - hb + 5 + 18 * k), t, font=f, fill=(255, 255, 255, 255))
    return np.asarray(im)


def render(att_id, a, rank, n_scored, cell_rank, label, out_mp4, weights=None):
    m, s = a["meta"], a["score"]
    pol = load_weights("hopper", weights or R / "attempts" / att_id / "parsed.weights.json")
    env = gym.make("Hopper-v5", max_episode_steps=STEPS, render_mode="rgb_array", width=W, height=H)
    obs, _ = env.reset(seed=EVAL_SEED0)
    top = [f"SIMULATION (MuJoCo Hopper-v5, no real robot) - {label}",
           (f"rank {rank} of {n_scored} scored hopper attempts; {cell_rank} of 10 in its cell"
            if rank else "stock PPO baseline, not an LLM attempt (unranked)"),
           f"{m['model']} | mode {m['mode']} | arm {m['arm']}",
           att_id]
    base = [f"episode seed {EVAL_SEED0}; score = mean of 100 eps (seeds 10000-10099):",
            f"return {s['mean_return']:.0f}, forward distance {s['mean_distance']:.2f} m, "
            f"full length {s['frac_full_length']:.0%}"]
    x0 = float(env.unwrapped.data.qpos[0])
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-threads", "1", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out_mp4)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ret, step, kind, fell = 0.0, 0, None, False
    last = env.render()
    nframes = 0
    for step_i in range(STEPS):
        live = kind is None
        if live:
            obs, r, term, trunc, _ = env.step(pol.act(obs).astype(np.float32))
            ret += float(r)
            step = step_i + 1
            if term:
                kind, fell = f"FELL at step {step} (episode ended)", True
            elif trunc:
                kind = "time limit (1000 steps), still upright"
        if step_i % EVERY == 0:
            if live:
                last = env.render()
            state = kind or "running"
            dist = float(env.unwrapped.data.qpos[0]) - x0
            enc.stdin.write(caption(last, top, base + [f"step {step:4d}/1000 | return {ret:7.1f} | forward {dist:6.2f} m",
                                                        state]).tobytes())
            nframes += 1
    env.close()
    enc.stdin.close()
    enc.wait()
    return {"episode_return": ret, "episode_steps": step, "terminated_early": fell, "frames": nframes,
            "episode_forward_distance": float(env.unwrapped.data.qpos[0]) - x0}


def main():
    att = load_attempts()
    scored, rank, best, median, cell, cell_all, cell_rank, med, n_hop = select(att)
    out = R / "clips"
    out.mkdir(exist_ok=True)
    info = {}
    for key, i, label in (("a_best", best, "BEST Claude hopper weights attempt"),
                          ("b_median", median, "MEDIAN attempt, same model/mode/arm")):
        info[key] = {"attempt": i, "rank_all": rank[i], "rank_in_cell": cell_rank[i],
                     "mean_return": scored[i]["score"]["mean_return"],
                     "mean_distance": scored[i]["score"].get("mean_distance"),
                     "frac_full_length": scored[i]["score"].get("frac_full_length"),
                     "model": scored[i]["meta"]["model"], "arm": scored[i]["meta"]["arm"], "mode": scored[i]["meta"]["mode"]}
        info[key].update(render(i, scored[i], rank[i], len(scored), cell_rank[i], label, out / f"hopper_{key}.mp4"))
    ppo = json.load(open(R / "baselines/ppo/hopper_ppo_seed0.score.json"))
    ppo_a = {"meta": {"model": "ppo", "mode": "weights", "arm": "-"}, "score": ppo}
    info["c_ppo_reference"] = {"attempt": "hopper_ppo_seed0", "rank_all": None, "mean_return": ppo["mean_return"],
                               "mean_distance": ppo["mean_distance"], "frac_full_length": ppo["frac_full_length"]}
    info["c_ppo_reference"].update(render("hopper_ppo_seed0", ppo_a, None, len(scored), None,
                                          "REFERENCE: PPO baseline", out / "hopper_c_ppo_reference.mp4",
                                          weights=R / "baselines/ppo/hopper_ppo_seed0.weights.json"))
    info["_selection"] = {"n_hopper_attempts": n_hop, "n_scored": len(scored), "cell_size": len(cell_all),
                          "cell_scored": len(cell), "cell_median_return": med,
                          "cell_returns": {i: scored[i]["score"]["mean_return"] for i in cell}}
    (out / "selection.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
