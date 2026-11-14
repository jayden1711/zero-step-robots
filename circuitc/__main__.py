"""python -m circuitc SPEC.json OUT_WEIGHTS.json  -> compiles (MLP, or cpg-v1 if spec has \"target\": \"cpg\"); prints the report."""
import json
import sys

from .compiler import CompileError, compile_spec
from .cpg import compile_cpg

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    try:
        if isinstance(spec, dict) and spec.get("target") == "cpg":
            params, report = compile_cpg(spec)
        else:
            params, report = compile_spec(spec)
            params = {k: v.tolist() for k, v in params.items()}
    except CompileError as e:
        sys.exit(f"compile error: {e}")
    json.dump(params, open(sys.argv[2], "w"), indent=1)
    print(json.dumps(report, indent=1))
