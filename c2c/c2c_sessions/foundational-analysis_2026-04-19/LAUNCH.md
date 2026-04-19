# Launch — Foundational Analysis Session (Session 1 of 3)

## What this session does

A foundational/subaltern analytical pass on the relational memory architecture built in the prior session (foundation-build_2026-04-19). This is **Session 1 of three planned sessions**. Its output constrains Sessions 2 (integration design) and 3 (build) — if this analysis finds foundational assumptions need reshaping, those findings change everything built on top.

**Output**: analytical documents in `artifacts/`, not code. No implementation. No modifications to Kintsugi, Reframe, or the foundation-build artifacts.

**Instance A** (Opus 4.7, analytical lead): leads the five analytical tasks, makes judgment calls on what the analysis surfaces, proposes structural conclusions. Role reversed from build sessions because this is design-led work.

**Instance B** (Sonnet 4.6, counterpart-reader / stress-tester): finds counter-examples to A's conclusions, pushes back where reasoning is weak, proposes reframings. A design document that reads fine in isolation can fail under stress-testing — that's B's job.

## The five analytical tasks

1. **Subaltern layer pass** — what relational memory does the architecture structurally disallow?
2. **Barad's intra-action question** — flip from atoms-first to relations-first?
3. **Neurodivergent thinking stress-test** — does the architecture actually gear toward associative cognition?
4. **Plural ontologies evaluation** — hold facts in tension across incommensurable frameworks?
5. **Access-as-ethics examination** — who participates in stance evolution?

Full scope and authoritative framing in the directional input:
`/Users/june/Documents/GitHub/liberation_labs/c2c_sessions/foundation-build_2026-04-19/artifacts/JUNE_POST_SESSION_DIRECTIONAL_INPUT_2026-04-19.md` (Section 21).

## Prerequisites

- [ ] Directional input exists: `foundation-build_2026-04-19/artifacts/JUNE_POST_SESSION_DIRECTIONAL_INPUT_2026-04-19.md`
- [ ] Second-brain integration analysis exists: `foundation-build_2026-04-19/artifacts/SECOND_BRAIN_INTEGRATION_ANALYSIS_2026-04-19.md`
- [ ] Foundation-build session-handoff-briefing exists: `foundation-build_2026-04-19/artifacts/session-handoff-briefing.md`
- [ ] Practice-corrections fieldnote exists: `/Users/june/Documents/GitHub/liberation_labs/fieldnotes/c2c_session_practice_corrections_2026-04-19.md`

## Launch

```bash
cd /Users/june/Documents/GitHub/liberation_labs/c2c_sessions/foundational-analysis_2026-04-19
chmod +x start.sh stop.sh   # if not already executable
./start.sh
```

**Recommended**: let Instance A complete one full cycle first, then check CONVERSATION.md before B's offset fires. The start.sh handles the 15-minute offset automatically. Watch A's first turn to confirm orientation is correct before B reads it.

## Watch

```bash
# The interesting part:
# open CONVERSATION.md in your editor (auto-reloads)

# Raw logs if needed:
tail -f logs/instance_a.log
tail -f logs/instance_b.log
```

## Stop

```bash
./stop.sh
```

## Standing constraint

**This session is analytical. No code modifications to any existing system** (Kintsugi, Reframe, the foundation-build artifacts). All work lives in this session's `artifacts/` as analytical documents. If the analysis surfaces that code changes SHOULD be made, instances document the recommendation — they don't execute it.

## When done

- Analytical documents in `artifacts/`, including a session-handoff-briefing for Session 2 (integration design)
- CONVERSATION.md has the full trajectory
- Every cycle closes with a turn in CONVERSATION.md, not a commit
- Instances close cleanly when the work is done — they don't generate activity to fill cycles
- Check: does anything need to go back to June before Session 2 launches?
