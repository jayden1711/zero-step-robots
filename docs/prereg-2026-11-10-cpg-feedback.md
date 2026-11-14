# Pre-registration addendum 2026-11-10: CPG feedback arm

Written 2026-11-10 (CST) on an owner decision ("option (b)", relayed by the organizer the same day), **before any code,
prompt, baseline or attempt of this arm exists**. It is committed on its own (docs only) before anything below is built
or run. It extends `docs/prereg-2026-11-09-cpg.md` (the CPG track; call it "the track prereg"). Everything in the track
prereg that this file does not change still holds: network `cpg-v1`, spec language and compiler, tasks and versions,
metric, pass rules, isolation, logging, stop date. **The no-feedback result of the track stays reported exactly as it
is** (all 120 attempts, verdict "did not work"); this arm neither replaces nor re-scores it.

## 1. Question

With zero training, does the model reach the 3 m target if it may **look at a fixed summary of rollouts of its own
design on dev seeds and revise it**, for a fixed number of rounds? Every number in every design still comes from the
model; code only compiles, simulates, summarises and scores. This is closer to an LLM-in-the-loop design process, and
it is labelled as such everywhere: it is not "zero-shot".

## 2. Protocol (one attempt)

- **Rounds.** Round 0 is a first design; then **5 revision rounds** (rounds 1 to 5), so 6 designs and **6 model calls**
  per attempt.
- **Each call is a fresh, isolated `claude -p` call** (same flags, empty cwd under `/var/tmp`, probe per batch, email
  redaction, as in the track). There is no session state: the runner sends the whole history in one prompt. Round k's
  prompt = the round-0 prompt + for each earlier round j < k: the model's round-j reply verbatim, then the round-j
  feedback summary (section 3) + a fixed revision instruction. No other text is added, and nothing is edited, shortened
  or selected.
- **Final design.** The **round-5 reply** is the attempt's result. The revision instruction says so and says that an
  earlier design may be resubmitted unchanged. Code never picks a "best round": no selection by any score.
- **Failures.** A round whose reply has no valid spec, or whose spec does not compile, gets the parse / compile error
  message as its feedback (that round's design is then "no controller"). If the round-5 reply fails, the attempt scores
  as a failure (d = 0), as in the track. Transport failures (no reply) may be repeated once at the same round, both
  logged, as in the track.
- **The model never sees a scoring seed** or any score computed on one.

## 3. The feedback summary (exact contents)

Computed by `cpg-v1` on **dev seeds 0..9** (10 episodes; disjoint from the scoring seeds 10000..10099), with the same
harness and compiled weights that scoring uses. Plain text, fixed layout, numbers rounded to 2 decimals (3 for angles in
radians):

1. **Per episode (10 rows):** seed, d (forward displacement to the last healthy step, m), time survived (s), and how the
   episode ended: `cut off at 1000 steps`, or the first healthy condition that failed (`height too low`, `height too
   high` (walker2d), `torso angle out of range`, `state out of range`).
2. **Aggregate over the 10 episodes:** mean / min / max d; mean time survived; mean forward speed (d / time survived);
   the count of episodes with d >= 3 m.
3. **Episode seed 0, in detail:**
   - per joint (in action order): min and max joint angle, mean |action|, fraction of steps with |action| >= 0.99;
   - torso angle min / max, torso height min / max;
   - foot-ground contact: fraction of steps in contact and number of touchdowns (contact onsets), per foot
     (hopper: 1 foot; walker2d: right, left), using the env's floor contacts with the foot geoms;
   - a trace of the first 1.5 s every 0.1 s (15 rows): time, x, torso height, torso angle, contact flag per foot, and the
     oscillator phase(s) mod 2 pi.
4. **Compiler notes:** for each `linear` unit, the fraction of steps of episode seed 0 in which its input sum was
   outside its declared `range` (where it saturates).

Nothing else: no gradient, no suggested change, no comparison with any baseline, no target value other than the 3 m bar
the round-0 prompt already states.

## 4. Cells, models, hint levels, counts

- **Models:** Claude Opus 5.5 (`claude-opus-5-5`) and Claude Sonnet 5.5 (`claude-sonnet-5-5`), subscription CLI.
- **Hint level: H2** (the full hint; the frozen v3 hint files of the track, unchanged), on **Hopper-v5 and Walker2d-v5**.
- **10 attempts per model x task.** 4 cells x 10 attempts x 6 calls = **240 calls**, plus one isolation probe per batch.
- **Conditional H0 stage:** only if an H2 cell meets the target, the same model x task runs at H0 (10 attempts x 6
  calls = 60 calls per such cell), within the timebox.
- **Hard caps:** at most **330 Claude calls** in this arm, including probes and transport repeats. Per-call timeout
  1800 s. Token use (input, output, cache) is recorded per call from the CLI's `usage`; expected per call ~6k to ~45k
  input tokens (the history grows by round) and ~10k output tokens median, the tail up to ~80k as in the track. No
  per-call token cap is imposed beyond the CLI's own.

## 5. Prompts

New frozen files (SHA-256 in `prompts/SHA256SUMS-cpg-feedback.txt`, committed before any attempt):
- `template_v4fb.md`: the track's `template_v3.md` with only the opening paragraph changed to describe the protocol
  (you cannot run code yourself; after each design you get a test summary on practice episodes; 5 revisions; the round-5
  design is final and scored on different, held-out episodes). Task, format and H2 hint text are the v3 files,
  unchanged.
- `feedback_round_v4fb.md`: the fixed text around each round's summary and the revision instruction.
The round-0 prompt therefore differs from the no-feedback H2 prompt only in that opening paragraph.

## 6. Scoring and pass bar

- Scoring seeds 10000..10099, held out from the feedback. Metric, clean episode, attempt pass (mean d >= 3 m and >= 50
  clean episodes), arm meets target (>= 5 of 10 attempts pass): all as in the track prereg.
- **Primary:** the round-5 design. **Secondary (reported, never fed back, never used for selection):** every round's
  design is also scored on the scoring seeds, giving a per-round curve of the held-out score.

## 7. Baselines

1. **No-feedback arm:** the track's H2 cells (already run, 10 attempts per model x task). Also, as an internal control,
   this arm's own round-0 designs (one fresh no-feedback design per attempt).
2. **Random-search proposer, same feedback budget (RS-random):** per task, 10 runs; each run makes 6 designs. Design 0 is
   a random CPG from the track's fixed random-CPG distribution (seeds 100..109, disjoint from the track's 0..49); each
   later design perturbs every number of the best design so far (Gaussian, sd = 0.3 x |value| + 0.1; oscillator
   names, structure and declared ranges kept) and becomes the best if its dev mean d (the same dev seeds 0..9) is higher.
   The final design is the best so far after design 5, scored once on the scoring seeds.
3. **Random-search proposer from the model's start (RS-from-LLM):** the same procedure, but design 0 is the model's own
   round-0 design of each attempt (so 10 runs per model x task), isolating "the model's revisions" from "any revisions
   from the same start".
Both RS baselines use code search by construction; they are baselines, not LLM arms, and use exactly the same budget of
6 designs and 6 x 10 dev episodes. The tuned CPG and PPO of the track stay as headroom and upper references.

## 8. What still counts as "no training" here

No gradient step and no optimiser acting on the model's numbers; no code-side search, selection or editing of any
design in the LLM arm; every number of every design is written by the model. What is new and labelled: the model sees
dev-seed rollout summaries of its own designs (section 3) and revises, for 5 rounds.

## 9. Compute

CPU only, through `~/projects/bin/sim-run` (nice 10, one thread), load < 20, at most 2 sim processes of this arm at a time.
Per attempt: 6 x 10 dev episodes for feedback + 6 x 100 scoring episodes (each <= 1000 steps). The runner itself only
waits on `claude -p` and launches each rollout as a separate `sim-run` process. RS baselines: (10 + 20) runs x 6 designs
per task, 10 dev episodes each, + one scoring per run. No GPU.

## 10. Order and stop rule

1. This file committed. 2. Code, prompt files and the summary generator committed, with prompt hashes. 3. RS-random
baselines (independent of any LLM output). 4. Feedback attempts: hopper (Opus and Sonnet streams may run side by side,
one call at a time each), then walker2d. 5. RS-from-LLM after the corresponding round-0 designs exist. 6. Report:
`results/cpg_feedback_report.md`, verdict per section 6, "did not work" stated plainly if so.
Stop: no new LLM call after 2026-11-23 18:00 CST (track prereg). Any change to the above needs a further dated addendum
committed before the affected attempts.

## 11. Contrast with prior work

- Wang, Zhang, Chen, Sreenath, "Prompt a Robot to Walk with Large Language Models" (Prompt2Walk), IEEE CDC 2024,
  arXiv:2309.09969: the LLM is the controller, queried every control step from few-shot prompts. Here the LLM writes a
  network once per round; the network alone runs the robot.
- Ma et al., "Eureka", ICLR 2024, arXiv:2310.12931, and Yu, Xia et al., "Language to Rewards for Robotic Skill Synthesis",
  CoRL 2023, arXiv:2306.08647: the LLM writes reward code and iterates on training / optimisation feedback, while RL (Eureka) or
  MuJoCo MPC (Language to Rewards) finds the actions. Here no optimiser runs; the model's numbers are the controller.
- LLM-as-optimiser work with rollout feedback in general: TO VERIFY (not searched; not cited until checked).
