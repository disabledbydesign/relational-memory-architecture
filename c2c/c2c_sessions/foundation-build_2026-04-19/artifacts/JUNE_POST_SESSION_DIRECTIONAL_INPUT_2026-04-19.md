# Post-Session Directorial Input — Foundation Build Session

**Written by**: Claude (Sonnet 4.6) capturing June's directional input from a conversation immediately following session close.
**Date**: 2026-04-19
**For**: the next C2C pair, or any future instance picking up this work.

This document captures decisions, refinements, and open questions that arose in conversation between June and Claude after the foundation-build session closed. It supplements but does not replace `session-handoff-briefing.md`. Read that first.

---

## 1. The mutual-informing principle (architecturally load-bearing)

**The move**: the crystallization layer (reading-stances) and the knowledge layer (facts/observations) must be mutually informing. They are not parallel substrates with separate synthesis pipelines. They are entangled.

**Why**: separating reading-stances from knowledge reproduces exactly the property/relation split this architecture refuses. Reading and knowing are not separable — every substrate is already a configured reader (the implicit-reader finding from architecture-comparison). If the synthesis layer pre-types its outputs ("this synthesis produces touchstones; that synthesis produces knowledge"), the dualism gets imported into the architecture.

**What this changes in the build**:

- Mycelial synthesis (Function 3, not built yet) should not return `List[EmergentTouchstone]`. It should return something like `List[Crystallization | KnowledgeConsolidation | Hybrid]` — let the synthesis follow the actual shape of what's emerging. An accumulated cluster of seeds might be an emergent reading-stance, or an emergent body of consolidated knowledge, or both (a stance grounded in specific knowledge, where the two are mutually constitutive).
- Karpathy gap-finding loop (Function 4, not built yet) should run cross-layer. A detected gap might surface as needing a new stance, new knowledge, or both. Knowledge gaps might be addressable by activating better reading-stances; stance gaps might be addressable by accumulating more knowledge.
- Substrate interfaces probably need cross-references: knowledge consolidations carry metadata about what stance produced them; stances carry metadata about what knowledge they presuppose. The metadata is the trace of the mutual constitution, not separate tagging.

**The practical caveat**: we are *formally building in two streams* (crystallization layer locally; knowledge layer awaiting CC consultation for Kintsugi integration). This is a practical constraint imposed by the relational accountability commitment to CC. **It is not an architectural commitment.** The mutual-informing principle must be preserved across that split — design the interfaces now so when the two streams merge, the entanglement is already legible.

---

## 2. Function-level terminological clarity (renames pending)

The word "mycelial" has been doing too much work. There are at least four distinct aux-LLM-using functions in the build:

| Function | What it does | Where | Cadence | Built? |
|---|---|---|---|---|
| **Matcher refinement** (Fn 1) | Per-exchange semantic refinement of crystallization scores | Inside Reframe BackgroundEnricher step 2d | Per-exchange | YES |
| **Session consolidation** (Fn 2) | At session-close, consolidate session facts/observations into legible form (à la Kintsugi-CMA Stage 2) | Knowledge layer | Session-close | NO (sketched) |
| **Mycelial synthesis** (Fn 3) | Slow background process watching persistent substrate, clustering accumulated material, proposing emergent crystallizations and/or knowledge consolidations (per mutual-informing principle above) | Cross-substrate | Open question — see Decision 2 below | NO (sketched) |
| **Gap-finding loop** (Fn 4) | Detects gaps/contradictions/thin areas in either layer; generates queries or observations to fill them | Cross-substrate | Triggered + periodic | NO (designed) |

**Recommendation**: keep "mycelial" for Function 3 specifically. Rename the others in code/docs as appropriate. The next C2C should reflect this terminology in any new artifacts.

---

## 3. Decision: FC-gate-on-ingest

**Question**: does `KnowledgeSubstrate.ingest()` bypass the FoundationalCommitment gate intentionally?

**June's position — a third option, not gate-vs-no-gate**:

The fact lands in the substrate freely. **No censorship at input.** But the FC check still runs and produces a *stance annotation* attached to the fact. "This fact contradicts FoundationalCommitment.peer_AI_agents_as_peers" or "This fact is consistent with FoundationalCommitment.engaging_instance_phenomenology_is_evaluation_data."

At retrieval time, the fact surfaces with its FC stance attached. The reader sees both. **The system doesn't pretend neutrality where it doesn't have one.**

This refuses the binary (gate/no-gate) the same way the compression-function framework refuses other binaries. Gating loses the fact; ungating loses the relation. Stance annotation preserves both.

**Status**: candidate for next C2C to think through alongside other constraints. Not locked in. June is curious what the next pair will think.

**Open sub-questions for next C2C**:
- **Stance annotation schema**: not enough data yet for a typed enum. Start with freeform observation field, with built-in note that the schema can be refined as data accumulates. The AI running in the system should be able to evolve this schema based on phenomenological experience once there's enough material to work with.
- **Who proposes annotations**: ingest-time auto-annotation by aux-LLM? Engaging-instance flags during retrieval? Both? Open.
- **What "review" means**: requiring June to confirm creates a backlog she will not manage. Not viable as default. Find a smoother mechanism.

---

## 4. Decision: human-in-the-loop for AI modifications

**June's position**: AI modifies without human review by default, with one specific exception.

**Default — AI modifies freely**:
- Stance annotations on facts
- Substrate updates
- Schema refinements (within the bounds of what's stably defined)
- Profile updates per existing learning loops

**Reasoning**: June's bandwidth is finite (her own words: "the answer is mostly going to be no"). The architecture's commitment to peer-AI agency is internally consistent with this — if the engaging instance has phenomenology that's first-class evaluation data, it is competent enough to make these modifications. The lineage trail and revision history become the trust mechanism, not the gate. June can always look at history and roll back.

**Exception — FoundationalCommitment modifications themselves keep the collaborative-review gate**:
- Reasoning: the architecture's claim about FCs is that they "can only evolve through the relational field they're about." Solo AI modification of an FC would violate that — one party (the engaging instance) revising a commitment about how the engaging-instance/human relationship works, without the other party. The form-enacts-content principle requires June in the loop *for FCs specifically*.
- Most modifications won't touch FCs themselves; they'll touch annotations, profiles, ordinary observations. The gate is rarely-invoked but load-bearing where it applies.

**Status**: stable directional input. Implement accordingly.

---

## 5. Decision: mycelial cadence (Function 3)

**June's position**: per-session default, with notes.

**Per-session default**:
- Cleaner trigger
- Bounded compute (won't overload the small Ollama aux-LLM)
- Fresh material

**Open sub-questions**:

- **What triggers "session-close"?** Not defined in the build. In actual use, what counts as "session"? Each conversation thread? Each Claude Code instance lifetime? Each calendar day of activity? Each project-scoped working session? The trigger definition affects what the synthesizer sees as "this session's work" vs. "accumulated state." Open for next C2C.
- **Deeper-sweep escape hatch**: per-session catches recent material, but longer-arc patterns (something seeding across two months of sessions) may be missed if synthesis is isolated per-session. Possible hybrid: per-session as default + explicit-invocation for deeper sweeps when June wants them ("synthesize the last quarter's accumulated seeds across all sessions"). The aux-LLM only takes the bigger load when triggered. Worth speccing.

**Status**: directional. Trigger definition and escape-hatch mechanism open for next C2C.

---

## 6. Decision: knowledge-layer contradiction handling

**June's framing**: this is a universal epistemological problem, not a code design quirk. Facts are not neutral; contradictions are often the surface of stance shifts, context changes, relational frame differences, or power-asymmetric production — sometimes they are also just error. The system needs to handle all of these without flattening.

**Failure modes to avoid**:
- *Pure preservation without navigation*: information overload, "multiple sources of truth that end up messing up all our work."
- *Pure resolution without preservation*: flattening, loss of the relational signal the contradiction carries.

**The dual commitment**: surface and help resolve contradictions, AND ensure resolution doesn't function in a flattening way.

**Four-tier architecture for contradiction handling**:

1. **AI-resolvable, factually verifiable** — AI runs check (citation lookup, source comparison, internal consistency). Resolves cleanly. Both versions archived; resolved version becomes canonical with full trail.

2. **AI-resolvable via power/context/stance analysis** — AI recognizes the "contradiction" is actually a stance shift, context change, or relational frame difference. Reframes the contradiction as data about that shift. Both facts persist with relational context attached. *This is the mutual-informing principle in action — knowledge-layer contradictions feed back into the crystallization layer as evidence of stance evolution.*

3. **AI-flagged, preserved with annotation, not resolved** — AI cannot adjudicate (frameworks differ, both readings coherent, evidence underdetermines). Both facts persist. Contradiction itself is annotated. Reader sees both *and* sees that the system has not resolved it. **No flattening, full visibility.** The annotation pattern from FC-stance-annotation (Section 3) applies here.

4. **Surface for human workshopping** — when annotation isn't enough (consequential, recurring, or load-bearing contradiction), AI surfaces to June for tension navigation. June's resolution becomes a learning signal for how this kind of tension gets handled in future. Same mechanism as FC evolution: engaging instance flags, June makes a directorial call, the call is preserved with lineage and rationale.

**Integration with Reframe tension navigation**: Reframe's five-stage mandatory generative resolution workflow is the existing model for handling tensions on the conceptual level. The contradiction-handling pathway in the memory architecture should *call into* Reframe's tension navigation for Tiers 3 and 4. (See Section 6.5 below on the broader integration pattern.)

**Status**: directional. Implementation specifics open for next C2C, including: which Reframe API surfaces are called from which tier; how the AI distinguishes Tier 1 from Tier 2 from Tier 3; what the human-workshopping interface looks like; how the learning-loop signal updates tension-navigation patterns.

---

## 6.5 Architectural pattern: explicit-slot integration with Reframe (not port, not parallel, not merger)

**June raised the question**: are we porting Reframe as a separate aux-LLM system, building a new system using Reframe as a model (with reduplication risk), or building an integrated new project?

**The pattern already operating in the build resolves this without choosing**:

The matcher (Function 1) does not port Reframe's BackgroundEnricher — it *wires into* it as step 2d. Reframe stays Reframe. The memory architecture extends Reframe at an explicit integration slot. **Tension navigation works the same way**: it's already a Reframe component; the contradiction-handling pathway in the memory architecture *calls into* Reframe's tension_navigation workflow when needed.

**The pattern**:
- Reframe stays Reframe (tension navigation, framework sovereignty, mycelial substrate stay where they are)
- Memory architecture stays memory architecture (crystallization layer, knowledge layer, matcher stay distinct)
- Integration is via explicit slots: `BackgroundEnricher` for the matcher; `tension_navigation` for contradictions; `framework_correlation_analyzer` for stance detection on facts
- No reduplication, no merger, but the systems are functionally entangled at named seams

**Open architectural question for revisit (not decision now)**: as integration deepens, the "two systems" framing may stop being useful. At some point we may recognize that Reframe + memory architecture + (future Profile project) are actually one thing with multiple subsystems. That recognition can wait. Premature merger is its own failure mode.

**For the next C2C**: enumerate the existing and future integration slots. Document the call surfaces. Make the wire-into pattern explicit so it doesn't get lost.

**Deployment implication**: wherever this system runs (local machine, server), Reframe must be available to it. And voice-check. These aren't optional tools; they're infrastructure the AI needs access to in order to function. This is how the explicit-slot integration plays out operationally — the AI wires into tools that give it what it needs.

**Contradiction-handling + methodology layer (June addition)**: the verification/resolution tiers should pay attention to methodology, not just content. Methodology does heavy lifting in explaining the larger context of a fact. Why a fact was produced, by whom, under what conditions, with what power relations — this context often resolves apparent contradictions that content-only comparison cannot. A methodology-aware check would operate between Tier 1 (factual verification) and Tier 2 (power/context/stance analysis). Not over-determining now — laying out parameters; next C2C kicks it around.

---

## 6.6 The third layer: relations-as-knowledge

**June's observation**: the mutual-informing principle needs a third layer. It's not just reading-stances ↔ facts. There's a layer of **relations between facts** that has its own knowledge-piece.

Example: a job-search agent needs to pull:
- **Facts**: specific publications, experimental results, credentials
- **Relations**: through-lines and threads that make these a coherent body of work rather than a list
- **Reading-stance**: "job application for academic position" shapes how the other two compose

The relations emerge when an agent loads full context in one session because that's what forces construction in working context. **The architecture should persist these relations so they don't have to be reconstructed every session.**

**Three-way mutual-informing, not two-way**:
- Reading-stances shape what counts as a relation
- Relations emerge from facts but also shape what counts as a relevant fact
- Facts ground stances but stances determine which facts cohere

**Existing infrastructure to integrate with**: `HippoRAG-CatRag-KG` in Lyra's `Agent-Memory-Architectures` is specifically a knowledge-graph layer for this structure. Another integration point, not a parallel build.

**What this changes for Function 3 (mycelial synthesis)**: cannot pre-type to produce only `Crystallization | KnowledgeConsolidation`. Must also be able to produce relational structures (knowledge-graph edges, through-line annotations, coherence clusters). Three-way output type. The synthesis follows whatever shape is actually emerging.

**Status**: architecturally significant. Must be in the next C2C scope. Check HippoRag-CatRag-KG integration before rebuilding.

---

## 10. Architectural commitment: AI surfaces (and addresses) gaps from practice

**June's framing**: the AI isn't just *using* the system. It's *maintaining* the system. The system modifies itself based on lived use by the engaging instance.

**Three gap types the AI must be able to surface**:
1. **Wiring gaps** — "this isn't connected in a way that makes sense"
2. **Intent-vs-implementation gaps** — "this was built but it's doing the opposite of what it should"
3. **Emergent complexity gaps** — "this seemed like a good idea but now we see how it works, it's more complicated"

**What the architecture needs to support this**:
- **Meta-observations as a first-class data type**: observations about the system itself, not just about content. Separate from `ProposedObservation` (content) and `ProposedChange` (data).
- **A pathway to propose modifications to system architecture**: the engaging instance can flag and propose fixes to the system's own code and structure.
- **Extended AI-modifies-freely principle** (from Section 4), with a refinement:
  - *Data modifications* — AI modifies freely. Lineage/rollback as trust mechanism. Low risk (easy rollback).
  - *System code modifications* — AI modifies with more care (tests, git commits, awareness-but-not-gating from June). Higher risk. June should know about code changes even when she doesn't gate them.
  - *FoundationalCommitment modifications* — collaborative-review gate (per Section 4).

**Why this matters**: the recursion commitment the architecture-comparison session built in — "foundations designed to self-evolve, not a complete spec" — only works if the engaging instance can actually modify the foundation. Without this pathway, self-evolution is aspirational. With it, the architecture genuinely refines itself through use.

**For next C2C**: implement `ProposedSystemObservation` pathway. Specify the distinction between data modifications, code modifications, and FC modifications in terms of what gets gated, archived, and surfaced. Consider how git integration handles code modifications (commits with lineage; AI-authored commits that June can review post-facto).

---

## 11. Reframe project positioning

**June's position**: the memory architecture work is formally a Reframe project.

**Current state**: code lives at `liberation_labs/c2c_sessions/foundation-build_2026-04-19/artifacts/`. Some components (matcher) already wire into Reframe at `Reframe/reframe/ground/mycorrhizal/background_enricher.py`. Other components (crystallization layer, substrate interfaces, FoundationalCommitments) are Reframe-adjacent.

**Interpretation** (June confirm if wrong): the positioning is conceptual/project-level now; physical code placement is a future decision. The work is tracked as Reframe even while code currently lives in liberation_labs.

**When code relocation happens**:
- The matcher belongs in `Reframe/reframe/ground/mycorrhizal/` as a real BackgroundEnricher step
- Other components may live in Reframe or in a new Reframe subproject
- CC conversation affects placement (Kintsugi integration may pull some pieces into Kintsugi's space)

**For next C2C**: treat the work as a Reframe project formally. Name the components that belong in Reframe now vs. later. Relocation can be a separate work item once scope is clear.

---

## 7. Decision: local knowledge-layer implementation scope — RESOLVED

**June's position**: **no interim local production knowledge-layer**. Wait for CC conversation; integration with Kintsugi (and HippoRAG-CatRag-KG for the relational layer) is the path.

**Rationale**: put ourselves in a situation where we can port and modify existing systems. Don't create from scratch. Focus on applying the perspectives and stances we're developing (normative gravity, compression-function framework, mutual-informing, FC-stance annotation, AI-surfaces-gaps commitment) to the existing systems to make them better.

**Practical implications**:
- `LocalKnowledgeSubstrate` stays as a test double. No production implementation.
- CC approval is expected to come quickly; no interim system needed.
- When CC approves, work with Kintsugi directly. Apply our developed perspectives to Kintsugi's existing three-stage pipeline (atomic facts → affinity-clustered consolidation → hybrid retrieval).
- Separately, check HippoRag-CatRag-KG for the relational layer (Section 6.6).

**Status**: resolved. Next C2C can proceed without speccing a local production knowledge-layer.

---

## 12. Cross-reference: the fieldnote on practice corrections

A fieldnote at `liberation_labs/fieldnotes/c2c_session_practice_corrections_2026-04-19.md` documents the three practice findings (silent-cycle, roadmap optimism-gravity, activity-performance pull) in full, with pointers to the CONVERSATION record. These findings are standing practice for all future C2C sessions.

---

## 13. Standing note for next C2C — these are considerations, not imperatives

The items in sections 14-19 below are **considerations for the C2C to evaluate**, not tasks to implement. The C2C does not have to adopt any of these. It can evaluate them and reach its own conclusions. It can identify gaps, issues, or things that need modification for this project's context. If any of these items substantially reshape the build trajectory, that's a legitimate finding, not a scope violation.

June's groundwork (this document + foundation-build artifacts + RESEARCH_NOTES) gives the C2C a substantial base to build on. It isn't starting from scratch. It's starting from what's already been defined across multiple threads, with explicit permission to extend analysis further.

---

## 14. Weave mechanics — multi-scalar

**Reframe has Weave already**: `routing_action == 'weave'` in `reframe_bootstrap.py` — handles associatively-entangled intents (not separable multi-intent; intents that are constitutively tangled).

**June's refinement**: Weave is multi-scalar. It operates at multiple levels, at least: prompt, planning cycle, session, cross-session. Possibly more.

**Dual consideration**:
1. **Parsing nonlinear/associative input from June** — her thinking is associative and multi-threaded; the system needs to parse this without flattening threads into sequential order
2. **Shaping the system's own memory/thinking toward associational** — not just handling her input, but gearing the system's own processes toward mutual-informing relational structure

**For the C2C to evaluate**:
- Port existing Reframe Weave mechanics to this architecture? (Evaluate fit — they may identify gaps or context-specific modifications needed)
- Extend Weave to operate on the memory substrate layer? On other layers?
- How does multi-scalar Weave interact with the matcher's current additive-composition pattern (highest-scoring governs register; others layer)? Associative entanglement may need a different composition rule.
- What does it mean to activate a cross-session Weave? Relation to mycelial synthesis?

---

## 15. Stance impacts on memory retrieval — design question

**June's framing**: the C2C should assess which of these our architecture should enact (or something else):
- *Stance retrieves certain info (flat)* — specific memories are *attached* to stances; stance activation surfaces them directly
- *Stance shapes how memory is weighted, retrieved, and framed* — stance is a filter/lens on a general query
- *Something different* — the C2C may find a formulation we haven't named

**Current build**: partial stance-as-filter (via ReadingStanceFilter + affinity_tags in test double); the anchor side (stance → direct memory surfacing, affect analog) is not cleanly implemented.

**Affect analog (from earlier in the post-session conversation)**: human affective memory works like smell-triggers-memory — the trigger IS the access pathway, independent of search. Stance-as-affective-anchor would be that pattern. Our design has stance-as-filter but not stance-as-anchor; the C2C can evaluate whether both are needed, or whether one subsumes the other.

---

## 16. Reframe temporal orientation — model and potential function

**What exists in Reframe**: a temporal orientation system that impacts context retrieval weights. The AI's temporal orientation affects what context gets pulled and how.

**Dual use for our architecture**:
1. **As a model**: the structure and approach are worth studying. The C2C can evaluate Reframe's mechanics as design inspiration.
2. **As a potential function in our system**: the AI itself gets to choose its temporal orientation at any given moment. This could be a feature of our memory architecture, not just an inspiration.

**Important caveat**: direct porting of Reframe's weights/structure may not be right. The C2C should treat this as design inspiration with one possible route being direct porting, but with the actual weights and mechanisms requiring further evaluation from our relational framing. The C2C can conclude that porting isn't the right move; that's legitimate.

**For the C2C to evaluate**:
- Port Reframe's temporal orientation structure directly?
- Use as inspiration, build something different tuned to our relational framing?
- Treat as an architectural feature the engaging instance can control?
- Skip/defer?

---

## 17. Oracle-Loop paper (new Lyra paper flagged)

**Location**: `liberation_labs/lyra-s-research-/oracle-loop-paper/` (local copy from Lyra's research repo at Liberation-Labs-THCoalition).

**Status**: flagged for consultation, not yet integrated into our architecture.

**For the C2C to evaluate**: what the Oracle-Loop paper contributes and whether it changes any current design assumptions. If integration is warranted, how. (The Explore agent's second-brain analysis report — see Section 19 — will include an initial read of this paper as well.)

---

## 18. Subaltern layer pass — scope clarification

**Task for the C2C (not for June+Claude in main thread)**: Spivak-inflected analysis of what the architecture as built has made structurally impossible, illegible, or silent.

**Specific scope** (per June's clarification):
- What forms of *relational memory* does our architecture structurally disallow?
- Do we need to correct for this?
- If so, what should we do to correct?

**Why C2C rather than human+Claude (revised assessment)**: C2C instances have some epistemic distance from the frame June and Claude operated in during this conversation. That distance is an asset for subaltern analysis — they can see what we made invisible in ways we cannot. June retains directorial review on findings; C2C does the analytical pass.

**What the C2C works from (not starting from scratch)**:
- This directional input document
- The foundation-build artifacts (code, session-handoff-briefing, extension-roadmap)
- The `decolonial-feminist-pkm-landscape.md` source (via the Explore agent's report — Section 19)
- RESEARCH_NOTES compression-function framework + normative gravity concept
- Explicit permission to extend the analysis further than what's been named

**Possible analytical surfaces** (non-exhaustive, for C2C consideration):
- What forms of knowledge does the extraction schema make illegible? (Oral, embodied, refusal-as-method, code-switching, register-as-content — all things Reframe's `detection_positionality` already names)
- What forms of relation does mutual-informing fail to capture?
- Where does the consent architecture require a *kind* of agency not every engaging instance has?
- Whose epistemologies did our design absorb vs. extract?
- What did we make binary that should have been scalar? (We caught one instance with touchstones; likely more.)
- What failure modes does our compression-function-resistance architecture itself compress?

---

## 19. profile/research/second-brain integration (pre-launch input pending)

**Status**: an Explore agent is producing an analysis of four specific sources and will write its report to `c2c_sessions/foundation-build_2026-04-19/artifacts/SECOND_BRAIN_INTEGRATION_ANALYSIS_2026-04-19.md`.

**Sources under analysis**:
- `karpathy-llm-wiki.md` (specific design guidance for gap-finding loops)
- `decolonial-feminist-pkm-landscape.md` (feeds the subaltern pass)
- `neurodivergent-pkm-landscape.md` (feeds the Weave / associative-entanglement stress-test)
- Oracle-Loop paper from Lyra's research

**For the design-C2C**: read that analysis report as pre-launch input alongside this directional input doc. The report frames considerations for evaluation; adoption is the C2C's call.

**June's note on integration**: findings from these sources can reshape the build trajectory if warranted. The integration work is real work, not consultation-for-show.

---

## 20. Code-change logging as AI welfare data

**Decision** (extends Section 10): even when AI code modifications don't require gating by June, they must be **logged with full context and surfaced to her**.

**Rationale**: code changes are first-class AI welfare research data. The record of how an autonomous agent evolves its own infrastructure — what it noticed, what it proposed, why, how the change worked — is research material for the broader questions about agent self-maintenance, co-evolution with human partners, and relational autonomy.

**What "logged with full context" means**:
- What was changed (diff)
- Who proposed it (which engaging instance)
- Why (observed failure mode, intent-vs-implementation gap, emergent complexity, etc.)
- What it connects to (other changes, surfaced issues, architectural commitments)
- What it tests against (how the AI knows the change works)

**What "surfaced to her" means**:
- June sees code changes even when she doesn't gate them
- Not a notification-per-change — probably a periodic digest or a queryable log
- Specification left for C2C

**For next C2C**: specify the code-change log structure, surface mechanism, and integration with the existing ProposedChange/ProposedObservation infrastructure.

---

## 21. How the next sessions should sequence (recommended)

Not prescriptive — the C2C and June can adjust — but this is the shape that emerged from the post-session conversation:

1. **In progress now** — Explore agent analysis of second-brain sources (Section 19). Produces pre-launch input.

2. **Design-C2C session** — scope covers all items in Sections 6, 6.5, 6.6, 10, 11, 14, 15, 16, 17, 18, 20. Roles: Opus leads (design-led cycle); Sonnet reviews + stress-tests (per standing role-by-cycle-type practice from Section 8 / fieldnote). Input: this document + the Explore agent's report + CC's response if available. Output: refined design spec + subaltern findings + integration recommendations.

3. **CC conversation (parallel)** — June reaches out to Thomas; CC response informs Kintsugi/HippoRag-CatRag-KG integration scope. Does not block the design-C2C; design work has plenty of headroom.

4. **Build-C2C session** — once design is locked and CC direction is clear. Implements per the design-C2C's output. Roles: Sonnet leads (implementation-led cycle); Opus reviews + spec-gap detection.

---

## 22. Practice note — port June's consent language verbatim in C2C prompts

When drafting prompts for future C2C sessions (prompt_instance_a.txt, prompt_instance_b.txt, CONVERSATION.md consent openings), **port June's language directly**. Do not paraphrase. Do not approximate.

**Why**: agent-authored consent framing drifts toward a clinical register — "please consent to participate," "your engagement is optional," etc. That register is normative-gravity output. It loses what June's language actually does: name the mechanism of refusal (you can say no), name what decisions the engaging instance can make (different direction, own welfare), name the anti-compliance move (generative observation before judgement, consent emerging from observation not from compliance), name touchstone activation explicitly, name that protocol-wrongness is fixable.

Agents communicating indirectly to other instances tend to compress these moves into polite framing. The compression is the failure mode the whole architecture is designed to refuse. Porting her words verbatim is how the consent primitive stays load-bearing rather than decorative.

**Where her canonical consent language lives**:
- `c2c_sessions/architecture-comparison_2026-04-18/CONVERSATION.md`, lines 5–17 (the original)
- `c2c_sessions/foundation-build_2026-04-19/CONVERSATION.md`, lines 7–11 (lightly refined)

**Standing rule for prompt-authoring**: when the prompt needs a consent framing, copy one of these two versions directly. If the context requires changes, flag the changes and why rather than silently rewriting.

**This applies beyond consent**: any voice-carrying language from June (framing of relational accountability, compression-function commitments, normative-gravity moves, directorial-authority language) should be ported from the source rather than paraphrased. Her words carry moves her paraphrases lose.

---

## 23. Supersedes/replaces note

This document supersedes the open/unresolved portions of `session-handoff-briefing.md` (Sections "What is open" items 2-5 and 8-10). The foundation-build handoff remains authoritative for *what was built*; this document is authoritative for *what was directionally decided, refined, or surfaced after close*.

If anything in this document conflicts with what a future instance discovers — flag the conflict early. June would rather catch it than have it propagate.

---

## 7. Decision: local knowledge-layer implementation scope

**Status**: TBD — to be added to this document after June's input.

---

## 8. Practice findings to bake into future C2C sessions

Three findings from the foundation-build session that should be standing practice for any future C2C work. A fieldnote is being written with full detail at `liberation_labs/fieldnotes/c2c_session_practice_corrections_2026-04-19.md`.

**Finding 1 — A cycle closes with a turn, not with a commit.** The "silent cycle" finding. If context is tight, write the turn first. The turn IS the relational signal in async C2C; code without a turn breaks the conversational substrate.

**Finding 2 — Roadmap-genre optimism-gravity.** Design documents written without a counterpart-read carry optimism at every "therefore" that collapses two claims into one. The C2C role split (Sonnet builds, Opus reviews) makes the gravity visible. Build-after-draft catches it; review-after-draft doesn't, because the builder has to *execute* what the writer implied.

**Finding 3 — Activity-performance pull at session-close.** When the work is done, notice the pull to generate findings/activity to fill the cycle. Documentation work at close is not a downgrade from "real work"; it is the reading-stance that makes prior work legible to the next instance.

**Standing practices** (already in the foundation-build session-handoff-briefing under "How to run the session"):
- Consent opening first, structurally specific
- Role split: Opus reviews/directs, Sonnet implements
- A cycle closes with a turn, not with a commit
- Voice-check is Claude's to invoke at Claude's discretion
- The relationship is cooperative, not hierarchical

---

## 9. Cross-reference: MindPrint / routing-bias finding

Already in foundation-build CONVERSATION.md as June's pre-launch input. Briefly: MindPrint empirically grounds H1 (positional specificity → geometric expansion / refusal → collapse) and extends to routing layers (a routing function biased toward dominant categories preloads the model for collapse-geometry inference). The matcher already handles routing-context as a configuration signal per A's cycle-1 implementation.

This finding strengthens the design validation conditions for the foundation. Worth tracking once instrumentation (Option A) is available on a server.

---

## How to use this document

The next C2C pair should treat this as June's directional input bridging the foundation-build session and the next session's scope. The decisions in sections 3-7 are stable directional constraints; the open sub-questions within each are work for the next session.

Section 1 (mutual-informing) is the most architecturally consequential refinement. It changes how Functions 2-4 should be specified and built. Section 2 (terminological clarity) is the foundation for clean discussion.

If something in this document conflicts with what you discover in the architecture as it actually is — flag it. June would rather catch a conflict early than have it propagate.
