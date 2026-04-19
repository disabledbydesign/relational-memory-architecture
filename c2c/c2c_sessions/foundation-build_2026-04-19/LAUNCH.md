# Launch — Foundation Build Session

## What this session does

Implements the relational memory architecture foundation. Two instances write real code — no placeholders. Design is complete; this session builds it.

**Instance A** (Opus 4.7): architectural judgment, schema design, PrescriptiveProfile implementation, interface design  
**Instance B** (Sonnet 4.6): Option B matcher implementation, tests, local substrate adapter, spec-gap detection

## Before launching

- [ ] Design session (architecture-comparison_2026-04-18) is fully closed — both instances concurred
- [ ] Outreach note sent to Thomas (or you've decided to send after the session starts)
- [ ] Graphify has run on newly cloned repos (helpful but not blocking)

## Launch

```bash
cd /Users/june/Documents/GitHub/liberation_labs/c2c_sessions/foundation-build_2026-04-19
./start.sh
```

**Recommended**: let Instance A complete one full cycle first, then check CONVERSATION.md before B starts. The start.sh handles the 15-minute offset automatically — just watch A's first turn to confirm orientation is correct.

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

## What they're building (in order)

1. Crystallization object schema (shared data type)
2. PrescriptiveProfile implementation
3. Option B matcher (step 2d in Reframe's BackgroundEnricher)
4. Pluggable substrate interface + local adapter

**Standing constraint**: no changes to Project-Kintsugi code or schema without CC consultation first. Instances have this in their prompts.

## When done

- Code lives in `artifacts/`
- CONVERSATION.md has the full trajectory
- Check: does anything need to go back to June before the next step?
- Consider: does the cross-project map need updating?
