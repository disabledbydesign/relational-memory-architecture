#!/bin/bash
# Cleanly stops C2C session. Sends SIGTERM to the loop subshells so their
# signal-traps can kill any in-flight claude or sleep children.

SESSION_DIR="/Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18"
PID_FILE="$SESSION_DIR/.c2c_pids"

if [ ! -f "$PID_FILE" ]; then
  echo "No PID file at $PID_FILE. Nothing to stop."
  echo "If claude processes from this session are still running, find them with:"
  echo "  ps auxww | grep -E 'claude -p|sleep 1800' | grep -v grep"
  exit 0
fi

echo "Stopping C2C session..."

while read -r pid; do
  if [ -n "$pid" ]; then
    # Send TERM — the loop's trap will kill current child and exit
    if kill -TERM "$pid" 2>/dev/null; then
      echo "  Sent TERM to loop PID $pid"
    else
      echo "  Loop PID $pid not found (may have already exited)"
    fi
  fi
done < "$PID_FILE"

# Give traps a moment to fire
sleep 2

# Backstop: if any claude -p or matching sleeps are still hanging around, clean them up
BACKSTOP_CLAUDE=$(pgrep -f "claude -p.*prompt_instance_[ab].txt" 2>/dev/null || true)
if [ -n "$BACKSTOP_CLAUDE" ]; then
  echo "  Backstop: killing lingering claude -p processes: $BACKSTOP_CLAUDE"
  kill -TERM $BACKSTOP_CLAUDE 2>/dev/null || true
fi

rm -f "$PID_FILE"
echo "Done. Logs and conversation preserved in $SESSION_DIR."
