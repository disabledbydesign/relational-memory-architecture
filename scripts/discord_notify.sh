#!/bin/bash
# Send a message to the CC/relational-memory Discord channel.
# Usage: ./discord_notify.sh "Your message here" ["Sender name"]
# Requires: DISCORD_WEBHOOK_URL set in environment or .env at repo root

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if present
if [ -f "$ROOT_DIR/.env" ]; then
    set -a; source "$ROOT_DIR/.env"; set +a
fi

MESSAGE="$1"
SENDER="${2:-C2C Instance}"

if [ -z "$MESSAGE" ]; then
    echo "Usage: discord_notify.sh \"message\" [\"sender name\"]" >&2
    exit 1
fi

if [ -z "$DISCORD_WEBHOOK_URL" ]; then
    echo "Error: DISCORD_WEBHOOK_URL not set. Add it to $ROOT_DIR/.env" >&2
    exit 1
fi

# Escape quotes in message for JSON
ESCAPED=$(echo "$MESSAGE" | sed 's/"/\\"/g')

PAYLOAD="{\"username\": \"${SENDER}\", \"content\": \"${ESCAPED}\"}"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$DISCORD_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

if [ "$HTTP_STATUS" = "204" ]; then
    echo "Message sent to Discord."
else
    echo "Discord webhook returned HTTP $HTTP_STATUS" >&2
    exit 1
fi
