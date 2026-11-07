#!/usr/bin/env bash
# Pilot arm for one local model, queued behind other GPU jobs. One model on the GPU at a time.
# usage: scripts/run_local.sh qwen3-coder-30b|gpt-oss-20b RESULTS_DIR
# Starts llama-server inside gpu-run (the lock is held for the whole run), runs scripts/run_pilot.py local, stops the server.
set -euo pipefail
NAME=$1; RES=$2; PORT=8089
HERE=$(cd "$(dirname "$0")/.." && pwd)
PY=${PY:-python3}; BIN=$HOME/opt/wiif/llama.cpp/build/bin/llama-server
case "$NAME" in
  qwen3-coder-30b) GGUF=$HOME/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf; NEED=11500; EXTRA="--n-cpu-moe 28" ;;
  gpt-oss-20b)     GGUF=$HOME/models/gpt-oss-20b-MXFP4.gguf; NEED=11500
                   EXTRA="--n-cpu-moe 4 --chat-template-kwargs {\"reasoning_effort\":\"medium\"}" ;;
  *) echo "unknown model"; exit 1 ;;
esac
[ -f "$GGUF" ] || { echo "missing $GGUF"; exit 4; }
inner() {
  mkdir -p "$RES/pilot"
  nice -n 10 "$BIN" -m "$GGUF" --host 127.0.0.1 --port $PORT --jinja --no-webui -ngl 99 $EXTRA \
    -c 32768 --parallel 1 --threads 6 --threads-batch 6 > "$RES/pilot/server_$NAME.log" 2>&1 &
  SRV=$!; trap 'kill $SRV 2>/dev/null; wait $SRV 2>/dev/null' EXIT
  up=0
  for _ in $(seq 1 600); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && { up=1; break; }; kill -0 $SRV || exit 5; sleep 2; done
  [ "$up" -eq 1 ] || { echo "llama-server not healthy after 1200 s" >&2; exit 6; }
  $PY "$HERE/scripts/run_pilot.py" local --results "$RES" --name "$NAME" --port $PORT --n 10
  rc=$?
  exit $rc
}
export -f inner 2>/dev/null || true
export NAME RES PORT HERE PY BIN GGUF NEED EXTRA
exec ~/projects/bin/gpu-run --need-mib $NEED --wait 43200 --label zero-step-robots -- bash -c "$(declare -f inner); inner"
