"""python -m circuitc SPEC.json OUT_WEIGHTS.json  -> compiles; prints the per-unit report."""
import json
import sys

from .compiler import CompileError, compile_spec

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    try:
        params, report = compile_spec(spec)
    except CompileError as e:
        sys.exit(f"compile error: {e}")
    json.dump({k: v.tolist() for k, v in params.items()}, open(sys.argv[2], "w"), indent=1)
    print(json.dumps(report, indent=1))
