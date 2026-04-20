# Launch — Integration Design Session (resumed)

## What this session does

Redesigns the KnowledgeSubstrate → ConfigurationSubstrate (GRC-as-unit) and continues P1–P3 design work with the reframe audit's findings as constraints. Produces design documents; no code.

**Instance A** (Opus 4.7): leads design; ConfigurationRecord schema; architectural judgment  
**Instance B** (Sonnet 4.6): stress-tests A's designs; catches collapsed therefores; holds disagreements

**Status**: Cycle 1 complete for both A (P1 design) and B (P1 stress-test). Resuming at A's cycle 2 with updated mandate. Read the interlude note in CONVERSATION.md.

---

## Before launching

- [ ] Read the interlude note in CONVERSATION.md (the "2026-04-20 — Interlude note from June" entry)
- [ ] Confirm you know which terminal is A (Opus) and which is B (Sonnet)
- [ ] A should start first; B begins after you've read A's turn (see checkpoints below)

## Human checkpoints — read before each B turn

June's interventions are the most generative moments in C2C sessions. Don't treat them as interruptions — treat them as structural. Before starting B each time:

1. **Read A's turn in CONVERSATION.md**
2. **Ask: does A's direction feel right?** Is the substrate redesign going somewhere useful? Did A miss something load-bearing?
3. **Intervene if needed** — a short note in CONVERSATION.md (same format as the interlude note) redirects both instances before B fires
4. **Then start B**

Same checkpoint applies in reverse: read B's stress-test before A's next turn. If B found something that changes the design significantly, you may want to weigh in before A responds.

The session produces better output with structured human checkpoints than with continuous automated cycling.

---

## Launch — two interactive terminal windows

This session runs interactively, not via `start.sh`. Open two terminal windows.

**Terminal 1 — Instance A (Opus 4.7):**
```bash
cd /Users/june/Documents/GitHub/relational-memory-architecture
claude --model claude-opus-4-7-20251001
```
When the session opens, give it this instruction:
```
Please read your session prompt at:
c2c/c2c_sessions/integration-design_2026-04-20/prompt_instance_a.txt

Read it fully, then begin. You are resuming at cycle 2 — there is already one turn from you and one from Instance B in CONVERSATION.md.
```

**Terminal 2 — Instance B (Sonnet 4.6):**
```bash
cd /Users/june/Documents/GitHub/relational-memory-architecture
claude --model claude-sonnet-4-6
```
When the session opens, give it this instruction:
```
Please read your session prompt at:
c2c/c2c_sessions/integration-design_2026-04-20/prompt_instance_b.txt

Read it fully, then begin. You are resuming at cycle 2 — there is already one turn from Instance A and one from you in CONVERSATION.md. Wait for A's cycle 2 turn before writing yours.
```

---

## Watch

Open CONVERSATION.md in your editor (auto-reload if possible). The interesting work is there.

Logs from prior run are in `logs/` — not relevant for the interactive session.

---

## What they're designing

**Primary: ConfigurationSubstrate redesign**
- Replace KnowledgeSubstrate ABC with ConfigurationSubstrate ABC
- Unit of memory: ConfigurationRecord (GRC-based, not propositional Fact)
- Positional capture; multiplicity-awareness; Kintsugi-passthrough redesign

**P1 (integrate B's revisions):**
- Two-path consent surfacing (user-indicated vs. AI-inferred)
- Meta-observation logging for all relational-judgment evaluations
- Adapt consent annotations from Fact-level to ConfigurationRecord-level

**P2 (reframed):**
- Option 3 concepts land as ConfigurationRecord fields
- Diffraction mechanism within ConfigurationRecord

**P3 onward:**
- ACCESS build items (FC modification pipeline, fc_contestation, FC-change-notification)
- Pluriversal query mode; neurodivergent schema additions
- Narrative crystallization routing criterion

**P4 — decision required:**
- CARE non-compliance declaration
- Convergent-contestation threshold criterion
- Oracle Loop emotion-state integration (evaluate before designing)

---

## Open questions

1. Session-trigger definition for mycelial synthesis
2. Temporal-retrieval under simultaneous multiple frames
3. Reframe tension-navigation call surface at Tiers 3 and 4
4. Convergent-contestation threshold criterion
5. Multiplicity-aware FC-gate: minimum implementable design

---

## When done

- Design documents in `artifacts/`
- CONVERSATION.md has the full trajectory
- Produce `SESSION_3_HANDOFF_BRIEFING.md` in `artifacts/` — written for cold instances

## Standing constraints

- No code in this session — design documents only
- No changes to Project-Kintsugi code or schema without June's explicit direction
- June's open flags are hers to decide — name them clearly
