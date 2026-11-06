# Method direction: circuit-compiler track (owner, 2026-11-06)

Fold into PLAN.md at the next review. Not part of tonight's first stop point.

## Idea
Add a fourth way to produce a controller. The LLM writes a **functional design** in a small spec language:
what each hidden unit computes, e.g. sensor features (angle error, velocity), oscillators (frequency, phase),
reflexes (if-this-then-that thresholds), and gains. A deterministic **compiler** turns that spec into exact network
weights in the same architecture the other arms use. The LLM decides *what* the circuit should do; the compiler
handles *how* that becomes weights.

## Comparison (same envs, same scoring harness, same information as PPO)
1. Circuit compiler: LLM writes the spec, the compiler emits the weights.
2. Raw weight writing: LLM writes every weight directly (the MIT "Sparks of Weight-Space Programming" approach).
3. Python controller written by the same LLM.
4. PPO.
(+ the random-weight and zero-weight controls already in PLAN.md)

Things to measure besides score: whether the compiled weights match the spec exactly (unit tests per primitive),
how many attempts/edits each arm needs, and whether the spec is readable enough to debug a failure.

## Design notes
- The spec language should be small and closed: primitives that compile exactly into the target architecture's layers
  (linear features, ReLU thresholds/reflexes, a fixed oscillator block if the architecture has recurrence or
  takes time/phase as input). Anything the compiler can't express exactly is an error, not an approximation.
- The compiler is plain deterministic code with tests. No learning inside it.
- walk-anything plans to reuse this compiler for its symmetry-derived gait track, so keep it a separate package
  with no repo-specific imports.

## Prior art (starting points; read before designing the spec language)
- Tracr (Lindner et al., DeepMind, NeurIPS 2023, arXiv 2301.05062): compiles RASP programs into exact transformer
  weights. This is the closest analogue: a compiler from a program to weights with a known structure. It targets
  transformers and sequence tasks, not control MLPs or recurrent controllers. Code: github.com/google-deepmind/tracr.
- Neural Engineering Framework / Nengo (Eliasmith & Anderson): specifies functions and dynamics and solves for neural
  weights. It's relevant for oscillators and dynamics. (From memory; verify before citing.)
- Hand-designed CPG and neural controllers in robotics, e.g. the survey "A survey on CPG-inspired control models
  and system implementation" (IEEE TNNLS 2014). These show which primitives (oscillators, reflexes) are useful.
- No dedicated "spec language → controller weights" tool for locomotion turned up in a quick search. If that
  holds after a proper search, it's a contribution worth stating carefully.
