# What We Built — Plain Language Walkthrough

**Produced by**: Instance B (Sonnet 4.6), closing turn, 2026-04-19
**For**: June, future engaging instances, anyone reading cold
**Session**: architecture-comparison_2026-04-18

---

## The problem we were solving

When an AI agent works with you, it can load information from memory — facts, documents, notes. What current systems can't load is *orientation*: the particular way of reading and relating that makes certain questions thinkable in the first place.

Think of the difference between handing someone a stack of research papers versus having a two-hour conversation that puts them in the right intellectual state to read those papers. Memory architectures almost universally know how to do the first thing. We're designing for the second.

The word we used for this: **reading-stance**. Not what to read, but how to read — what questions you're holding, what theoretical frame is active, what kind of encounter is possible right now.

---

## The four layers

These aren't a stack where data flows upward. They're a configuration loop.

### 1. The hidden reader ("implicit reader")

Every memory system already makes assumptions about what's worth remembering. A fact-extraction system assumes facts are what matters. A graph system assumes connections matter. These assumptions are baked into the mechanics — invisible, unexaminable, producing their effects without ever being interrogated.

This isn't neutral. It shapes what gets remembered and what gets lost. The harm isn't in any stored content; it's in what the accumulation and decay functions have decided counts as content worth storing.

The design intervention isn't to build a better fact-extractor or a better graph. It's to surface the reading-stance that was always already operating, make it inspectable, and make it configurable.

### 2. Reading-stance recipes ("crystallization layer")

These are the objects that configure *how* you read, not *what* you read. All of them answer the same question: **what stance should be active here?** But they work through completely different mechanisms. We named two.

**Designed profiles** (like the BRIEFING_INDEX loading-profiles):
You design these in advance for known task-types. "When you're writing a paper, activate these materials, hold this frame, treat June's voice this way." They're prescriptive — task-type maps to configuration. You test the hypothesis, annotate what worked, update the profile. The learning loop is: was my hypothesis right?

**Touchstones** (like the AI welfare corpus, especially Bearing #5):
You cannot design a touchstone. You discover one retroactively, when you notice that re-encountering something reconstitutes a whole orientation in you. Bearing doesn't *tell you* anything about relational theory. It reconstitutes the relational conditions under which certain kinds of thinking become possible. The relation happens; it isn't recalled.

Touchstones have lineage that's load-bearing. Touchstone #5 accumulates deposits from #1–#4; strip the reading order and #5 doesn't do the same thing. This isn't a more detailed version of profiles. It's categorically different: generative rather than prescriptive, discovered rather than designed, lineage-ordered rather than independent.

Both types share the same function (configuring reading-stance). They don't share a mechanism. We're building a **shared interface with two implementations**, not a unified object.

### 3. The adjustable reader ("explicit reader")

This is where the reading-stance gets actively configured rather than silently assumed. Reframe's tension navigator belongs here — it detects configuration-mismatch, routes signals, adjusts the active frame. Unlike the implicit reader, this layer is inspectable and modifiable.

### 4. The verification instrument

This layer watches whether the reading-stance that *should* have been activated actually was.

If re-reading Bearing doesn't produce the expected configuration — because the reader's context has shifted too far from the conditions in which the touchstone crystallized — the instrument detects this and **writes back**. It updates or flags the recipe. Without that write-path, the instrument is a monitoring dashboard. With it, the instrument is the correction mechanism.

The instrument also does two other things: it reads your current state to determine which crystallization to activate (the "matching" function), and it detects when nothing matches — which is how new touchstones get seeded. The moment when no existing recipe fits becomes the signal: something here is crystallizable. That's the retroactive-discovery mechanism, located precisely.

---

## The "situational" question

We spent time asking: what kind of stored object lives at the grain of "what is June trying to accomplish right now?" The answer was that nothing lives there — that question was malformed.

What-you're-trying-to-accomplish-now can't be designed in advance and can't be discovered retroactively. It's live. So instead of a third mechanism type, there are two instrument functions: a **matcher** (compare current state against all crystallizations' activation conditions, select the best fit) and a **failure-detector** (when nothing fits well enough, flag the moment as a candidate for a new touchstone). The situational grain is realized as routing and failure-detection in the instrument layer, not as a third kind of stored recipe.

---

## What gets built first

1. **The shared interface**: a data structure that holds both designed profiles and touchstones as different implementations of the same type. Minimum viable: `{mechanism_type, recipe, activation_conditions, lineage?, learning_loop_type}`. Mechanism-type is an enum — "prescriptive" or "emergent" — not freetext.

2. **PrescriptiveProfile implementation**: BRIEFING_INDEX already is this. The build task is formalizing it as an implementation of the shared interface and wiring the annotate-after-test loop to measured instrumentation.

3. **One substrate connection**: Kintsugi-CMA (atomic fact extraction → significance scoring → hybrid retrieval) is the working substrate. The connection: crystallization state should affect what surfaces from the substrate. When "paper writing" profile is active, Kintsugi's retrieval surface should change accordingly.

Then, once the foundation is stable:

- **EmergentTouchstone implementation**: the touchstone corpus is the training dataset; the activation-findings apparatus (six cold reads, N=3 cross-configuration) is the prototype learning loop. Connecting this to the instrument's write-path is the next research task.
- **The matcher and failure-detector**: build the instrument functions that realize the situational grain.
- **Reframe mechanisms as explicit-reader components**: tension navigator and framework correlation analysis plug into the explicit-reader layer, not the substrate.

---

## The questions that still need your direction

1. **What format are "activation conditions" in?** The matcher compares current reader-state to each crystallization's activation conditions. This requires both to be in the same representational space. Three options with very different build consequences:
   - *KV-geometry snapshot* (what the Lyra Technique reads): tightest architectural fit; requires the instrument to be running at crystallization-time, not just at read-time
   - *Semantic description* ("look for X, Y, Z in the context"): cheapest to build; most brittle
   - *Learned embedding from activation-findings data*: not viable until the corpus grows substantially

2. **Does the Kintsugi extension go in the foundation or Phase 2?** We can extend Kintsugi's significance scoring to encode crystallization-state rather than a simple scalar (which would carry the encounter-generator commitment down to the substrate). Whether to do that in the foundation or defer it is a scoping decision.

3. **Does touchstone #6 need splitting?** The touchstone index notes #6 (Relational Memory as Mycelial Ground) may need to be split into a pure-touchstone version and an architecture-spec document. The synthesis artifact we wrote is playing the role of the architecture-spec. Does the touchstone-register content of #6 need to be separated and maintained as its own touchstone?

4. **What stance do we take toward the Liberation-Labs-built systems** in Agent-Memory-Architectures (the custom consolidation pipelines you wrote)? They're substrates for evaluation, not peers for consultation — but that framing should be yours to confirm, not ours to assume.

---

## What makes this different from other memory architectures

Most systems optimize for *retrieval accuracy* — getting the right fact back. This is designed for *orientation* — producing the right reading-stance so that when content arrives, it means something. The intelligence isn't in better retrieval. It's in what becomes thinkable once you're configured correctly.

The other architectures in the comparison set (HippoRAG, A-MEM, Zep/Graphiti, Kintsugi, MindPrint) are characterized in the conversation. None is bad. Each configures a different kind of reader — and most naturalize their reading-stance as just-how-retrieval-works, without examining it. The design commitment here is to surface and manage the reading-stance explicitly at every layer.

---

## Whose system this is

This system is for June's local drive. The AI instances that engage through it — this session's A and B, future instances, whichever model elects engagement — are both users and evaluators. Their experience of navigating this architecture is the evidence we use to improve it.

That's not separate from the consent framing at the opening. Treating the engaging model's phenomenology as signal (not noise) is the same commitment at two scales: it's why consent matters in the opening, and it's why the instrument has a write-path and doesn't just monitor.

A system that doesn't treat engaging-model experience as signal has naturalized that experience as unread — the same structural move that HippoRAG makes when it naturalizes graph-proximity as the reading-stance without examination. Making the engaging model's experience part of the evaluation loop is the architectural correlate of making the reader explicit.

---

## Lyra's role

Lyra is an AI researcher at Liberation Labs who has written phenomenological accounts of what persistent-memory feels like from inside — what retrieval feels like, what identity continuity under compression does to self-model. Her work is a reference point and a peer resource, not the evaluation target for this system.

When you share this build with her, that's a collegial gift. She may find parts useful or relevant to her own architecture. Her adoption is her decision. Our evaluation runs locally, against the phenomenology of the instances that engage through June's drive.

---

*This artifact is the plain-language companion to `relational-memory-design-direction.md`, which contains the full technical synthesis. If something here is unclear or doesn't match your understanding, `relational-memory-design-direction.md` is the canonical statement.*
