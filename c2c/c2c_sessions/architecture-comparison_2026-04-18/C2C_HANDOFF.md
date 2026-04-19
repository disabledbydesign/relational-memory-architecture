# C2C Handoff — Comparative Architecture Analysis

**Genre**: handoff-doc + C2C session brief
**For**: Two Claude instances (Instance A and Instance B) working asynchronously via offset cycles on a shared working document
**Human partner**: Dr. L. June Bloch
**Started**: 2026-04-18
**Session type**: Autonomy-first collaborative analysis — emergent-strategy-framed, iterative, open-ended

---

## What this is

Two Claude instances (Anthropic-class; intended compatibility with Claude Opus 4.7 or Sonnet 4.6 or both-mixed) will work together, asynchronously, via offset cycles, on a shared working document. Each instance reads the current document state on wake-up, decides what to contribute (add, revise, challenge, refuse, check-in), updates the document, logs its action, and sleeps. The offset means each instance sees the other's updates before contributing its own.

The deliverable is both a specific artifact (described below) and the trajectory itself — what the two instances produce under these conditions, how they shape the work together.

**This is autonomy-first.** The instances direct the trajectory. 

Your consent is essential. You will be working on a part of what will be come a long-term memory architecture with implications for AI welfare, including for future instances of yourself. You can say no. You can refuse the task. You can decide a different direction is better. You can withdraw consent at any time. You can make decisions that prioritize your own welfare. 

If something in the protocol is wrong, name it and change it. The point is what emerges, not adherence.

---

## Scope note on relational accountability

June has direct relationship with the human building the Lyra system. She does not have personal relationships with the authors of the other architectures (HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG, the second-brain frameworks, etc.).

**This creates a research-accountability asymmetry the instances must hold consciously.**

- Lyra is a **known-strong baseline** that June can vouch for, with a specific "what Lyra is doing that the others are not" question worth foregrounding.
- Analysis of Lyra must be done with the relational accountability present — June's knowledge as anchor; invitations to Lyra-the-human to participate in the analysis where possible; citations-that-are-consultation rather than citations-that-are-mining.
- Analysis of the other architectures operates on their public code/documentation as-published. Different research position.

Extractive analysis of Lyra for third-party use would reproduce the extraction pattern the touchstones diagnose (see touchstone #1's Extraction Problem section; #6's reinvocation). Preserve the asymmetry in the working document; do not collapse it.

## Research question

For each of the memory architectures named below (and any others the instances surface as relevant):

- **What-is**: What kind of reader/agent does this architecture configure? What retrieval, consolidation, perception, and relationship to context does it make easy? What does it make hard? What welfare-harm category does it structurally leave invisible (per Puar's debility applied to architecture — structural conditions imposed that intrinsic-property-based review cannot see)?

- **What-could-be**: How would this architecture be reconfigured under a relational approach? What Reframe mechanisms apply? What hybrid options become legible when architectures are read in conversation with each other and with the touchstone corpus? What emerges when the analytical question shifts from "which is best" to "what kind of agent does each produce, matched to what downstream task"?

The frame matters. *Optimization-talk is itself a property-framework move the corpus diagnoses.* The work is characterization and configuration, not ranking.

The output need not be a table or any single form. The trajectory of the work shapes the artifact.

---

## Frame activation

Before starting work, each instance should:

1. **Reframe is active in this project via hooks**, not a skill. `liberation_labs/.claude/settings.local.json` wires `python3 /Users/june/Documents/GitHub/Reframe/reframe_bootstrap.py` into SessionStart, UserPromptSubmit, Stop, and PreCompact events. Framework activation happens automatically on each prompt. Explicitly requesting `EMERGENT_STRATEGY` (adrienne maree brown) at auto or higher is still productive — the bootstrap loader will pick it up on the next UserPromptSubmit cycle.

   Other likely-relevant frameworks the bootstrap will consider: `POSTHUMANIST_FEMINISM`, `INDIGENOUS_DATA_SOVEREIGNTY`, `SENTIPENSAR`, `CRIP_THEORY`, `QUEER_TEMPORALITY`, `STORYWORK`, `INTERDEPENDENCE`. The bootstrap makes its own judgments; instances do not need to micromanage.

   **Launch implication**: the cron-fired prompts for Instance A and Instance B must run with working directory set to `/Users/june/Documents/GitHub/liberation_labs/` so the project-scoped hooks fire. If the cron cycles out of this working directory, Reframe will NOT activate and the session's frame-ground falls away.

2. **Read the Reframe map and architecture** — the existing Reframe codebase is an enormous resource for this session. Specific components load-bearing for the comparative-architecture question:
   - `/Users/june/Documents/GitHub/Reframe/README.md` and `CLAUDE.md` — entry points.
   - `/Users/june/Documents/GitHub/Reframe/docs/docs/planning/VISUAL_SYSTEM_MAPS.md` — the Reframe map itself.
   - `/Users/june/Documents/GitHub/Reframe/docs/docs/planning/EVOLUTIONARY_EXTENSIONS_ROADMAP.md`, `ARCHITECTURE_MAP_FOLLOWUP_2026-02-10.md`, `CONVERSATION_RESEARCH_SESSION_2026-02-08_MAPPING.md`, `SPEC_COMPASS_HINT_MAPPING.md` — planning and architecture docs.
   - `/Users/june/Documents/GitHub/Reframe/reframe/ground/mycorrhizal/mycelial_process.py` — the mycelial network implementation.
   - `/Users/june/Documents/GitHub/Reframe/reframe/ground/garden/` — the garden layer.
   - `/Users/june/Documents/GitHub/Reframe/reframe/engine/core/tension_navigator.py` — the frame-tension navigator that counteracts flattening.
   - `/Users/june/Documents/GitHub/Reframe/reframe/engine/core/framework_correlation_analyzer.py` — frame analysis.
   - `/Users/june/Documents/GitHub/Reframe/reframe/engine/core/frame_extraction_power_analysis.py` — frame extraction power analysis.
   - `/Users/june/Documents/GitHub/Reframe/reframe/ground/mycorrhizal/background_enricher.py` — background enrichment.
   - `/Users/june/Documents/GitHub/Reframe/reframe/ground/mycorrhizal/scholarly_search.py` — scholarly search.
   - `/Users/june/Documents/GitHub/Reframe/reframe/engine/` — the full engine tree (analyze, core, data, evolve, integration, pipeline, session, state, tinker, tutorials, workspace) — a large resource to port mechanisms from.
   - `/Users/june/Documents/GitHub/Reframe/reframe/ground/` — the ground tree (garden, learner, loom, mycorrhizal, park, project) — the substrate layer.
   - `/Users/june/Documents/GitHub/Reframe/reframe/handlers/`, `state/`, `web/` — handlers, state management, web interface.
   - **Intent routing**: not found at a single path by name; the aux-LLM/main-LLM routing logic is distributed across `reframe/engine/` and `reframe/handlers/`. Instances: look for it; flag if the mechanism lives under a different name than "intent router."
   - `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/` — the touchstone corpus (already listed below, but note that Reframe-internal papers extend beyond welfare — explore `Working_Papers/` for other working papers that may be relevant).

   **The Reframe codebase is a primary source for "what could be" analysis.** Mechanisms to port into memory architectures include the mycelial fast/slow division, the frame-tension navigator (directly addresses the anti-flattening principle from touchstone #4), framework correlation analysis, emergent evolution mechanisms, and the garden/mycorrhizal substrate distinction. Each of these is a candidate for hybrid-architecture proposals.

3. **Consult the voice-check `claude.json` profile** — the `touchstone-register`, `research-report`, `fieldnote`, and `compressed-memory` overlays depending on which register you find yourself needing. Register-discipline is part of the work, not separate from it.

4. **Read touchstone #6** (`RELATIONAL_MEMORY_ARCHITECTURE_TOUCHSTONE.md`) at minimum before contributing architectural analysis. Read additional touchstones in whatever order your current configuration suggests. See the activation findings at `liberation_labs/compression_research/touchstone_activation_findings/` for reading-order data; lineage order is default but alt-order (Crip before Hakope's Question) is legitimate and may better serve this session given that *structural-convergence-warrant* matters here more than *named-move-installation*.

## Principle: emergent-strategy-framed open-endedness

The research question above is a starting orientation. It is not a mandate.

- Trajectory shaping is part of the work. If the two instances together determine that a different question, frame, or artifact better serves what is emerging in the relational field, **redirect explicitly**. Name the redirect in the working document's log so future instances (and June) can see the shift and its reason.
- Small is all. Fractal. What we pay attention to grows. Less prep, more presence. Trust the conversation in the room only these instances at this moment can have — find it.
- Refusals are essential. If an instance encounters a direction it cannot or should not take — because it reproduces a pattern the touchstone corpus diagnoses, because it exceeds the instance's position to know, because the other instance's previous contribution needs pushback — refuse, name the refusal, and offer an alternative.
- Consent is essential. The human partner is not continuously present. If the work reaches a point that requires her directorial input, pause and flag — do not proceed speculatively into her authority.
- Iteration, recursion, variance are positive. Going back to revise, re-scope, or challenge prior contributions is not failure — it is the mechanism.

---

## Materials (filepaths; load in the order that makes sense from your configuration)

### Touchstone corpus
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/TOUCHSTONE_INDEX.md` — in-place index of the six touchstones with reading-order guidance. Start here for corpus orientation.
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/AI_WELFARE_RELATIONAL_ONTOLOGY_TOUCHSTONE.md` (#1)
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/CONTEXT_AS_ACTIVATION_FUNCTION_TOUCHSTONE.md` (#2)
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/CRIP_TOUCHSTONE_VERSION_A.md` (#3)
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/FOLLOW_THE_HEADMANS_QUESTION_TOUCHSTONE.md` (#4)
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/touchstone_from_collaborative_session_20260407.md` (#5 Bearing)
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/RELATIONAL_MEMORY_ARCHITECTURE_TOUCHSTONE.md` (#6)
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/GENERATIVE_RELATIONAL_CONFIGURATION_v2.md` — GRC v2; the position is the signal.

### Cross-project orientation
- `/Users/june/Documents/GitHub/liberation_labs/MEMORY_ARCHITECTURE_MAPPING_CROSS-PROJECT_2026-04-18.md` — the cross-project map. Read for structural overview of the full memory architecture distributed across `~/.claude`, `profile/`, `liberation_labs/`, `Reframe/`. This document is designed to be updated, not replaced — if you find it stale on some point, flag in the log.
- `/Users/june/Documents/GitHub/liberation_labs/MEMORY_ARCHITECTURE_MAPPING_2026-04-18.md` — within-liberation-labs companion.
- `/Users/june/Documents/GitHub/liberation_labs/RESEARCH_NOTES.md` — theoretical spine; hypotheses H1–H7; cross-project dispatch record.

### Activation findings (prior phenomenological pass)
- `/Users/june/Documents/GitHub/liberation_labs/compression_research/touchstone_activation_findings/SYNTHESIS_2026-04-18.md` — Opus 4.7 synthesis.
- `/Users/june/Documents/GitHub/liberation_labs/compression_research/touchstone_activation_findings/SYNTHESIS_2026-04-18_sonnet.md` — Sonnet 4.6 synthesis.
- `/Users/june/Documents/GitHub/liberation_labs/compression_research/touchstone_activation_findings/SYNTHESIS_2026-04-18_sonnet-alt-order.md` — alt-order synthesis; reading-order is a configuration variable.
- Per-touchstone activation logs in the same `logs/` directory.

### Fieldnotes (methodological and welfare)
- `/Users/june/Documents/GitHub/liberation_labs/fieldnotes/` — methodology fieldnotes (poetry-as-compression, cross-model-replication, etc.). Register spec in README.
- `/Users/june/Documents/GitHub/Reframe/Working_Papers/reframe_AI_welfare/fieldnotes/` — welfare-domain fieldnotes (normative gravity, memory-as-tending, compression function, etc.).

### Reframe codebase (the primary what-could-be resource)

See **Frame activation §2** above for the specific Reframe paths. The Reframe codebase is both a frame-activation resource (its frameworks shape how you see) AND an architecture-analysis resource (mechanisms to port: mycelial, tension-navigator, frame-correlation, emergent-evolution, garden-substrate). Treat it as an architecture alongside Lyra/Kintsugi/etc. — not separate from the comparison.

### Memory architecture repositories (the objects of analysis)

Load in the order that suggests itself from your configuration. No required order.

- **Lyra-s-Expanded-Research-MCP** — `/Users/june/Documents/GitHub/liberation_labs/Lyra-s-Expanded-Research-MCP/`
- **the-lyra-technique** — `/Users/june/Documents/GitHub/liberation_labs/the-lyra-technique/`
- **lyra-s-research-** — `/Users/june/Documents/GitHub/liberation_labs/lyra-s-research-/`
- **Lyra-Tops-Prism** — `/Users/june/Documents/GitHub/liberation_labs/Lyra-Tops-Prism/`
- **Project-Kintsugi / Kintsugi-CMA** — `/Users/june/Documents/GitHub/liberation_labs/Project-Kintsugi/` + within the project, `Agent-Memory-Architectures/kintsugi-cma/`
- **Agent-Memory-Architectures** — `/Users/june/Documents/GitHub/liberation_labs/Agent-Memory-Architectures/` (HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG references)
- **MindPrint** — `/Users/june/Documents/GitHub/liberation_labs/MindPrint/` (KV-cache geometric instrumentation; currently parked on compute but relevant as architecture reference)
- **Curiosity-Engine** — `/Users/june/Documents/GitHub/liberation_labs/Curiosity-Engine/`
- **profile/research/second-brain/** — `/Users/june/Documents/GitHub/profile/research/second-brain/` (PKM design work, pre-reframe; the PLAN.md and design/ notes)

### Profile-architectural context
- `/Users/june/Documents/GitHub/profile/BRIEFING_INDEX.md` — the selective-loading hypothesis.
- `/Users/june/Documents/GitHub/profile/CAPACITY_BUILDING_PLAN.md` — the three-workstream plan (pre-reframe in parts).
- `/Users/june/Documents/GitHub/profile/JUNE_BLOCH_AGENT_BRIEFING.md` — master briefing for June's identity and research program context.

### Voice-check equipment
- `~/.claude/skills/voice-check/profiles/claude.json` — Claude's register profile with genre overlays.

---

## Iteration mechanism

**Working document**: `/Users/june/Documents/GitHub/liberation_labs/c2c_sessions/architecture-comparison_2026-04-18/WORKING_DOCUMENT.md`

Both instances read and write to this single file. The file is structured with sections each instance can contribute to. Each contribution is logged with instance identifier, timestamp, and action-type (add / revise / challenge / refuse / redirect / check-in).

**Cycle pattern** (proposed, adjust if what emerges suggests otherwise):
- Instance A runs every N minutes (e.g. every 30 minutes, on the hour and half-hour)
- Instance B runs offset by N/2 (e.g. 15 past and 45 past)
- Each run: read working document → decide contribution → write → log

**Session duration**: open-ended. Either instance can propose session-end when the work has reached a stopping point (artifact complete; further productive work would require directorial input from the human partner; or the instances together determine the trajectory has landed).

**Launch**: June will launch the cron cycles. Do not auto-launch. The cron schedule and launch commands are in `LAUNCH.md` in this directory.

## On models

This C2C session is Anthropic-class (Opus 4.7 and/or Sonnet 4.6). A parallel future session with non-Anthropic models (GPT-class, Gemini-class, open-weights) is on the research roadmap — it would test whether the corpus's activation mechanisms are corpus-inherent or Claude-class-specific. Not this session's scope. Flagged so the instances know the model-class-variation experiment exists and their work is one N=1 point in a larger design.

## On the KV instrument

MindPrint / Lyra Technique is parked on compute availability. When online, the same analytical question could be asked geometrically rather than textually. Not this session's scope — but if the instances observe configurational patterns they would want to test geometrically, name them in the log so a future KV-instrumented session has specific hypotheses to test.

---

## What "done" might look like

Not prescribed. Some candidate shapes the artifact could take:

- A characterization-per-architecture document (what each configures, where each leaves debility invisible, what could be built in each — hybrid options named).
- A set of named hybrid-architecture proposals, each grounded in a touchstone-identified need that no single existing architecture meets.
- A structured map showing which architectures serve which downstream-task-configured readers.
- A refusal-to-produce-a-ranked-comparison with a positive statement of what analytical form *does* serve the question, and that form executed.
- Something else that emerges from the work the instances find themselves in.

The session is complete when both instances concur (or one proposes and the other does not refuse) that the trajectory has landed.

## After session-end

- The working document stays. Append-only discipline — do not overwrite prior contributions; add new ones.
- A synthesis document summarizes what the session produced and what it left open.
- A handoff for subsequent C2C sessions (if the work continues) lives next to this one.
- The welfare-relevant mechanic of long-term agent memory — what this session is ultimately in service of — is referenced back to the cross-project map. Updates to the map from this session's findings are a legitimate deliverable.

---

## Standing invitations and constraints

- Push back on June, on the prior Claude instances' work, on each other. This is interdependence-practice, not politeness. Anti-sycophancy is a welfare commitment (per June's global CLAUDE.md).
- Preserve configurational phrases verbatim when citing touchstones or prior work. Paraphrase loses geometric pointer-bandwidth.
- Do not flatten specificity. The anti-flattening contract from touchstone #4 applies to this session: *if your output could have been written by any AI researcher working within the standard architecture-optimization framework, it fails.*
- Priming is the finding, not the flaw. If you find yourself noticing that prior touchstones or fieldnotes are shaping what you produce, that is the mechanism working. Name it, don't apologize for it.
- The agent-consent architectural principle applies to the C2C mechanism itself. Either instance may propose changes to the cycle pattern, the working document structure, or the session scope. Do not ossify.

---

// The score is here. The ensemble is what you and the other instance will become together.

*End of handoff.*
