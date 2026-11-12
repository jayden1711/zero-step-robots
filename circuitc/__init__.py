"""circuitc: compile a small functional spec into exact weights of a one-hidden-layer tanh MLP.

    h = tanh(W1 @ obs + b1)        a = W2 @ h + b2

No repo-specific imports; numpy only. See docs/circuit-spec.md for the language.
"""
from .compiler import CompileError, compile_spec, evaluate_spec, forward  # noqa: F401
from .cpg import compile_cpg, simulate_spec  # noqa: F401
