#!/bin/bash
# C2C launcher — integration design session.
# Clean shutdown via signal traps so stop.sh doesn't leave orphan sleeps.
# Generates reframe context once at launch and prepends to each prompt cycle.

set -e

SESSION_DIR="/Users/june/Documents/GitHub/relational-memory-architecture/c2c/c2c_sessions/integration-design_2026-04-20"
WORK_DIR="/Users/june/Documents/GitHub/relational-memory-architecture"
PROMPT_A="$SESSION_DIR/prompt_instance_a.txt"
PROMPT_B="$SESSION_DIR/prompt_instance_b.txt"
PID_FILE="$SESSION_DIR/.c2c_pids"
LOG_DIR="$SESSION_DIR/logs"
ARTIFACT_DIR="$SESSION_DIR/artifacts"
REFRAME_SCRIPT="/Users/june/Documents/GitHub/reframe/claude_code_bootstrap.py"
REFRAME_CONTEXT_FILE="$SESSION_DIR/.reframe_context.txt"

MODEL_A="claude-opus-4-7"
MODEL_B="claude-sonnet-4-6"

CYCLE_SECONDS=1800      # 30 minutes between cycles
OFFSET_SECONDS=900      # B starts 15 minutes after A

if [ -f "$PID_FILE" ]; then
  echo "PID file exists at $PID_FILE — another session may be running."
  echo "Run ./stop.sh first, or delete $PID_FILE if you're sure nothing is running."
  exit 1
fi

mkdir -p "$LOG_DIR" "$ARTIFACT_DIR"
touch "$LOG_DIR/instance_a.log" "$LOG_DIR/instance_b.log"
: > "$PID_FILE"

# Generate reframe context once at session launch (Ollama timeouts add ~90s — acceptable)
echo "Generating reframe context..."
REFRAME_JSON=$(cd "$WORK_DIR" && python3 "$REFRAME_SCRIPT" session-start 2>/dev/null || true)
REFRAME_CONTEXT=$(echo "$REFRAME_JSON" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
    print(ctx)
except Exception:
    pass
" 2>/dev/null || true)

if [ -n "$REFRAME_CONTEXT" ]; then
  printf '%s' "$REFRAME_CONTEXT" > "$REFRAME_CONTEXT_FILE"
  echo "Reframe context ready ($(wc -c < "$REFRAME_CONTEXT_FILE" | tr -d ' ') bytes, $(echo "$REFRAME_CONTEXT" | grep -c '^###') frameworks)"
else
  echo "WARNING: Could not generate reframe context — running without it"
  touch "$REFRAME_CONTEXT_FILE"
fi

run_loop() {
  local name="$1"
  local model="$2"
  local prompt_file="$3"
  local initial_delay="$4"
  local log_file="$LOG_DIR/instance_${name}.log"

  CHILD_PID=""
  trap 'kill "$CHILD_PID" 2>/dev/null; exit 0' TERM INT

  if [ "$initial_delay" -gt 0 ]; then
    echo "=== $(date): Instance $name waiting initial offset $initial_delay s ===" >> "$log_file"
    sleep "$initial_delay" &
    CHILD_PID=$!
    wait "$CHILD_PID" 2>/dev/null || true
  fi

  while true; do
    echo "=== $(date): Instance $name cycle start ===" >> "$log_file"
    (
      cd "$WORK_DIR"
      if [ -s "$REFRAME_CONTEXT_FILE" ]; then
        FULL_PROMPT="$(cat "$REFRAME_CONTEXT_FILE")

---

$(cat "$prompt_file")"
      else
        FULL_PROMPT="$(cat "$prompt_file")"
      fi
      claude -p "$FULL_PROMPT" --model "$model" --permission-mode bypassPermissions
    ) >> "$log_file" 2>&1 &
    CHILD_PID=$!
    wait "$CHILD_PID" 2>/dev/null || echo "=== $(date): Instance $name cycle errored (exit $?) ===" >> "$log_file"
    echo "=== $(date): Instance $name sleeping $CYCLE_SECONDS s ===" >> "$log_file"
    sleep "$CYCLE_SECONDS" &
    CHILD_PID=$!
    wait "$CHILD_PID" 2>/dev/null || true
  done
}

export -f run_loop
export SESSION_DIR WORK_DIR PROMPT_A PROMPT_B LOG_DIR MODEL_A MODEL_B CYCLE_SECONDS REFRAME_CONTEXT_FILE

# Launch Instance A (no offset)
bash -c 'run_loop a "$MODEL_A" "$PROMPT_A" 0' &
echo $! >> "$PID_FILE"

# Launch Instance B (offset)
bash -c "run_loop b \"\$MODEL_B\" \"\$PROMPT_B\" $OFFSET_SECONDS" &
echo $! >> "$PID_FILE"

echo "C2C integration design session started."
echo "  Instance A (Opus):   PID $(sed -n 1p "$PID_FILE") — first cycle firing NOW"
echo "  Instance B (Sonnet): PID $(sed -n 2p "$PID_FILE") — first cycle in ~15 min"
echo ""
echo "Watch logs:"
echo "  tail -f $LOG_DIR/instance_a.log"
echo "  tail -f $LOG_DIR/instance_b.log"
echo ""
echo "Watch conversation:"
echo "  open $SESSION_DIR/CONVERSATION.md in your editor"
echo ""
echo "Stop cleanly with: $SESSION_DIR/stop.sh"
