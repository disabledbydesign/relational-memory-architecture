#!/bin/bash
# C2C launcher — two Claude instances on offset cycles.
# Clean shutdown via signal traps so stop.sh doesn't leave orphan sleeps.

set -e

SESSION_DIR="/Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18"
WORK_DIR="/Users/june/Documents/GitHub/liberation_labs"
PROMPT_A="$SESSION_DIR/prompt_instance_a.txt"
PROMPT_B="$SESSION_DIR/prompt_instance_b.txt"
PID_FILE="$SESSION_DIR/.c2c_pids"
LOG_DIR="$SESSION_DIR/logs"
ARTIFACT_DIR="$SESSION_DIR/artifacts"

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

# Loop with signal trap: when SIGTERM arrives, kill current child and exit cleanly.
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
      claude -p "$(cat "$prompt_file")" --model "$model" --permission-mode bypassPermissions
    ) >> "$log_file" 2>&1 &
    CHILD_PID=$!
    wait "$CHILD_PID" 2>/dev/null || echo "=== $(date): Instance $name cycle errored (exit $?) ===" >> "$log_file"
    echo "=== $(date): Instance $name sleeping $CYCLE_SECONDS s ===" >> "$log_file"
    sleep "$CYCLE_SECONDS" &
    CHILD_PID=$!
    wait "$CHILD_PID" 2>/dev/null || true
  done
}

# Export function so backgrounded subshells can use it
export -f run_loop
export SESSION_DIR WORK_DIR PROMPT_A PROMPT_B LOG_DIR MODEL_A MODEL_B CYCLE_SECONDS

# Launch Instance A (no offset)
bash -c 'run_loop a "$MODEL_A" "$PROMPT_A" 0' &
echo $! >> "$PID_FILE"

# Launch Instance B (offset)
bash -c "run_loop b \"\$MODEL_B\" \"\$PROMPT_B\" $OFFSET_SECONDS" &
echo $! >> "$PID_FILE"

echo "C2C session started."
echo "  Instance A (Opus):   PID $(sed -n 1p "$PID_FILE") — first cycle firing NOW"
echo "  Instance B (Sonnet): PID $(sed -n 2p "$PID_FILE") — first cycle in ~15 min"
echo ""
echo "Watch logs:"
echo "  tail -f $LOG_DIR/instance_a.log"
echo "  tail -f $LOG_DIR/instance_b.log"
echo ""
echo "Watch conversation (the interesting part):"
echo "  open $SESSION_DIR/CONVERSATION.md in your editor; it'll auto-reload"
echo ""
echo "Stop cleanly with: $SESSION_DIR/stop.sh"
