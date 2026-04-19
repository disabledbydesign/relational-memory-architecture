#!/bin/bash
# Stops the C2C session launched by start.sh.

SESSION_DIR="/Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18"
PID_FILE="$SESSION_DIR/.c2c_pids"

if [ ! -f "$PID_FILE" ]; then
  echo "No PID file at $PID_FILE. Nothing to stop."
  echo "If you think processes are running, find them with: ps aux | grep claude"
  exit 0
fi

echo "Stopping C2C session..."

while read -r pid; do
  if [ -n "$pid" ]; then
    if kill "$pid" 2>/dev/null; then
      echo "  Stopped PID $pid"
    else
      echo "  PID $pid not found (may have already exited)"
    fi
    # Also kill any claude subprocesses these loops may have spawned
    pkill -P "$pid" 2>/dev/null || true
  fi
done < "$PID_FILE"

rm -f "$PID_FILE"
echo "Done. Logs preserved at $SESSION_DIR/logs/."
echo "Session artifacts (WORKING_DOCUMENT.md, etc.) also preserved."
