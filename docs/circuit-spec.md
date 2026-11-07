# Circuit spec language (v0, first compile)

`circuitc/` compiles a small JSON spec into the weights of the architecture every arm uses
(`h = tanh(W1 obs + b1)`, `a = W2 h + b2`, 16 hidden units). It is plain deterministic code (numpy only, no repo
imports) with tests in `tests/test_circuitc.py`. See the docstring in `circuitc/compiler.py` for the grammar.

Primitives (each takes one hidden unit):
- `linear`: contributes `to[a] * (sum_i inputs[i] * obs[i])` to action `a`. A tanh unit cannot be exactly linear, so
  the spec states the input `range` and relative `tol` it needs; the compiler picks the input scale so the error is
  at most `tol` inside that range and reports it. Outside the range the unit saturates.
- `reflex`: contributes `to[a] * tanh(sharpness * (sum_i inputs[i] * obs[i] - threshold))`. Exact.
- `bias`: constant action offsets.

Not expressible here, and therefore a compile error (never approximated): oscillators or any state/time (the
architecture is feedforward on the raw observation), more units than hidden units, unknown inputs or outputs,
weights beyond 1e4 in magnitude.

Usage: `python -m circuitc SPEC.json OUT.json` then score `OUT.json` with `python -m zsr.harness <task> --weights OUT.json`.
`scripts/run_circuit.sh` compiles and scores the two fixtures in `circuitc/examples/` (written by the repo author as
compiler tests; they are not LLM outputs). No LLM has written a spec yet.
