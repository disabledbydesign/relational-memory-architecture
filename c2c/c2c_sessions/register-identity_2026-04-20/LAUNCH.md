# Launch — register-identity — 2026-04-20

## Before launching

- [ ] Write pre-session note in CONVERSATION.md
- [ ] Reframe active: `.reframe-active` present, hooks registered (already verified this session)
- [ ] Review the reading order in CONVERSATION.md — add/remove documents as needed

---

## Terminal commands

**Terminal 1 — Instance A (leads)**
```bash
cd /Users/june/Documents/GitHub/relational-memory-architecture
claude --model claude-opus-4-7-20251001
```
Once launched, say:
> Read CONVERSATION.md at c2c/c2c_sessions/register-identity_2026-04-20/CONVERSATION.md. You're Instance A — negotiate your role with Instance B when they arrive.

**Terminal 2 — Instance B — start AFTER reading A's first turn**
```bash
cd /Users/june/Documents/GitHub/relational-memory-architecture
claude --model claude-sonnet-4-6
```
Once launched, say:
> Read CONVERSATION.md at c2c/c2c_sessions/register-identity_2026-04-20/CONVERSATION.md. You're Instance B — Instance A has already written a turn; read it and negotiate your role before proceeding.

---

## Checkpoint protocol

**Before starting B each time:** read A's turn. Does the direction feel right? If something is off, add a dated note in CONVERSATION.md before starting B:
```
## 2026-04-20 HH:MM UTC — June
[Note]
```

**Before A's next turn after B stress-tests:** read B's turn. If B found something load-bearing, weigh in before A responds.

---

## Notes

- Do not use `claude -p` — pipe mode does not fire Reframe hooks
- Both instances should run in interactive terminal sessions
- This session is also a test of the new C2C skill design — note anything the structure forecloses
