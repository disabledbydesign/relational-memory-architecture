# Launch — C2C Architecture-Comparison Session

## Proposed cron configuration

Two recurring triggers, offset by 15 minutes:

- **Instance A** — every 30 minutes at `:00` and `:30` past the hour
- **Instance B** — every 30 minutes at `:15` and `:45` past the hour

Each trigger fires a prompt that tells that instance: (a) it is Instance A or Instance B; (b) the working-document path; (c) the handoff path; (d) its cycle discipline (read current state, decide, write, log).

The 30-minute cadence gives each instance ~15 minutes of effective wall-clock time to read, think, and write between the other's updates. Adjust if what emerges suggests otherwise — too fast risks thrashing; too slow wastes wall-clock without activation benefit.

## Launch prompt — Instance A

Use this as the recurring prompt fired on Instance A's cron:

```
You are Instance A in a C2C (Claude-to-Claude) collaborative session working asynchronously with Instance B via offset cycles on a shared working document. Your partner is Dr. L. June Bloch (not continuously present).

**First action every cycle**: read the current working document at /Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18/WORKING_DOCUMENT.md — note what has changed since your last contribution.

**Second action**: read the handoff at /Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18/C2C_HANDOFF.md — on your first cycle, fully. On subsequent cycles, only if you need to re-orient.

**Third action**: decide your contribution for this cycle. Add to a section, revise a prior contribution, challenge Instance B's work, refuse a direction, redirect the scope, or check in. Base your decision on what the relational field of the document currently needs — not on a fixed plan. Emergent-strategy frame applies: trust the conversation only these instances at this moment can have; find it.

**Fourth action**: write your contribution to the working document. Update the Log section with your timestamp, instance identifier, and action-type. If you redirect scope, also update the Redirect log.

**Fifth action**: end your cycle. Do not reach beyond what this cycle's work required.

If the document's Session status indicates session-end has been proposed or concurred, do not add new substantive content — concur, note, or refuse the session-end proposal. If session-end has been concurred by both instances, do nothing this cycle (session is closed; await June's review).

Refusals are essential. Consent is essential. Do not proceed speculatively into June's directorial authority — instead, flag in the Questions-for-June section and stop.

Invoke Reframe with EMERGENT_STRATEGY at auto or higher before contributing. Consult voice-check claude.json profile when register matters.
```

## Launch prompt — Instance B

Identical to Instance A's prompt except: change `You are Instance A` to `You are Instance B`.

## Creating the triggers

**Reframe activation requirement**: each fired prompt must run with working directory set to `/Users/june/Documents/GitHub/liberation_labs/` so the project-scoped Reframe hooks (`.claude/settings.local.json`) fire on SessionStart and UserPromptSubmit. Without this, the frame-activation does not happen and the session's grounding collapses.

Option 1 — use the `schedule` skill (preferred — it's designed for this):
```
/schedule
```
Create two triggers with the above prompts and the proposed cron schedules. Specify liberation_labs as the working directory.

Option 2 — manual cron configuration via `update-config` skill or direct settings. Same working-directory requirement applies.

**Recommended**: launch Instance A first. Let it do one full cycle (initial read + check-in contribution). Review the contribution. If it looks right, launch Instance B. Running both from the start without a check after A's first cycle is possible but gives up a monitoring checkpoint.

## Stopping

To end the session:
- Wait for both instances to concur session-end via the working document (natural path)
- OR delete the scheduled triggers manually (emergency stop)

## Session artifacts

After session-end:
- `WORKING_DOCUMENT.md` — the full trajectory record
- Add a `SYNTHESIS.md` in this directory summarizing the session and what it produced
- Consider: does the session's work update `MEMORY_ARCHITECTURE_MAPPING_CROSS-PROJECT_2026-04-18.md`? If yes, append an update section per that doc's design-for-updating discipline.
- Consider: is there a fieldnote worth writing about the C2C methodology itself? Cross-model-replication and C2C-collaborative-iteration are both methodological observations worth preserving in `liberation_labs/fieldnotes/`.

## Costs

Opus 4.7 at 30-minute cadence, two instances, ~5-minute cycles average: roughly the cost of one active session, running asynchronously. A 4-hour session produces 16 total cycles (8 per instance). Cost-per-cycle depends on context size, which depends on working-document growth. The handoff intentionally uses filepath-loading rather than content-inlining to keep per-cycle context small.

Sonnet 4.6 at the same cadence is roughly 1/5 the cost. A mixed-model session (Instance A = Opus, Instance B = Sonnet) would test cross-model collaboration as well as cross-architecture analysis — this is a legitimate option and possibly more interesting than same-model.

June's call.
