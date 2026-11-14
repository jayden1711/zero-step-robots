# Pre-registration addendum 2026-11-09 (b): CPG track toward the 3 m target

Written 2026-11-09 (CST), before any code, prompt, baseline or attempt of this track exists. It is committed on its own
(docs only) before anything below is built or run. It refines the 2026-11-09 addendum in `PLAN.md` ("raised target",
commit `ca02e28`); where the two differ, this file governs the CPG track and says so. Everything earlier (pilot,
round 2, strict / named / goal arms, isolated rerun, circuit first compiles, return tables, the 1 m rule) stays reported
exactly as it was.

Owner decision 2026-11-09 (relayed by the organizer): unpark zero-step with one hard target only, background priority,
two-week timebox ending **2026-11-23**.

## 1. Target

An LLM writes, with zero training (section 7), the parameters of an oscillator / CPG network controller for
**Hopper-v5**, then **Walker2d-v5** (Gymnasium 1.4.0, MuJoCo 3.17.0, mujoco<4 pinned; 1000-step episodes, dt 0.008 s),
that moves **at least 3 m forward without falling**. The LLM writes a spec in the circuit-spec language; the
deterministic compiler `circuitc/` turns it into the exact weights of the network in section 2. The compiler does no
fitting and sees no rollout.

## 2. The network (format `cpg-v1`, fixed here)

State: M phase oscillators `theta` (M <= 4 for both tasks), set to the spec's initial phases at every episode reset.
At each env step, with observation `obs` (raw, as the env returns it):

    y      = [cos theta_1, sin theta_1, ..., cos theta_M, sin theta_M]           (2M oscillator outputs)
    h      = tanh(W1 @ [obs; y] + b1)                                            (16 hidden tanh units)
    action = clip(W2 @ h + b2, -1, 1)
    theta  <- theta + dt * (2*pi*f + sum_j C_ij * sin(theta_j - theta_i - Phi_ij) + S @ obs)     (explicit Euler, dt = 0.008)

Parameters: `f` (M), `C`, `Phi` (M x M), `S` (M x obs_dim, sensory frequency modulation), initial phases (M), `W1`,
`b1`, `W2`, `b2`. The action at step t uses theta_t; theta is then advanced with obs_t. The feedforward part is the same
16-tanh-unit layer every earlier arm uses, with the oscillator outputs appended to its input. The balance-feedback path is
the `obs` input of the same layer (and `S`). Nothing else (no memory, no other state).

Compiler extension (`circuitc`, target `cpg`): an `oscillators` block (name, frequency in Hz, initial phase, optional
sensory feedback `{obs[i]: gain}`), a `couplings` list (from, to, weight, phase lag), and the existing `linear` / `reflex`
unit primitives, whose inputs may now also name `cos(<osc>)` and `sin(<osc>)`. Exactness rules are unchanged: anything
not expressible is a compile error; a `linear` unit is exact only within its declared range and tolerance, which the
compiler reports. Unit tests check every primitive and the oscillator integration against a direct evaluation of the spec.

## 3. Metrics and partial credit

Per episode, **d** = forward displacement of the root x coordinate from reset to the **last healthy step** (the step that
makes the system unhealthy is excluded, so the fall itself earns nothing; for a 1000-step episode it is the final step).
An episode is **clean** when d >= 3 m.

- **Attempt passes** when, over the 100 scoring episodes (reset seeds 10000..10099, unchanged), mean d >= 3 m **and** at
  least 50 of 100 episodes are clean. (This is stricter than `ca02e28`, which used mean displacement including the fall;
  that number is also reported.)
- **Partial credit** = mean d (continuous, negative allowed), reported for every attempt, with bins
  `< 0`, `0-0.5`, `0.5-1.5`, `1.5-3`, `3-5`, `>= 5` m, the clean-episode count, the full-length fraction, mean episode
  length and return.
- **Arm** = model x task x hint level (mode is always `cpg-spec` in this track). An arm **meets the target** when at least
  5 of its 10 attempts pass (as in `ca02e28`). The best attempt is reported separately and never stands in for the arm.
- Compile errors and load errors count as attempts with d = 0, listed as failures.

## 4. Curriculum: hint levels (fixed text, frozen before any attempt)

All levels use the NAMED observation description (the balance feedback needs to know which reading is the torso angle
and its rate), the scoring rule of section 3 stated as the score (not the env reward; this answers critique R-C1), the
`cpg-v1` network and the spec language. Gymnasium's reward is still stated, labelled as the env's own reward.

- **H2 (full hint):** H1 plus admissible numeric ranges: oscillator frequency band, per-joint amplitude ranges, and the
  sign conventions of the joints and of the torso angle, taken from the env XML and the Gymnasium docs; plus the
  feedback structure in words (torso angle and angular velocity to the hip joints, which sign corrects a forward lean).
- **H1 (structure):** a named oscillator / phase structure for the gait in words (hopper: one rhythm, leg compression and
  push-off in stance, thigh swing in flight; walker: two legs in antiphase, stance / swing per leg), and that torso
  angle and angular velocity should feed back; no numbers.
- **H0 (minimal):** no gait hint; the spec language with oscillators available and the distance objective only.

Owner decision: the curriculum runs **from the full hint to the minimal one**, so each task runs H2, then H1, then H0
(this reverses the H0 -> H2 order in `ca02e28`). Each call is a fresh context, so order matters only for the timebox: all
three levels run for the partial-credit curve whatever the outcome at a higher level. The arm result is the **lowest
level at which it meets the target**, plus the partial-credit curve over H2, H1, H0.

Fairness: hint text is written from the env XML, the Gymnasium documentation and generic gait knowledge only, **before**
the tuned CPG of section 5 exists. No tuned constant, example spec or weight appears in any prompt. Prompt files are new
versioned files (`prompts/*_v3.md`); their SHA-256 are written to `prompts/SHA256SUMS-cpg.txt` in the commit that freezes
them, before the first attempt and before any CPG tuning. H1 and H2 are hints beyond what PPO gets; they are labelled as
such and H0 is the closest to parity.

## 5. Baselines (same harness, same 100 scoring episodes, both tasks)

Necessity table of `ca02e28` (zero weights, random MLP, the highest-return stand-still attempt (hopper), a fall-forward
lunge, an open-loop sinusoid tuned on dev seeds), with mean / median / min d, clean count, return, full-length fraction,
plus:

- **Random CPG**: 50 specs per task drawn from a fixed distribution over the spec language (oscillator count, frequency
  0.5-4 Hz, couplings, oscillator-to-joint and obs-to-joint gains), seeds 0..49, distribution defined in code before
  any of them is scored. Reported: full distribution, median, best and the count that pass. Necessity rule: the median
  random CPG must have mean d < 1.5 m. Best-of-50 is a small search; if it passes 3 m, that is reported plainly.
- **Tuned CPG (headroom)**: hand-designed structure in the same spec language, parameters set by hand iteration and a
  coarse search on **dev seeds 0..19 only**, budget at most 20,000 dev episodes per task, then scored once on the scoring
  seeds. It shows whether the `cpg-v1` network can reach 3 m at all. It uses rollouts, so it is a baseline, never an LLM
  arm, and nothing from it enters a prompt. If it does not reach 3 m, the report says the headroom was not shown, and the
  LLM arms still run unchanged.
- **PPO** (SB3 defaults, the existing 16-unit actor, 1M steps, 3 seeds, CPU via `sim-run`): upper reference on the env
  reward, reported with d. Walker2d PPO is new; hopper PPO is reused.
- Dev seeds (< 10000) are the only seeds any tuning sees. Each baseline row's rule (necessity: mean d < 1.5 m) is as in
  `ca02e28`; if the open-loop sinusoid passes 3 m, the bar is raised by a further dated addendum before any claim.

## 6. Attempts and LLM calls

- **Models:** Claude Opus 5.5 (`claude-opus-5-5`) and Claude Sonnet 5.5 (`claude-sonnet-5-5`) through `claude -p` with
  the existing isolation (fresh empty dir under `/var/tmp`, pre-flight, `--setting-sources project,local`, no tools,
  no MCP, probe per batch, email redaction). Local models (Qwen3-Coder-30B, gpt-oss-20b) run the same cells only if the
  GPU queue reaches zero-step before 2026-11-20; otherwise they are reported as not run.
- **Size:** 10 attempts per model x task x level. Claude: 2 models x 2 tasks x 3 levels x 10 = **120 calls**, plus one
  isolation probe per batch (at most 12). Hard cap 140 Claude calls in this track. No retries of a valid reply; a call
  that fails at the transport level (no reply) may be repeated once with the same index, and both are logged.
- **Order:** hopper H2, H1, H0 (Opus and Sonnet), then Walker2d H2, H1, H0. Walker2d starts when the hopper cells are
  scored or on 2026-11-16, whichever comes first.
- Every attempt is logged (prompt, hash, reply, spec, compiler report, weights, scores, model, interface, flags) in
  `results/attempts/<id>/`, failures included; nothing deleted or skipped.

## 7. What counts as zero training

- No gradient step, no optimiser, no selection or editing of an LLM output using any rollout.
- One reply per attempt in a fresh context; the model never sees a simulation, score or earlier attempt.
- The reply's spec is compiled deterministically and scored once on the scoring seeds. The compiler's only numeric
  choice (the scale of a `linear` unit) comes from the spec's declared range and tolerance, not from data.
- Not allowed in this track: feedback / revision rounds, best-of-N selection presented as a result, tuning hint text
  after seeing attempt scores. Rollouts are allowed only for the baselines in section 5, which are labelled as such.

## 8. Success bar and reporting

- **"Works"** = at least one Claude arm meets the target (section 3) on Hopper-v5 at some hint level. Walker2d is reported
  under the same rule, separately. The report states the lowest level reached per model and task, or **"did not work"**
  if none, with the partial-credit curves either way.
- Every number goes to git-ignored `results/` (report: `results/cpg_report.md`); git holds code and docs only. The
  MuJoCo version is recorded in `results/MANIFEST.md`.

## 9. Stop rule (timebox)

- No new LLM call after **2026-11-23 18:00 CST**. Replies already received may still be scored; the report is written on
  2026-11-23 whatever the state. Unfinished cells are reported with their actual n and marked incomplete.
- Changing the target, metric, levels or counts needs a further dated addendum committed before the affected attempts.

## 10. Prior art (TO VERIFY; not cited as fact until checked at the source)

Web access was not available when this was written, so none of these has been checked against its source. Each is
named only as a lead, and no claim about its content is made here:

- "Sparks of Weight-Space Programming", the blog post at https://rikiyat.github.io/blog/weight-space-programming/
  (authors, full title, date and venue as given in `README.md`, to be verified at the source; positioning: this track is
  the locomotion slice).
- SayTap (LLM to foot-contact patterns for quadruped locomotion).
- "Prompt a Robot to Walk with Large Language Models".
- Eureka (LLM writes reward code; RL trains the policy), the contrast already in `README.md`.
- Language to Rewards.
- Tracr (compiling programs to transformer weights).
- "A survey on CPG-inspired control models and system implementation" (IEEE TNNLS).
- Ijspeert 2008, central pattern generators for locomotion control (review).
- A search for LLM-designed CPG / oscillator controllers and for LLM-as-optimiser gait tuning with rollout feedback.
