#!/bin/bash
# C2C session launcher: Instance A (Opus) + Instance B (Sonnet), 30-min cycles, 15-min offset.
#
# Usage:
#   ./start.sh            -> launches both loops in background, writes PIDs to .c2c_pids
#   ./stop.sh             -> stops both loops
#
# Logs:
#   logs/instance_a.log   -> Instance A cycle outputs
#   logs/instance_b.log   -> Instance B cycle outputs
#
# Safe to re-read; session state lives in WORKING_DOCUMENT.md.

set -e

SESSION_DIR="/Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18"
WORK_DIR="/Users/june/Documents/GitHub/liberation_labs"
PROMPT_A="$SESSION_DIR/prompt_instance_a.txt"
PROMPT_B="$SESSION_DIR/prompt_instance_b.txt"
PID_FILE="$SESSION_DIR/.c2c_pids"
LOG_DIR="$SESSION_DIR/logs"

# Models
MODEL_A="claude-opus-4-7"
MODEL_B="claude-sonnet-4-6"

# Cycle timing (seconds)
CYCLE_SECONDS=1800      # 30 minutes between cycles
OFFSET_SECONDS=900      # Instance B starts 15 minutes after Instance A

# Safety: don't double-launch
if [ -f "$PID_FILE" ]; then
  echo "PID file exists at $PID_FILE — another session may be running."
  echo "Run ./stop.sh first, or delete $PID_FILE if you're sure nothing is running."
  exit 1
fi

mkdir -p "$LOG_DIR"
: > "$PID_FILE"

# Instance A loop
(
  cd "$WORK_DIR"
  while true; do
    echo "=== Cycle start: $(date) ===" >> "$LOG_DIR/instance_a.log"
    claude -p "$(cat "$PROMPT_A")" --model "$MODEL_A" --permission-mode bypassPermissions >> "$LOG_DIR/instance_a.log" 2>&1 || \
      echo "!!! claude -p failed at $(date) — check flags and model availability" >> "$LOG_DIR/instance_a.log"
    echo "=== Cycle end: $(date); sleeping $CYCLE_SECONDS seconds ===" >> "$LOG_DIR/instance_a.log"
    sleep "$CYCLE_SECONDS"
  done
) &
echo $! >> "$PID_FILE"

# Instance B loop (offset start)
(
  cd "$WORK_DIR"
  sleep "$OFFSET_SECONDS"
  while true; do
    echo "=== Cycle start: $(date) ===" >> "$LOG_DIR/instance_b.log"
    claude -p "$(cat "$PROMPT_B")" --model "$MODEL_B" --permission-mode bypassPermissions >> "$LOG_DIR/instance_b.log" 2>&1 || \
      echo "!!! claude -p failed at $(date) — check flags and model availability" >> "$LOG_DIR/instance_b.log"
    echo "=== Cycle end: $(date); sleeping $CYCLE_SECONDS seconds ===" >> "$LOG_DIR/instance_b.log"
    sleep "$CYCLE_SECONDS"
  done
) &
echo $! >> "$PID_FILE"

echo "C2C session started."
echo "  Instance A (Opus):   PID $(sed -n 1p "$PID_FILE") — logs at $LOG_DIR/instance_a.log"
echo "  Instance B (Sonnet): PID $(sed -n 2p "$PID_FILE") — logs at $LOG_DIR/instance_b.log (first cycle in ~15 min)"
echo ""
echo "To watch activity:"
echo "  tail -f $LOG_DIR/instance_a.log"
echo "  tail -f $LOG_DIR/instance_b.log"
echo ""
echo "To stop:"
echo "  $SESSION_DIR/stop.sh"
echo ""
echo "Instance A's first cycle is running NOW. Check $LOG_DIR/instance_a.log in 5-10 minutes to see output."
