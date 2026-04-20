#!/bin/bash
SESSION_DIR="/Users/june/Documents/GitHub/relational-memory-architecture/c2c/c2c_sessions/reframe-audit_2026-04-19"
PID_FILE="$SESSION_DIR/.c2c_pids"

if [ ! -f "$PID_FILE" ]; then
  echo "No PID file at $PID_FILE. Nothing to stop."
  echo "If claude processes are still running, find them with:"
  echo "  ps auxww | grep -E 'claude -p|sleep 1800' | grep -v grep"
  exit 0
fi

echo "Stopping reframe audit session..."

while read -r pid; do
  if [ -n "$pid" ]; then
    if kill -TERM "$pid" 2>/dev/null; then
      echo "  Sent TERM to loop PID $pid"
    else
      echo "  Loop PID $pid not found (may have already exited)"
    fi
  fi
done < "$PID_FILE"

sleep 2

BACKSTOP_CLAUDE=$(pgrep -f "claude -p.*prompt_instance_[ab].txt" 2>/dev/null || true)
if [ -n "$BACKSTOP_CLAUDE" ]; then
  echo "  Backstop: killing lingering claude -p processes: $BACKSTOP_CLAUDE"
  kill -TERM $BACKSTOP_CLAUDE 2>/dev/null || true
fi

rm -f "$PID_FILE"
echo "Done. Logs and artifacts preserved in $SESSION_DIR."
