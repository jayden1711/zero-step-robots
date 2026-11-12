# Abstract (draft, 2026-11-11)

**Can an LLM write a walking controller without training? A pre-registered negative / partial result.**

Recent work shows that general LLMs can read and edit neural-network weights from a plain-language goal (Takehi, Teoh,
Zhang, Khattab, "Sparks of Weight-Space Programming", blog post, 2026, not peer-reviewed). We test the locomotion slice
that work does not cover: with zero gradient steps, can an LLM write the parameters of a controller that makes a
simulated legged robot walk? The LLM (Claude Opus 5.5 and Sonnet 5.5, isolated subscription CLI) designs an oscillator /
central-pattern-generator network (up to four phase oscillators feeding a 16-unit tanh layer with balance feedback) in a
small spec language that a deterministic compiler turns into exact weights. The pre-registered target is at least 3 m of
forward travel before any fall, in Gymnasium MuJoCo Hopper-v5 and Walker2d-v5, on 100 held-out episodes, with at least 5
of 10 attempts passing per model.

With one reply per attempt and no feedback, none of 120 attempts passes at any of three gait-hint levels (best 1.08 m on
hopper, 1.30 m on Walker2d); most designs fall within two seconds. In a second pre-registered arm the model sees a fixed
summary of practice-episode rollouts and revises its design five times, with no code-side search or selection: 2 of 10
Opus attempts pass on hopper (6.42 m and 6.90 m; one hops through all 1000 steps of every held-out episode, after the model read
from the contact pattern that its previous design never left the ground), Sonnet passes none, and no attempt passes on
Walker2d, where Opus got worse with feedback. A random-search proposer with the same six-design budget never passes from a random start; started from the model's own first designs, it passes only where that start already passed. No
model meets the target on either task. A hand-built CPG of the same network passes on hopper, so there the gap lies in the
LLM-written controllers, not in the representation; on Walker2d the hand-built CPG did not pass, so headroom there was not
shown. Every attempt, failures included, the pre-registrations and a pre-registered clip set are published.
