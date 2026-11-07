"""Render four hopper clips from existing, CLEAN attempts (no training, no new attempts) into RESULTS/clips/.

  (a) best Claude hopper weights attempt by mean return, (b) the median attempt of that same model/mode/arm cell,
  (c) best goal-arm hopper attempt by mean forward distance, (d) stock PPO seed 0 (baseline, for contrast).
Same camera, same episode seed (first evaluation seed, not chosen), same length (1000 steps, 250 frames).
Every frame carries a caption: SIMULATION, model, mode, arm, attempt id, seed, mean return AND mean forward distance over
the 100 scoring episodes, rank, and a live step / return / distance counter.
Attempts labelled `contaminated` in their meta.json (unrelated project file in context) are never selected or ranked.
Selection rules (fixed here, before looking at any clip):
  a = max stock mean return over clean Claude hopper weights attempts (ties: id);
  b = in a's cell (model, mode, arm), the scored attempt whose mean return is closest to the cell median (ties: id);
  c = max stock mean forward distance over clean goal-arm hopper attempts, any mode (ties: id).
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
from zsr.harness import PythonController  # noqa: E402
from zsr.policy import load_weights  # noqa: E402
from zsr.tasks import EVAL_SEED0  # noqa: E402

R = Path(sys.argv[1]) if len(sys.argv) > 1 else None
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
W, H, STEPS, EVERY, FPS = 640, 480, 1000, 4, 31
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def load_attempts(results):
    out = {}
    for f in sorted(glob.glob(str(results / "attempts/*/score.json"))):
        s = json.load(open(f))
        m = json.load(open(Path(f).parent / "meta.json"))
        if m.get("contaminated"):
            continue
        out[m["id"]] = {"meta": m, "score": s, "dir": Path(f).parent}
    return out


def ranks(ids, scored, key):
    order = sorted(ids, key=lambda i: (-scored[i]["score"][key], i))
    return {i: k + 1 for k, i in enumerate(order)}


def select(att):
    hop = {i: a for i, a in att.items() if a["meta"]["task"] == "hopper"}
    scored = {i: a for i, a in hop.items() if not a["score"].get("failure") and "mean_return" in a["score"]}
    rank_ret = ranks(scored, scored, "mean_return")
    rank_dist = ranks(scored, scored, "mean_distance")
    claude_w = [i for i in scored if scored[i]["meta"]["mode"] == "weights" and scored[i]["meta"]["model"].startswith("claude")]
    best = max(claude_w, key=lambda i: (scored[i]["score"]["mean_return"], i))
    bm = scored[best]["meta"]
    cell_all = [i for i, a in hop.items() if (a["meta"]["model"], a["meta"]["mode"], a["meta"]["arm"]) ==
                (bm["model"], bm["mode"], bm["arm"])]
    cell = sorted(i for i in cell_all if i in scored)
    med = st.median(scored[i]["score"]["mean_return"] for i in cell)
    median = min(cell, key=lambda i: (abs(scored[i]["score"]["mean_return"] - med), i))
    cell_rank = ranks(cell, scored, "mean_return")
    goal_all = [i for i, a in hop.items() if a["meta"]["arm"] == "goal"]
    goal = sorted(i for i in goal_all if i in scored)
    goal_best = max(goal, key=lambda i: (scored[i]["score"]["mean_distance"], i))
    goal_rank = ranks(goal, scored, "mean_distance")
    return {"scored": scored, "rank_ret": rank_ret, "rank_dist": rank_dist, "n_hop": len(hop),
            "a": best, "b": median, "cell": cell, "cell_all": cell_all, "cell_rank": cell_rank, "cell_median": med,
            "c": goal_best, "goal": goal, "goal_all": goal_all, "goal_rank": goal_rank}


def caption(frame, lines_top, lines_bottom, font):
    im = Image.fromarray(frame)
    d = ImageDraw.Draw(im, "RGBA")
    for t in lines_top + lines_bottom:
        assert font.getlength(t) <= W - 12, f"caption line too wide: {t!r}"
    h = 18 * len(lines_top) + 8
    d.rectangle([0, 0, W, h], fill=(0, 0, 0, 170))
    for k, t in enumerate(lines_top):
        d.text((8, 5 + 18 * k), t, font=font, fill=(255, 255, 255, 255))
    hb = 18 * len(lines_bottom) + 8
    d.rectangle([0, H - hb, W, H], fill=(0, 0, 0, 170))
    for k, t in enumerate(lines_bottom):
        d.text((8, H - hb + 5 + 18 * k), t, font=font, fill=(255, 255, 255, 255))
    return np.asarray(im)


def make_policy(adir, mode, weights=None):
    if weights is not None or mode == "weights":
        return load_weights("hopper", weights or adir / "parsed.weights.json")
    return PythonController("hopper", adir / "parsed.controller.py")


def render(att_id, a, top_extra, label, out_mp4, weights=None):
    m, s = a["meta"], a["score"]
    pol = make_policy(a.get("dir"), m["mode"], weights)
    env = gym.make("Hopper-v5", max_episode_steps=STEPS, render_mode="rgb_array", width=W, height=H)
    obs, _ = env.reset(seed=EVAL_SEED0)
    if hasattr(pol, "reset"):
        pol.reset()
    font = ImageFont.truetype(FONT, 13)
    top = ["SIMULATION (MuJoCo Hopper-v5, no real robot)", label,
           f"{m['model']} | mode {m['mode']} | arm {m['arm']}",
           att_id] + top_extra
    base = [f"episode seed {EVAL_SEED0}; score = mean of 100 eps (seeds 10000-10099):",
            f"mean return {s['mean_return']:.0f} | mean forward distance {s['mean_distance']:.2f} m"]
    x0 = float(env.unwrapped.data.qpos[0])
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-threads", "1", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out_mp4)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ret, step, kind, fell, fault = 0.0, 0, None, False, None
    last = env.render()
    nframes = 0
    for step_i in range(STEPS):
        live = kind is None
        if live:
            try:
                act = np.asarray(pol.act(obs)).astype(np.float32)
            except Exception as e:  # same rule as the scoring harness: a crashing controller ends the episode
                fault = f"{type(e).__name__}: {e}"
                kind = "controller fault (episode ended)"
                live = False
        if live:
            obs, r, term, trunc, _ = env.step(act)
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
            enc.stdin.write(caption(last, top, base + [f"step {step:4d}/1000 | return {ret:7.1f} | distance {dist:6.2f} m",
                                                        state], font).tobytes())
            nframes += 1
    final_dist = float(env.unwrapped.data.qpos[0]) - x0
    env.close()
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {out_mp4}")
    return {"episode_return": ret, "episode_steps": step, "terminated_early": fell, "frames": nframes,
            "episode_forward_distance": final_dist, "fault": fault}


def describe(i, sel):
    a = sel["scored"][i]
    return {"attempt": i, "model": a["meta"]["model"], "mode": a["meta"]["mode"], "arm": a["meta"]["arm"],
            "prompt_sha256": a["meta"].get("prompt_sha256"),
            "rank_by_return": sel["rank_ret"][i], "rank_by_distance": sel["rank_dist"][i],
            "mean_return": a["score"]["mean_return"], "mean_distance": a["score"]["mean_distance"],
            "frac_full_length": a["score"].get("frac_full_length")}


def main():
    att = load_attempts(R)
    sel = select(att)
    n = len(sel["scored"])
    out = R / "clips"
    out.mkdir(exist_ok=True)
    info = {}
    plan = [
        ("a_best", sel["a"], "BEST Claude weights (by return)",
         f"cell rank {sel['cell_rank'][sel['a']]}/{len(sel['cell'])} by return"),
        ("b_median", sel["b"], "MEDIAN of the same cell as (a)",
         f"cell rank {sel['cell_rank'][sel['b']]}/{len(sel['cell'])} by return"),
        ("c_goal_best", sel["c"], "BEST goal-arm attempt (by distance)",
         f"goal-arm rank {sel['goal_rank'][sel['c']]}/{len(sel['goal'])} by distance"),
    ]
    for key, i, label, cell_line in plan:
        extra = [f"rank by return {sel['rank_ret'][i]}/{n}, by distance {sel['rank_dist'][i]}/{n} (clean hopper)", cell_line]
        d = describe(i, sel)
        d.update(render(i, sel["scored"][i], extra, label, out / f"hopper_{key}.mp4"))
        info[key] = d
    ppo = json.load(open(R / "baselines/ppo/hopper_ppo_seed0.score.json"))
    ppo_a = {"meta": {"model": "ppo (stock)", "mode": "weights", "arm": "-"}, "score": ppo}
    info["d_ppo_seed0"] = {"attempt": "hopper_ppo_seed0", "rank_by_return": None, "mean_return": ppo["mean_return"],
                           "mean_distance": ppo["mean_distance"], "frac_full_length": ppo["frac_full_length"]}
    info["d_ppo_seed0"].update(render("hopper_ppo_seed0", ppo_a, ["rank: none (baseline, not an LLM attempt)"],
                                      "PPO seed 0 (first seed)", out / "hopper_d_ppo_seed0.mp4",
                                      weights=R / "baselines/ppo/hopper_ppo_seed0.weights.json"))
    info["_selection"] = {"n_hopper_clean_attempts": sel["n_hop"], "n_scored": n,
                          "cell": [info["a_best"]["model"], info["a_best"]["mode"], info["a_best"]["arm"]],
                          "cell_size": len(sel["cell_all"]), "cell_scored": len(sel["cell"]),
                          "cell_median_return": sel["cell_median"],
                          "cell_returns": {i: sel["scored"][i]["score"]["mean_return"] for i in sel["cell"]},
                          "goal_arm_size": len(sel["goal_all"]), "goal_arm_scored": len(sel["goal"]),
                          "goal_distances": {i: sel["scored"][i]["score"]["mean_distance"] for i in sel["goal"]}}
    (out / "selection.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
