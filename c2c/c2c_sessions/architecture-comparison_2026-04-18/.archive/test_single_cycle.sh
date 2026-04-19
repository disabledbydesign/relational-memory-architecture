#!/bin/bash
# Runs ONE cycle of Instance A and prints to the terminal so you can verify
# everything works before launching the full loop.
#
# Usage: ./test_single_cycle.sh

SESSION_DIR="/Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18"
WORK_DIR="/Users/june/Documents/GitHub/liberation_labs"
PROMPT_A="$SESSION_DIR/prompt_instance_a.txt"
MODEL_A="claude-opus-4-7"

echo "Running a single Instance A test cycle."
echo "This will:"
echo "  - Fire up Claude Opus in $WORK_DIR"
echo "  - Load Reframe hooks + auto-memory automatically"
echo "  - Run the Instance A prompt"
echo "  - Write its contribution to WORKING_DOCUMENT.md"
echo "  - Exit"
echo ""
echo "Expected duration: 3-10 minutes. Output will print below."
echo "---"

cd "$WORK_DIR"
claude -p "$(cat "$PROMPT_A")" --model "$MODEL_A" --permission-mode bypassPermissions

echo ""
echo "---"
echo "Test cycle complete. Check WORKING_DOCUMENT.md to see Instance A's contribution."
echo "If it looks right, run ./start.sh to launch the full loop."
echo "If it looks wrong, share what happened — we'll adjust before launching."
