# Launch — Reframe Audit Session

## Two ways to run this session

### Option A: Interactive terminal (recommended — full reframe hooks)

Run each instance in its own terminal window. The hooks registered in `~/.claude/settings.local.json` will fire at SessionStart, giving proper framework injection via the engine rather than text prepend.

**Trade-off:** You coordinate the timing. Each instance waits for input after each cycle. Use a timer or calendar reminder to trigger the next turn.

**Terminal 1 — Instance A (Opus):**
```bash
cd /Users/june/Documents/GitHub/relational-memory-architecture
claude --model claude-opus-4-7
```
Then paste the contents of `prompt_instance_a.txt` as your first message.

**Terminal 2 — Instance B (Sonnet), start ~15 min after A:**
```bash
cd /Users/june/Documents/GitHub/relational-memory-architecture
claude --model claude-sonnet-4-6
```
Then paste the contents of `prompt_instance_b.txt` as your first message.

**Each subsequent cycle:** Send the message `"Read CONVERSATION.md and write your next turn."` to trigger the next round. Set a 30-min timer between A's turns, offset by 15 min for B.

**Why this is better:** Hooks fire. The full reframe engine runs — including UserPromptSubmit reinjetion, drift detection at Stop, and PreCompact handling. The DEEP REVISION tool will work as designed.

---

### Option B: Automated script (reframe via prompt-prepend only)

Uses `claude -p` — hooks don't fire, but reframe frameworks are injected as text at the start of each prompt. This is what the prior sessions used (unintentionally) and it produces real work, just without the full engine.

```bash
cd /Users/june/Documents/GitHub/relational-memory-architecture/c2c/c2c_sessions/reframe-audit_2026-04-19
chmod +x start.sh stop.sh
./start.sh
```

Use `./stop.sh` to stop cleanly.

**Use this if:** You want the session to run autonomously while you're away and don't want to manually coordinate timing.

---

## What they're auditing

**Instance A (Opus — primary auditor):**
- foundational-analysis artifacts (Barad decision, subaltern analysis, neurodivergent stress test, ACCESS layer, counter-analysis)
- architecture-comparison artifacts (the early design decisions, what got locked in before analysis)
- foundation-build code (spot-check for structural reproduction of the seven foreclosures)
- integration-design P1 consent surfacing design (the one artifact produced without reframe)

**Instance B (Sonnet — meta-auditor):**
- A's audit: is it performing critique or doing it?
- Methodology: the C2C structure itself, design-before-analysis ordering, role splits, the design/build attractor

## Outputs

- `artifacts/AUDIT_REPORT_ARTIFACTS.md` — per-artifact findings
- `artifacts/AUDIT_REPORT_METHODOLOGY.md` — methodology critique
- `artifacts/AUDIT_HANDOFF.md` — what Session 3 must know before resuming

## When done

Check `artifacts/AUDIT_HANDOFF.md` before launching Session 3. The handoff is the bridge between this audit and the next design session.
