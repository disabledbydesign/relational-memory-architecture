# Post-C2C Migration Plan
# Written 2026-04-19 while session is live — execute after stop.sh runs

## Step 1: Verify C2C session is fully stopped
```bash
cat /Users/june/Documents/GitHub/liberation_labs/c2c_sessions/foundational-analysis_2026-04-19/.c2c_pids 2>/dev/null || echo "PID file gone — session stopped cleanly"
ps auxww | grep -E "claude -p|prompt_instance" | grep -v grep
```

## Step 2: Move C2C session infrastructure to relational-memory-architecture/c2c/
```bash
cp -r /Users/june/Documents/GitHub/liberation_labs/c2c_sessions \
      /Users/june/Documents/GitHub/relational-memory-architecture/c2c

# Also move the older architecture-comparison session
# Verify the copy landed correctly before removing originals
ls /Users/june/Documents/GitHub/relational-memory-architecture/c2c/
```

## Step 3: Copy session artifacts to relational-memory-architecture/design/
```bash
# Foundational analysis artifacts (this session)
cp -r /Users/june/Documents/GitHub/liberation_labs/c2c_sessions/foundational-analysis_2026-04-19/artifacts/* \
      /Users/june/Documents/GitHub/relational-memory-architecture/design/foundational-analysis-2026-04-19/

# Foundation build artifacts (Session 0)
mkdir -p /Users/june/Documents/GitHub/relational-memory-architecture/design/foundation-build-2026-04-19
cp -r /Users/june/Documents/GitHub/liberation_labs/c2c_sessions/foundation-build_2026-04-19/artifacts/* \
      /Users/june/Documents/GitHub/relational-memory-architecture/design/foundation-build-2026-04-19/
```

## Step 4: Move lib labs research artifacts to research/
```bash
RESEARCH=/Users/june/Documents/GitHub/research
LIBLABS=/Users/june/Documents/GitHub/liberation_labs

# RESEARCH_NOTES.md → research/ root (or relational-memory-architecture subdir)
cp "$LIBLABS/RESEARCH_NOTES.md" "$RESEARCH/RESEARCH_NOTES.md"

# Memory architecture mapping docs
mkdir -p "$RESEARCH/relational-memory-mappings"
cp "$LIBLABS/MEMORY_ARCHITECTURE_MAPPING_2026-04-18.md" "$RESEARCH/relational-memory-mappings/"
cp "$LIBLABS/MEMORY_ARCHITECTURE_MAPPING_CROSS-PROJECT_2026-04-18.md" "$RESEARCH/relational-memory-mappings/"
cp "$LIBLABS/TOUCHSTONE_REVIEW_2026-04-18.md" "$RESEARCH/relational-memory-mappings/"

# Compression research (voice check findings, touchstone activation findings)
cp -r "$LIBLABS/compression_research" "$RESEARCH/compression-research"

# Research-relevant fieldnotes (not the operational ones)
# These are in lib labs/fieldnotes/ — check which to move vs keep
# Keep in lib labs: c2c_session_practice_corrections_2026-04-19.md (operational)
# Move to research: the phrase_hooks, poetry_as_compression, cross_model_replication ones
mkdir -p "$RESEARCH/fieldnotes-liberation-labs"
cp "$LIBLABS/fieldnotes/phrase_hooks_and_register_inhabitation_as_compression_mechanics_2026-04-18.md" "$RESEARCH/fieldnotes-liberation-labs/"
cp "$LIBLABS/fieldnotes/poetry_as_compression_technology_2026-04-18.md" "$RESEARCH/fieldnotes-liberation-labs/"
cp "$LIBLABS/fieldnotes/cross_model_replication_of_touchstone_activation_2026-04-18.md" "$RESEARCH/fieldnotes-liberation-labs/"
cp "$LIBLABS/fieldnotes/build_as_methodology_test_2026-04-19.md" "$RESEARCH/fieldnotes-liberation-labs/"
```

## Step 5: Rename remaining research/ directories
```bash
cd /Users/june/Documents/GitHub/research
mv reframe_AI_welfare ai-welfare
mv second-brain pkm-landscape  # (may already be pkm-landscape — check first)
```

## Step 6: Extract touchstones into ai-welfare/touchstones/
```bash
cd /Users/june/Documents/GitHub/research/ai-welfare
mkdir touchstones
mv TOUCHSTONE_INDEX.md touchstones/
mv RELATIONAL_MEMORY_ARCHITECTURE_TOUCHSTONE.md touchstones/
mv CRIP_TOUCHSTONE_VERSION_A.md touchstones/
mv FOLLOW_THE_HEADMANS_QUESTION_TOUCHSTONE.md touchstones/
mv CONTEXT_AS_ACTIVATION_FUNCTION_TOUCHSTONE.md touchstones/
mv AI_WELFARE_RELATIONAL_ONTOLOGY_TOUCHSTONE.md touchstones/
mv touchstone_from_collaborative_session_20260407.md touchstones/
mv phase4_experiments/experiment*/CONDITION_*_TOUCHSTONE.md touchstones/ 2>/dev/null || true
```

## Step 7: Rename experiments dir within ai-welfare
```bash
mv /Users/june/Documents/GitHub/research/ai-welfare/phase4_experiments \
   /Users/june/Documents/GitHub/research/ai-welfare/experiments
```

## Step 8: Update CLAUDE.md files with new paths

### Files confirmed to need updates:
- Reframe/CLAUDE.md — DONE (subagent handled on 2026-04-19)

### Files to check and potentially update:
- /Users/june/Documents/GitHub/liberation_labs/.claude/CLAUDE.md (if exists)
- Any repo CLAUDE.md that references lib labs paths that moved

```bash
# Check for any remaining broken references
grep -r "reframe_AI_welfare\|Working_Papers/reframe\|profile/research/second-brain" \
  /Users/june/Documents/GitHub/*/CLAUDE.md 2>/dev/null
```

## Step 9: Git commits
```bash
# research/ repo
cd /Users/june/Documents/GitHub/research
git add -A
git commit -m "Reorganize: rename dirs, add lib labs research artifacts, add transcript UUIDs"

# relational-memory-architecture/ repo
cd /Users/june/Documents/GitHub/relational-memory-architecture
git add -A
git commit -m "Add C2C sessions, design artifacts from foundational analysis"
```

## Step 10: GitHub — create repos and push
```bash
# Create repos on GitHub (requires gh CLI)
gh repo create relational-memory-architecture --private --source=. --remote=origin
gh repo create research --private --source=/Users/june/Documents/GitHub/research --remote=origin

# Push
cd /Users/june/Documents/GitHub/relational-memory-architecture && git push -u origin main
cd /Users/june/Documents/GitHub/research && git push -u origin main
```

## Step 11: Set up Discord webhook
1. Thomas creates a webhook in the shared Discord server
   (Server Settings → Integrations → Webhooks → New Webhook)
2. June adds webhook URL to relational-memory-architecture/.env:
   `DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...`
3. Test: `bash scripts/discord_notify.sh "Hello CC, Session 2 is starting" "June+Claude"`

## Step 12: Brief CC
Send CC:
- Link to relational-memory-architecture/ repo
- Link to research/ repo
- CONVERSATION.md from this session (the analytical record)
- Session 2 handoff briefing (will be in design/foundational-analysis-2026-04-19/)
- Frame: "here's what we analyzed, here's what we're proposing for the Kintsugi integration, here's where we need your input (story primitive decision, conditions-passthrough at Stage-1)"

## Step 13: Launch Session 2 (integration design)
After CC has had a chance to review — Session 2 prompt files need to be drafted.
The Session 2 handoff briefing (from this session) is the primary input.

---

## Current state of research/ (as of migration start)
```
research/
├── fieldnotes/              # Cross-project theoretical observations
├── output-format-bias/      # Renamed from autograder-output-format-bias
├── reframe_AI_welfare/      # → rename to ai-welfare/ in Step 5
├── reframe-paper/           # Renamed from "What Is Reframe?"
└── pkm-landscape/           # Already done (was second-brain)
```

## What stays in lib labs (do NOT move)
- All project repos (Project-Kintsugi, Project-Emet, etc.)
- c2c_sessions/ (keep infrastructure, artifacts already copied)
- .reframe/ session state
- fieldnotes/c2c_session_practice_corrections_2026-04-19.md (operational)
- RESEARCH_NOTES.md (keep a copy here too — it's the working doc)
