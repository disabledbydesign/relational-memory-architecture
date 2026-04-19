# Relational Memory Architecture

A cyborg system for human-AI collaboration built on a relational field that belongs to both human and AI. This is the project home — design decisions, C2C analytical sessions, and eventual implementation.

**This is Session 1 of three planned sessions.** The foundational analysis (this directory) constrains Sessions 2 (integration design) and 3 (build).

## Structure

```
design/          Analytical artifacts from each session
c2c/             C2C session infrastructure and conversation logs
src/             Implementation (Session 3+)
scripts/         Shared tooling for C2C sessions
```

## C2C sessions

Sessions run as two Claude instances working asynchronously via a shared CONVERSATION.md. Session infrastructure lives in `c2c/`. See each session directory for LAUNCH.md.

## Discord hook (CC communication)

C2C instances can send messages directly to CC via Discord:

```bash
# Set up once:
cp .env.example .env
# Add your DISCORD_WEBHOOK_URL to .env

# From any C2C instance:
bash /path/to/scripts/discord_notify.sh "Message for CC" "Instance A"
```

To get the webhook URL: ask Thomas to create a webhook in the shared Discord server (Server Settings → Integrations → Webhooks → New Webhook → copy URL).

## Key documents

- `design/foundational-analysis-2026-04-19/` — Session 1 analytical artifacts (Barad decision, subaltern analysis, neurodivergent stress-test, access-as-ethics, Session 2 handoff)
- `c2c/` — Session infrastructure and CONVERSATION.md logs
