# Can an LLM write a walking controller without training? A pre-registered negative / partial result

*Draft write-up, 2026-11-15 (CST). Not published. Blog / workshop length. Simulation only: no real robot is involved anywhere.*

Every measured number below links to the file it comes from: a report section in `results/`, an attempt's own
`score.json`, or, for the few derived statistics (bounds, a p-value, episode-length medians), the script that computes
them from those files, [`scripts/writeup_numbers.py`](../scripts/writeup_numbers.py). That script re-reads every file
linked here and fails if any quoted number differs. Design constants (the 3 m bar, 100 held-out episodes, 10 attempts per
cell, the 5-of-10 rule) come from the pre-registrations linked in the Setup section.

## TL;DR

- **Question.** With zero gradient steps, can Claude write the parameters of an oscillator (CPG) network that makes
  Gymnasium MuJoCo `Hopper-v5` and `Walker2d-v5` travel at least 3 m forward before falling?
- **One reply per attempt, no feedback: no.** [0 of 120 attempts pass](../results/cpg_report.md#verdict-prereg-section-8)
  across two models, two tasks and three hint levels. The best designs reach
  [1.08 m](../results/attempts/cpg-claude-opus-5-5_hopper_H0_cpgspec_06/score.json) (hopper) and
  [1.30 m](../results/attempts/cpg-claude-opus-5-5_walker2d_H1_cpgspec_01/score.json) (Walker2d), about what a robot gets
  by falling forward on purpose ([0.74 m and 0.96 m](../results/cpg_report.md#hopper-necessity-table-and-cpg-baselines)).
- **Five revisions from a practice-episode summary: partly.** On hopper
  [2 of 10 Opus 5.5 attempts pass](../results/cpg_feedback_report.md#hopper)
  ([6.42 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_03/score.json),
  [6.90 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/score.json)). One of them hops for all 1000 steps in
  [every held-out episode](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/score.json). The pre-registered target
  (5 of 10 per model) was not met on either task, and on Walker2d Opus [got worse with feedback](../results/cpg_feedback_report.md#walker2d).
- **The network can do it on hopper.** A hand-structured CPG of the same form, with parameters searched on practice seeds,
  passes ([3.27 m](../results/cpg/baselines/hopper/tuned_cpg.score.json)), so on hopper the gap is in the written
  parameters, not the representation. On Walker2d the same search [did not pass](../results/cpg/baselines/walker2d/tuned_cpg.score.json),
  so there the negative result is weaker.
- **What we did not learn:** whether zero-step LLM designs carry *any* useful information. A binary 3 m bar that no attempt
  clears cannot measure that. The follow-up pre-registration ([`docs/prereg-followup-draft.md`](prereg-followup-draft.md))
  measures it with no new LLM calls.

## 1. Why this question

Takehi, Teoh, Zhang and Khattab ("Sparks of Weight-Space Programming", blog post, Nov 2026, not peer-reviewed) report
that general LLMs can read raw network weights and edit them toward a plain-language goal, with no gradient descent, on
language models. Locomotion is a hard place to test that claim. A controller's numbers only mean something through a
contact-rich dynamical system that the model cannot run. Prior LLM-for-locomotion work keeps an optimiser or a trained
policy in the loop: SayTap (the LLM writes foot-contact patterns, a trained RL controller executes them), Prompt2Walk (the
LLM is queried at every control step), Eureka and Language to Rewards (the LLM writes reward code; RL in NVIDIA Isaac Gym,
or MuJoCo MPC, finds the actions). Here there is no optimiser: the model's numbers are the controller.

## 2. Setup

Pre-registrations, each committed before the runs it governs (git history shows the order):
[PLAN.md addendum 2026-11-09](../PLAN.md) (the distance target), [the CPG track](prereg-2026-11-09-cpg.md), and
[the feedback arm](prereg-2026-11-10-cpg-feedback.md).

- **Tasks.** Gymnasium 1.4.0 `Hopper-v5` and `Walker2d-v5` on MuJoCo 3.17.0 ([`results/MANIFEST.md`](../results/MANIFEST.md)):
  1000-step episodes at dt 0.008 s, so 8 s at most.
- **The network (`cpg-v1`).** Up to four phase oscillators with couplings and sensory frequency modulation. Their cos/sin
  outputs and the raw observation feed one layer of 16 tanh units, then a linear action layer clipped to [-1, 1]. The
  same 16-unit layer is used by every arm of the project, including PPO. The model does not write raw weights. It writes
  a spec in a small language (oscillators, couplings, `linear` and `reflex` units), and a deterministic compiler
  ([`circuitc/`](../circuitc/)) turns the spec into exact weights. The compiler does no fitting and sees no rollout.
- **Metric.** d = forward displacement of the root to the *last healthy step*, so the fall itself earns nothing. An
  attempt **passes** when mean d >= 3 m over 100 held-out episodes (seeds 10000-10099) and at least 50 of those 100 are
  clean (d >= 3 m). A model x task x hint cell **meets the target** when at least 5 of its 10 attempts pass.
- **Hints.** H2 gives the gait structure, numeric ranges and sign conventions taken from the env XML and Gymnasium docs.
  H1 gives the structure in words. H0 gives none. Hint text was frozen with SHA-256
  ([`prompts/SHA256SUMS-cpg.txt`](../prompts/SHA256SUMS-cpg.txt)) before any attempt and before the tuned baseline existed.
- **Models and isolation.** Claude Opus 5.5 and Sonnet 5.5 ran through the subscription CLI (`claude -p`, no paid API).
  Each call ran in a fresh, empty working directory with no tools, no MCP and no instruction files, with a machine-checked
  isolation probe per batch and the account email redacted before anything was written
  ([CRITIQUES.md item 12](../CRITIQUES.md)).

### Why distance and not return

Earlier arms of this project scored the env's own return, and that misled. The hopper reward pays +1 for every healthy
step, so a controller that stands still for 1000 steps scores about 1000. In those arms (raw weights and Python
controllers) the highest-return hopper attempts stood still. For example, all
[10 of 10 Opus raw-weight attempts with the strict prompt stood (median return 999.0, distance about 0 m)](../results/pilot_report.md#finding-the-llm-exploited-the-healthy-reward-hopper).
The CPG track therefore states the distance-to-last-healthy-step rule as the score in the prompt, and reports return
only as the env's own number.

## 3. Result 1: one reply, no feedback: 0 of 120

| task | attempts | pass | best d | median episode length per cell |
|---|---|---|---|---|
| Hopper-v5 | [60](../results/cpg_report.md#hopper-llm-attempts-mode-cpgspec) | [0](../results/cpg_report.md#hopper-llm-attempts-mode-cpgspec) | [1.08 m](../results/attempts/cpg-claude-opus-5-5_hopper_H0_cpgspec_06/score.json) | [25-57 steps](../scripts/writeup_numbers.py) |
| Walker2d-v5 | [60](../results/cpg_report.md#walker2d-llm-attempts-mode-cpgspec) | [0](../results/cpg_report.md#walker2d-llm-attempts-mode-cpgspec) | [1.30 m](../results/attempts/cpg-claude-opus-5-5_walker2d_H1_cpgspec_01/score.json) | [7-175 steps](../scripts/writeup_numbers.py) |

Every reply compiled, so the spec format was not the failure ([report](../results/cpg_report.md#hopper-llm-attempts-mode-cpgspec):
0 failures in every cell). In every cell the median episode ends within about 1.4 s. The few designs that last 1000 steps
stand still: for example
[Opus hopper H0 #00 survives every episode and travels 0.24 m](../results/cpg_report.md#hopper-llm-attempts-mode-cpgspec).

More hint did not produce a pass. A post-hoc check (labelled post hoc in the report) found that the sign of the
torso-pitch-to-hip feedback gain, the one sign that corrects a forward lean, is right far more often at H2
([7 of 10 Opus, 10 of 10 Sonnet](../results/cpg_report.md#hopper-llm-attempts-mode-cpgspec)) than at H1 or H0. A correct
sign alone does not give a gait: Sonnet H2 got it right in 10 of 10 and its best design reached
[0.94 m](../results/cpg_report.md#hopper-llm-attempts-mode-cpgspec).

**How strong is "0 of 120"?** If every attempt independently passed with some fixed probability, 0 of 120 bounds that
probability below [2.5%](../scripts/writeup_numbers.py) (one-sided 95%), and 0 of 60 per task bounds it below
[4.9%](../scripts/writeup_numbers.py). That is far from the 50% the pre-registered target requires. It is the cleanest
statement the data supports.

### Baselines: what the bar means

| row (hopper / Walker2d, mean d) | hopper | Walker2d | source |
|---|---|---|---|
| zero weights | [-0.01 m](../results/cpg/baselines/hopper/zero.score.json) | [-0.17 m](../results/cpg/baselines/walker2d/zero.score.json) | necessity table |
| fall-forward lunge (best constant action) | [0.74 m](../results/cpg/baselines/hopper/lunge.score.json) | [0.96 m](../results/cpg/baselines/walker2d/lunge.score.json) | necessity table |
| open-loop sinusoid, tuned on practice seeds | [0.46 m](../results/cpg/baselines/hopper/sinusoid.score.json) | [-0.05 m](../results/cpg/baselines/walker2d/sinusoid.score.json) | necessity table |
| 50 random CPGs: median / best | [-0.02 / 0.35 m](../results/cpg_report.md#hopper-necessity-table-and-cpg-baselines) | [-0.16 / -0.06 m](../results/cpg_report.md#walker2d-necessity-table-and-cpg-baselines) | [random_cpg/](../results/cpg/baselines/hopper/random_cpg/) |
| hand-structured CPG, parameters searched on practice seeds | [**3.27 m, passes**](../results/cpg/baselines/hopper/tuned_cpg.score.json) | [1.29 m, does not pass](../results/cpg/baselines/walker2d/tuned_cpg.score.json) | [search log](../results/cpg/baselines/hopper/tuned_cpg.search.json) |
| PPO, 1M env steps, same 16-unit layer | [12.66](../results/cpg/ppo/hopper/hopper_ppo_seed0.score.json) to [17.48 m](../results/cpg/ppo/hopper/hopper_ppo_seed1.score.json) | [3.75](../results/cpg/ppo/walker2d/walker2d_ppo_seed2.score.json) to [16.57 m](../results/cpg/ppo/walker2d/walker2d_ppo_seed0.score.json) | upper reference |

Two things follow. First, the bar is not trivially reachable: no simple baseline comes near it, and the best LLM designs
sit at the level of a deliberate forward fall. Second, on hopper the bar is reachable *within the same network*: the
tuned CPG, which used [19,650 practice episodes](../results/cpg/baselines/hopper/tuned_cpg.search.json) of search, passes
with [80 of 100 clean episodes](../results/cpg/baselines/hopper/tuned_cpg.score.json). It still falls in
[every episode](../results/cpg/baselines/hopper/tuned_cpg.score.json) (full-length fraction 0.0) after covering 3 m. It
shows that the network can produce the motion, not a sustained gait. On Walker2d the same budget
[did not reach 3 m](../results/cpg/baselines/walker2d/tuned_cpg.score.json), so headroom for this network on Walker2d is
not shown. PPO's plain network does reach it there, so the bar itself is reachable.

## 4. Result 2: five revisions from a practice-episode summary

The second pre-registered arm keeps every number the model's own but lets it see a fixed plain-text summary of its design
on practice seeds 0-9: per-episode distance and how the episode ended, joint ranges, foot-contact fractions and
touchdowns, and a 1.5 s trace. It then revises its design five times. Each call is fresh, and the whole history is
resent. The round-5 reply is the result: code never picks a best round. The held-out seeds are never shown. This is an
LLM-in-the-loop design process, labelled as such, not zero-shot.

| cell (round-5 design, H2 hint) | pass | median d | best d |
|---|---|---|---|
| Opus 5.5, hopper | [**2 of 10**](../results/cpg_feedback_report.md#hopper) | [1.27 m](../results/cpg_feedback_report.md#hopper) | [6.90 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/score.json) |
| Sonnet 5.5, hopper | [0 of 10](../results/cpg_feedback_report.md#hopper) | [0.94 m](../results/cpg_feedback_report.md#hopper) | [0.96 m](../results/attempts/fb-claude-sonnet-5-5_hopper_H2_00/score.json) |
| Opus 5.5, Walker2d | [0 of 10](../results/cpg_feedback_report.md#walker2d) | [-1.10 m](../results/cpg_feedback_report.md#walker2d) (round 0: [-0.81 m](../results/cpg_feedback_report.md#walker2d)) | [0.83 m](../results/cpg_feedback_report.md#walker2d) |
| Sonnet 5.5, Walker2d | [0 of 10](../results/cpg_feedback_report.md#walker2d) | [0.68 m](../results/cpg_feedback_report.md#walker2d) | [0.97 m](../results/attempts/fb-claude-sonnet-5-5_walker2d_H2_04/score.json) |

All [240 of 240 pre-registered calls ran](../results/cpg_feedback_report.md#budget), using about
[2.86M input tokens (including cache) and 1.74M output tokens](../results/cpg_feedback_report.md#budget).

**The two passes are different stories.**

- [Attempt 03](../results/attempts/fb-claude-opus-5-5_hopper_H2_03/) passed **before any feedback**: its round-0 design
  already scored [6.12 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_03/r0/score.json). Revisions kept it in the
  [4.7-6.4 m range](../results/cpg_feedback_report.md#hopper) and it ended at
  [6.42 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_03/score.json). Its round-0 prompt differs from the
  no-feedback H2 prompt only in the opening paragraph that describes the protocol.
- [Attempt 08](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/) is the one case where feedback plainly did the work.
  Round 0 scored [-0.06 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/r0/score.json) and round 1
  [0.13 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/r1/score.json): round 1 survived every practice episode
  but its [summary](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/r1/feedback.txt) showed the foot on the ground
  99% of the steps with one touchdown. The [round-2 reply](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/r2/reply.md)
  reads it directly ("the robot never left the ground ... the gait needs real flight phases"), raises the leg amplitude
  and adds a thigh push-off in phase with leg extension. Round 2 hopped
  [5.43 m](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/r2/score.json), and round 5 reached
  [6.90 m with 100 of 100 episodes running all 1000 steps](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/score.json).
  That is a sustained hop, which the search-tuned baseline never achieves.

**Is it the model, or just revising?** The pre-registration included two random-search proposers with the same budget of
six designs and the same practice-episode scores. Started from a random CPG, random search
[never passes](../results/cpg_feedback_report.md#hopper) (hopper best [0.48 m](../results/cpg_feedback/rs/hopper/random/)).
Started from each Opus round-0 design, it passes [once in 10](../results/cpg_feedback/rs/hopper/fromllm_claude-opus-5-5/),
from the attempt-03 start that already passed ([6.12 m](../results/cpg_feedback/rs/hopper/fromllm_claude-opus-5-5/)).
From attempt 08's start, random revision did not find the hop the model found. That is one case: an anecdote, not a rate.

**Is 2 of 10 better than 0 of 10?** Not measurably. Against the no-feedback H2 Opus cell (0 of 10), a one-sided Fisher
exact test gives [p = 0.24](../scripts/writeup_numbers.py), and the 95% interval for a 2-of-10 rate runs from
[2.5% to 55.6%](../scripts/writeup_numbers.py). The arm-level verdict is the pre-registered one:
[target not met on either task](../results/cpg_feedback_report.md#verdict-prereg-s6).

**Feedback can also hurt.** On Walker2d, Opus's held-out median *fell* round by round, from
[-0.81 m at round 0 to -1.10 m at round 5](../results/cpg_feedback_report.md#walker2d) (moving backward), while Sonnet's
rose to [0.68 m](../results/cpg_feedback_report.md#walker2d) without passing.

Practice and held-out scores agree closely for every passing design (e.g. attempt 08:
[6.90 practice, 6.90 held-out](../results/cpg_feedback_report.md#hopper)), so the passes are not overfit to the
practice seeds.

## 5. What this does and does not show

**Shows.**
1. With one reply and no rollouts, Claude Opus 5.5 and Sonnet 5.5 did not write a CPG controller that walks 3 m in these
   two MuJoCo tasks, at any of three hint levels. The per-attempt pass rate is bounded well below the 50% bar.
2. On hopper the representation is not the limit (the tuned CPG passes). The failure lies in the written parameters.
3. Given a rollout summary and five revisions, Opus produced LLM-written controllers that clear 3 m on hopper, including
   one sustained gait. Seen across rounds, the revision process follows the evidence in the summary, at least once.
4. Return is a misleading score for zero-shot locomotion. Distance to the last healthy step is not.

**Does not show.**
- That LLMs "cannot" do this. There were two models, one network family, two tasks and 10 attempts per cell. The CLI
  exposes no sampling seed, so hosted-model runs are not exactly reproducible ([CRITIQUES.md item 13](../CRITIQUES.md)).
- Anything about Walker2d headroom: the tuned CPG did not pass there, so a Walker2d failure may be the network's, not the
  model's.
- Whether the zero-step designs are *close*. A design at 1 m might be one parameter away from 3 m, or nowhere near it.
  The binary bar cannot tell, which is the motivation for the follow-up.
- Anything about real robots. Everything here is simulation.

## 6. Limitations

- **Small cells.** Ten attempts per cell supports bounds, not rates. No significance claims are made beyond those above.
- **Hint fairness.** H1 and H2 give information PPO does not get. H0 is the closest to parity.
- **The tuned baseline falls.** It passes the metric but not as a gait (see C2 in [CRITIQUES.md](../CRITIQUES.md)).
- **Saturation not analysed** for the no-feedback designs (how often `linear` units ran outside their declared range).
- **One earlier contamination incident** (an unrelated instruction file in context for some earlier, non-CPG arms) was
  found, fixed and rerun. The affected attempts are kept and excluded from the tables
  ([`results/pilot_report.md`](../results/pilot_report.md#contaminated-attempts-contaminated-tmpclaudemd-stock-environment-excluded-from-every-table-above)).
  The CPG track ran entirely under the fixed isolation.
- **Prior-work coverage.** LLM-as-optimiser work with rollout feedback is related and has not been checked at source (TO
  VERIFY in the [README](../README.md#related-work)).

## 7. What would make zero-step success measurable

Running more LLM attempts against the same binary bar would buy little. At the observed rate it would most likely return
more zeros. The follow-up ([`docs/prereg-followup-draft.md`](prereg-followup-draft.md), draft) uses **no new LLM calls**.
It replays the 160 existing zero-step designs (120 no-feedback designs plus the 40 feedback round-0 designs) and asks a
continuous question: **how much black-box search does starting from the LLM's design save, compared with a random design
of the same kind, or with the LLM's own numbers shuffled within its structure?** It also gives Walker2d the headroom test
it lacks. Every number in it is a fixed-budget CPU computation, and each start condition has a pre-registered bar.

## Reproduce

- Tables: `scripts/cpg_report.py results` and `scripts/cpg_feedback_report.py results`. Numbers in this write-up:
  `python scripts/writeup_numbers.py results` (reads files only, runs nothing).
- Every attempt, failures included (prompt, reply, compiled design, per-episode scores):
  [`results/attempts/`](../results/attempts/), layout in [`results/README.md`](../results/README.md).
- Pre-registered clips (designs and seeds fixed before rendering, including a failing design and both tuned baselines):
  [`results/clips_cpg/`](../results/clips_cpg/).
- Objections and how each is answered: [CRITIQUES.md](../CRITIQUES.md).
