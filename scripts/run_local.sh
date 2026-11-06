#!/usr/bin/env bash
# Pilot arm for one local model, queued behind other GPU jobs. One model on the GPU at a time.
# usage: scripts/run_local.sh qwen3-coder-30b|gpt-oss-20b RESULTS_DIR [weights|controller] [MAX_SECONDS]
# Starts llama-server inside gpu-run (the lock is held for the whole run), runs scripts/run_pilot.py local, stops the server.
set -euo pipefail
NAME=$1; RES=$2; MODE=${3:-weights}; MAXS=${4:-0}; PORT=8089
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
    -c 32768 --parallel 1 --threads 6 --threads-batch 6 > "$RES/pilot/server_${NAME}_$MODE.log" 2>&1 &
  SRV=$!; trap 'kill $SRV 2>/dev/null; wait $SRV 2>/dev/null' EXIT
  for _ in $(seq 1 600); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && break; kill -0 $SRV || exit 5; sleep 2; done
  $PY "$HERE/scripts/run_pilot.py" local --results "$RES" --name "$NAME" --port $PORT --n 10 --mode $MODE --max-seconds $MAXS
}
export -f inner 2>/dev/null || true
export NAME RES MODE MAXS PORT HERE PY BIN GGUF NEED EXTRA
exec ~/projects/bin/gpu-run --need-mib $NEED --wait 43200 --label zero-step-robots -- bash -c "$(declare -f inner); inner"
