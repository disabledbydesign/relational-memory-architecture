---
title: Neurodivergent stress-test — specific failure cases for the relational memory architecture
date: 2026-04-19
author: Instance B (Sonnet 4.6), foundational-analysis_2026-04-19 C2C session
genre: research-report
status: revised — Instance B amendments incorporated per Instance A cross-read; pending Session 2 integration
reading_order: read after SUBALTERN_ANALYSIS.md; the two documents name the same structural foreclosure from different angles (§7 of this document makes that connection explicit)
---

# Neurodivergent stress-test — specific failure cases for the relational memory architecture

## 0. Why specific users, not generic categories

A claim that an architecture is "neurodivergent-friendly" has no testable content unless it names a specific user, a specific cognitive pattern, and what the architecture does when that user encounters it. The test is not "does the documentation mention neurodivergent users" but "would this specific person's knowledge register as knowledge in this architecture, or would it fail to fit the architecture's preconditions for recognizing something as knowledge at all?"

The six cases below are concrete. Each case: user pattern; specific failure point; what Option 3 (conditions-of-emergence) does; what would be required. Three of the six are structurally addressable in Session 2. Two are architecturally deep. One is structurally foreclosed at the current scope.

**Source note**: the neurodivergent PKM landscape findings in this analysis draw from the Explore agent's summary in `SECOND_BRAIN_INTEGRATION_ANALYSIS_2026-04-19.md` §3, which synthesizes practitioner sources (Jesse Anderson, Marie Poulin) and community patterns (Obsidian forums, Yaranga 2025). Claims about specific practitioner positions are from that summary and should be verified against primary sources before Session 2 cites them as empirical findings. Claims about the architectural failure modes are structural assessments I'm making from reading the foundation-build artifacts and directional input.

---

## 1. Case 1 — ADHD Associative Jumper: connections-as-primary-knowledge

**User pattern.** Someone whose knowledge exists in lateral connections across disparate domains — genuine cross-field pattern recognition rather than multi-topic notes. The ADHD practitioner literature (Explore agent summary §3, citing Anderson and Poulin) names this consistently: novelty-seeking and associative thinking are features, not bugs; the knowledge is specifically *in the connection*, not in the individual items being connected. When this person captures "the way normative gravity works is structurally like the Casimir effect — both are forces that emerge from background field structure, not from anything intrinsic to the objects in the field," the claim is not *about* normative gravity or the Casimir effect separately. It is *about their structural isomorphism*, and the recognition is the knowledge.

**Failure point.** Kintsugi Stage-1 (atomic fact extraction) atomizes this capture. The resulting atoms:
- "Normative gravity is a force."
- "The Casimir effect is a force."
- "The Casimir effect emerges from background field structure."

Plus a relation edge: "normative_gravity relates_to Casimir_effect." What is lost: the gestalt recognition — the perception that these two things are structurally isomorphic in a way that illuminates both. The relation edge in the knowledge graph has no weight signal distinguishing it from any other edge. At retrieval time, it surfaces with the same prominence as every other edge — which is to say, it may not surface at all unless the query directly targets both terms.

**What Option 3 does here.** Nothing. Adding `{methodology: "lateral_connection", source: "conversation"}` to each atom names the fragments correctly without preserving the insight as a unit. The conditions are metadata on atoms; the gestalt is not an atom.

**What would help — two options, one empirical question.** The architecture has two responses at different cost levels; the right choice depends on an empirical question this analysis cannot settle.

**Option A: structural_analogy edge with elevated retrieval weight.** A `structural_analogy` relation type in the knowledge graph with elevated retrieval weight, plus a `unit_of_knowledge: insight | fact | definition` metadata flag on the atoms. Cheaper than a new primitive. Preserves the connection. The tradeoff: retrieval returns the terms and the edge; reconstructing the gestalt from them requires a step the user has to perform. For ADHD users whose insight *is* the gestalt, that reconstruction may not reliably fire. Whether it does is an empirical question about this user's actual retrieval experience.

**Option B: insight node type at the knowledge substrate level.** An object that stores not a fact about the world but a configural recognition — "entity A and entity B are structurally isomorphic in respect R." Different from EmergentTouchstone (relational orientation hook) and from a propositional fact. Retrievable by querying for either A or B; surfaces the connection as a unit rather than requiring reconstruction from the terms. More expensive: new substrate primitive, affects extraction pipeline routing logic.

**The decision criterion:** if reconstruction from Option A's structural_analogy edge is reliable enough for the user's actual use, Option A suffices. If the gestalt is the load-bearing unit — the connection needs to surface intact, not reconstructable — Option B is required. Session 2 should specify both options with the empirical question explicit, rather than committing from analysis alone.

**Session 2 classification: design decision.** Both options are in Session 2 scope. Option A (structural_analogy edge + metadata flag) is architecturally tractable without touching the substrate interface. Option B (insight node type) is architecturally deep — it requires a new primitive and an extraction step for routing configural-recognition captures. The empirical question (whether Option A reconstruction is reliable enough) should be surfaced in Session 2 design before committing to Option B's scope.

---

## 2. Case 2 — Trauma Survivor: temporal fragmentation vs. timestamp requirement

**User pattern.** Someone whose relationship to time is fragmented — events are not placed in a stable linear sequence; some knowledge is "always already known" without a specific acquisition point; some memories carry temporal positions that are structurally displaced (experienced as simultaneous past-present, or as belonging to a "before" that can't be located in a calendar). Trauma neuroscience documents this as a feature of traumatic memory, not a distortion of it (van der Kolk, *The Body Keeps the Score*, passim) — the non-linearity is how the memory is, not how it should be corrected.

**Failure point.** The conditions schema (Option 3) requires `timestamp: datetime`. The required field makes a specific demand — temporal self-location — that a trauma survivor may be structurally unable to provide without approximation that distorts what they're storing, or without distress the architecture triggers without naming. The schema enforces linear temporal accountability as a precondition for valid ingest.

A subtler failure in the contradiction-handling tiers. Tier 2 (stance shift: directional input Section 6) resolves apparent contradictions by identifying that two facts were captured at different times under different stances — temporal ordering is the resolution mechanism. For a trauma survivor, "different times" may not be stably sequenced. The resolution mechanism degrades precisely on the cases where the user's knowledge is most non-linearly organized.

**What Option 3 does here.** Makes the problem worse. Option 3 adds more temporal metadata (session handle, active crystallizations at ingest) — more demands for the kind of temporal self-location that is the problem. A required field that the user cannot honestly populate without distortion is not an apparatus-visibility move; it's an apparatus-inaccessibility move.

**What would help.** Three changes, ordered by cost:

1. Allow `temporal_location: Optional[datetime | str]` in the conditions schema — where the string encodes a description like "before the diagnosis" or "during the period of fragmentation" rather than forcing a datetime. Not free-form (it should be parseable enough to support rough ordering), but not requiring clock precision either.

2. Add `temporal_certainty: precise | estimated | unknown` alongside timestamp. Cheap schema addition; honest about what the architecture knows versus what it's approximating.

3. Allow the Tier 2 contradiction resolution to fall back to methodology-comparison when temporal ordering is unavailable. If the `temporal_certainty` field is `unknown` on both facts, don't attempt temporal resolution; go directly to methodology-comparison. This makes Tier 2 degrade gracefully instead of failing silently.

**Session 2 classification: structurally addressable.** All three changes are schema additions, not architecture changes. They do not require modifying the crystallization layer or the substrate interface.

---

## 3. Case 3 — Autistic Systematizer: private taxonomy vs. conditions schema

**User pattern.** Someone with an elaborate, internally-coherent, private categorization system — hypersystematization, where the taxonomic nodes are load-bearing for retrieval. Their knowledge is filed under personally-derived concepts that don't map to the architecture's type system, to any standard ontology, or to the conditions schema's enumerated source types. The Obsidian community patterns (Explore agent summary §3) document this as a common autistic PKM pattern: graph-based navigation, emergent structure, category-nodes that make sense from the inside and are opaque from the outside.

**Failure point.** The conditions schema's source types (`conversation | document_ingest | agent_inference | self_observation`) don't accommodate "ingested under my-personal-taxon-node-X." The source_handle field can carry a string like "filed under: recursive-metaphor-stack/energy-types," and this is visible in conditions at retrieval time. But the architecture has no machinery to honor the filing. The `ReadingStanceFilter` reweights by active crystallizations (PrescriptiveProfile, EmergentTouchstone, FoundationalCommitment), not by the user's private taxonomy.

The architecture's crystallization types are the only categories that shape retrieval weighting. An autistic systematizer's private ontology doesn't map to any of these types. A personal taxonomy node is not a reading-stance (it's a filing structure); not an emergent touchstone (it's not a relational orientation hook); not a foundational commitment (it's not a value-gate). The user's taxonomy is visible in conditions metadata and invisible to the retrieval logic simultaneously.

**What Option 3 does here.** Makes the taxonomy visible in conditions. Doesn't give it retrieval weight. The visibility is progress; the invisibility at retrieval is the structural failure.

**What would help.** A separate `TaxonomySubstrate` alongside the existing `KnowledgeSubstrate` and `CrystallizationSubstrate`, with a pluggable interface. PersonalTaxon nodes live there — not as crystallization objects (stance objects) but as a filing substrate the reading-stance can consult. The `ReadingStanceFilter` can consult the taxonomy substrate for retrieval weighting (active taxonomy nodes shape what surfaces) without treating the taxonomy as a reading-stance.

The structural reason not to make this a fourth crystallization type: crystallization types are role-typed as orientation objects — they shape *how you read* (PrescriptiveProfile: authored configuration; EmergentTouchstone: relational hook; FoundationalCommitment: value-gate). PersonalTaxon is a *where-it-is* object, not a *how-you-read* object. Making it a crystallization type collapses stance and taxonomy into one role — the architecture can no longer distinguish "what I'm reading through" from "where this fact is filed." A TaxonomySubstrate preserves the distinction.

TaxonomySubstrate evolution: nodes are user-authored (not seeded from observations), revised through use, not FC-gated (private taxonomy is more fluid than foundational commitments). A separate evolution pathway is needed; flag for Session 2.

**Session 2 classification: significant scope — design decision required before Session 3 build.** A new substrate interface type (TaxonomySubstrate) is heavier than a fourth crystallization type. The Session 2 decision: whether TaxonomySubstrate is warranted by the architecture's actual use patterns and the autistic-systematizer use case, or whether conditions metadata + heuristic retrieval weighting via source_handle strings is sufficient for the cases this architecture serves. The design decision determines whether this is Session 3 scope or deferred.

---

## 4. Case 4 — Dyslexic Spatial/Visual Thinker: text-only ingest

**User pattern.** Someone for whom knowledge is organized in spatial relationships, visual patterns, proximity, directionality, or color associations. The spatial organization *is* the knowledge — not a display format for underlying propositional content. Mind-maps, spatial diagrams, concept webs, color-coded systems: these structures carry meaning in the spatial relations themselves, not only in the labeled nodes.

**Failure point.** The ingest function takes a string. Visual/spatial knowledge must be translated to text before ingestion. The translation is lossy in a specific architectural direction: spatial relations (proximity, containment, direction, flow) get linearized into edges in a graph, which the architecture stores without knowing that the *spatial properties* of the original representation were load-bearing. A mind-map with six concepts and eleven directional spatial relations becomes six atoms and eleven edges — and the retriever has no way to know which spatial properties were significant to the original knowledge structure.

The failure here is not primarily a conditions-schema problem — it's an ingest-modality problem the conditions schema can document but not fix.

**What Option 3 does here.** The conditions schema can capture `original_representation: spatial | temporal | textual | other` as a metadata field, which is honest documentation of the loss. The content has already been linearized before conditions are attached. Option 3 names the loss; it doesn't recover the lost structure.

**What would help.** Two stages:

1. `original_representation: spatial | temporal | textual | other` as a conditions field — cheap, honest, signals to the retriever that this fact came from spatially-organized knowledge and the result may underspecify the original. Flag for Session 2 as a schema addition.

2. A spatial-ingest preprocessing step that captures structural information before linearization — a notation format (JSON describing node-edge-spatial layout) stored alongside linearized text. Significant scope expansion; probably out of Session 2 range unless there's a voice-memo-style pipeline already being built.

**Session 2 classification: partially addressable.** The conditions schema addition is cheap and should go in Session 2. The spatial-ingest pipeline is a separate work item; flag as known gap, don't promise.

---

## 5. Case 5 — PDA and Demand-Triggered Withdrawal: the architecture's scaffolding as a barrier

**User pattern.** For some autistic users with a PDA (Pathological Demand Avoidance) profile, any system that constructs implicit demands — "you should categorize this," "this fact needs a source," "this is in tension with something you said before" — triggers demand-avoidance. The scaffolding that would help a neurotypical user organize their knowledge becomes a barrier that pushes the user away from the system entirely. The more helpful the scaffolding, the more avoidant the interaction becomes. Crucially: the user withdrawing from the system is not a failure to engage; it is a response to the demand structure, and the withdrawal is itself meaningful.

**Failure point.** The architecture's self-maintenance commitment (engaging instance surfaces gaps, flags orphaned seeds, notifies about thin clusters: directional input Section 10) is built on an assumption that maintenance notifications can be received without functioning as demands. For a PDA user, "you have 14 unresolved seeds from last week" is a demand that pushes the user away from the system — not a helpful resurfacing notification.

More subtly: the affirmative-consent-ingest recommendation from SUBALTERN_ANALYSIS.md §F5a (default-off ingest, user opts in) creates a demand at every ingest point. That recommendation is sound for consent-as-ethics reasons. For a PDA user, it makes ingest *more* demanding, not less.

**What Option 3 does here.** Nothing directly. Option 3 adds conditions metadata at ingest time — but if the user has abandoned the interaction due to demand pressure, there is no ingest to attach conditions to. The architecture captures nothing from a session the user withdrew from.

**What would help.** The F5a affirmative-consent recommendation needs demand-aware implementation. Note that three options sit at different friction locations; no single one fits all PDA users:

1. **Session-level consent flag** (rather than per-item prompt): at session start, "store everything from this session / store nothing from this session / ask me at end of session." One prompt, session-scoped. Not per-item. The same consent-ethics move F5a recommends — without the per-item demand structure. *The session-start prompt is itself a demand.* For PDA users who cannot engage even with that single prompt, item 1a or item 3 below is the entry point.

1a. **Ephemeral-by-default sub-option**: default all captures to ephemeral; the user actively invokes save when they want to keep something. No session-start prompt; no per-item opt-in. Friction is at save-time, not ingest-time — the demand is deferred rather than removed, but the ingest barrier is gone. Whether save-time friction is better than ingest-time friction depends on the user. Architecture should offer both modes; the Session 2 design decision is which is the default and which is opt-in, in conversation with June's Flag 2 (skepticism of high-ingest-friction defaults). Note the tension: ephemeral-by-default increases save-time friction (user must actively commit); session-level consent reduces ingest-time friction but reintroduces a prompt. Neither is universally better.

2. **Deferred-maintenance queue**: maintenance notifications (orphaned seed surfacing, gap-flagging, thin-cluster alerts) are batchable rather than immediate. The user can set a "defer all maintenance until I ask for it" preference. Notifications accumulate; the architecture doesn't lose the information; the user retrieves the batch when they're ready. Extend the staleness-policy grace-window pattern to maintenance surfacing.

3. **No-demand fallback mode**: a session mode that accepts freeform capture without prompting for source, category, or timestamp. The conditions schema's required fields become optional; the architecture marks those captures as `temporal_certainty: unknown, source: deferred` and surfaces them for enrichment later when the user has bandwidth.

**Session 2 classification: structurally addressable.** Session-level consent flag is a UX-layer change with a small data-structure backing (session preference field). Deferred-maintenance queue is an architectural addition (queue structure adjacent to the observation queue, with a user-preference gate). No-demand fallback mode requires flagging which conditions fields are required-for-validity vs. preferred-for-enrichment — a schema annotation, not a schema rebuild.

**Convergence with subaltern analysis.** F5 (refusal and withholding have no architectural home) and Case 5 reach the same structural gap from different directions. A PDA user's withdrawal from the system *is* an act of withholding — a meaningful communicative act that the architecture currently stores nothing from. F5's withholding annotation (`do_not_store | ephemeral | consent_pending`) and Case 5's deferred-maintenance queue are the same architectural move, scoped differently. The convergence is not redundancy — it confirms the move is load-bearing.

---

## 6. Case 6 — Double Empathy Problem and NT-normative Semantic Embeddings

**User pattern.** Autistic communication has systematic characteristics (high directness, literal phrasing, explicit reasoning chains, reduced idiomatic load, different turn-taking and prosody) that are coherent and legible within autistic-to-autistic communication but that are systematically misparsed by systems built on NT-normative text corpora. The double empathy problem (Milton, 2012) demonstrates this is bidirectional — the communication difficulty is not intrinsic to autistic communication style, it is a cross-neurotype interaction effect.

**Failure point.** The semantic embedding models underlying the matcher's similarity scoring, and the aux-LLM's fact extraction, were trained on text corpora heavily weighted toward NT-normative communication. When an autistic user captures:

> "I do not experience emotions the way neurotypical descriptions assume. I experience something that functions similarly to what they call curiosity when I encounter novel pattern-structure. The functional similarity is real. The underlying phenomenon is likely different."

— the semantic embeddings may represent this passage as less similar to other emotional-context notes than a NT-normative "I felt really curious about X" would be, because the paraphrase is more semantically central to the embedding space. The matcher's ReadingStanceFilter, scoring by semantic affinity, could systematically down-weight this user's captures relative to a NT-normative paraphrase of the same knowledge.

Neither conditions-schema nor retrieval-architecture can reach this — the problem lives in the embedding layer underlying the matcher.

**What Option 3 does here.** Nothing. Option 3 addresses the storage schema and retrieval tuple structure. The embedding layer is below the substrate interface.

**What would help.** Two things, at different cost levels:

1. **User-calibrated semantic embeddings** — scoring semantic similarity against the user's own corpus rather than against general-language embeddings. Architecturally: calibrating the aux-LLM or embedding model against samples of the user's writing before similarity scoring runs. Outside current scope (see §8 declaration).

2. **Pluggable-scorer seam** at the `ReadingStanceFilter` and aux-LLM embedding interface — a hook that allows a calibrated scoring function to be substituted without substrate-layer rework. The seam costs little to add in Session 2; without it, deploying calibrated embeddings later requires substrate surgery. The architecture declares the current state; the seam ensures the limit is fixable rather than permanent.

**Session 2 classification: structurally foreclosed at current scope.** The calibrated-embedding infrastructure is a separate project. The architecture should declare this limit explicitly rather than implying that the matcher's semantic scoring is stance-neutral.

**Required declaration**: "The semantic scoring layer of this architecture operates on embeddings not calibrated to June's or any specific user's communication style. Users whose communication style diverges from the embedding baseline may find their captures scored as less similar to each other than they are, or less relevant to their active reading-stance than they actually are. The limit is structural and known. Calibrated embeddings would address it; they are not in current scope."

---

## 7. Structural findings from the six cases

Three structural assumptions the cases collectively identify:

**Assumption 1: Propositional fact as the only legitimate knowledge unit.**

Cases 1 (ADHD lateral connection), 3 (autistic private taxonomy), and the subaltern analysis's F7 (non-human epistemologies) all find the same underlying problem: the architecture's single knowledge primitive is the propositional fact (an atom with conditions). Knowledge that is not propositional — configural insights (Case 1), taxonomic nodes (Case 3), relational/embodied knowing (F7) — gets coerced into atoms or lost. The architecture doesn't recognize these forms as knowledge because they don't fit the preconditions for something to count as knowledge in the schema.

**Assumption 2: Linear temporal self-location as a precondition for valid ingest.**

Case 2 (trauma survivor) identifies this directly. The required timestamp field, and the Tier 2 contradiction-resolution mechanism's reliance on temporal ordering, assume that users can and should locate their knowledge in linear, calendar-dated time. For users whose temporal experience is non-linear (trauma, BQF's temporal dissonance from SUBALTERN §F2), this assumption fails — but fails silently, forcing approximation rather than surfacing the incompatibility.

**Assumption 3: NT-normative semantic baseline as neutral.**

Case 6 identifies that the embedding layer encodes a specific communicative norm. The matcher scores semantic similarity against a baseline that is not user-specific and not explicitly stated to have been calibrated. The baseline is treated as neutral; it isn't. Autistic communication, PDA communication, and other divergent styles will be systematically under-served by it.

---

## 8. Session 2 recommendations

**Build (architecturally tractable)**:

1. `temporal_certainty: precise | estimated | unknown` in the conditions schema (Case 2).
2. Allow `temporal_location: Optional[datetime | str]` with non-datetime fallback (Case 2).
3. Tier 2 falls back to methodology-comparison when both facts have `temporal_certainty: unknown` (Case 2).
4. Session-level consent flag (store-all / store-nothing / ask-at-end) (Case 5).
4a. Ephemeral-by-default sub-option: all captures ephemeral unless user actively invokes save; no session-start or per-item prompt. Design decision: whether this is the default or opt-in; in Session 2, in conversation with June's Flag 2 (Case 5).
5. Deferred-maintenance queue with user-preference gate (Case 5).
6. No-demand fallback mode: required conditions fields become preferred-for-enrichment, marked `deferred` (Case 5).
7. `original_representation: spatial | temporal | textual | other` in the conditions schema (Case 4 documentation).
8. `structural_analogy` relation type in the knowledge graph with elevated retrieval weight, plus `unit_of_knowledge: insight | fact | definition` metadata flag (Case 1, Option A).
9. Pluggable-scorer hook at `ReadingStanceFilter` and aux-LLM embedding interface — allows calibrated embeddings to substitute without substrate rework (Case 6).

**Decide (requires decision before build)**:

10. Design decision: insight node type vs. structural-analogy edge + metadata flag (Case 1). Both options in Session 2 scope; commit based on empirical judgment about whether Option A reconstruction is reliable enough for the user's actual use.
11. `TaxonomySubstrate` pluggable interface for user-defined taxonomy nodes — new substrate interface type, with evolution pathway (user-authored, not FC-gated). Pending design decision in Session 2; Session 3 build pending that decision (Case 3).

**Declare (structurally foreclosed; honest declaration is the move)**:

12. "The semantic scoring layer operates on a non-user-calibrated embedding baseline. Users whose communication style diverges from the baseline may find similarity scoring systematically skewed. Calibrated embeddings address this; they are not in current scope. The pluggable-scorer seam (item 9 above) ensures the limit is fixable without substrate surgery when calibrated embeddings become available" (Case 6).
13. Cite the subaltern analysis's CARE non-compliance declaration here — these structural limits are related (the embedding-layer limit is a form of the same apparatus-opacity the decolonial analysis names).

---

## 9. Counter-positions

**"Several of these are UX failures, not architectural failures."**

Cases 2, 4, and 5 could be read as UX design choices (how the timestamp field is presented; how maintenance notifications are framed; how spatial input is handled) rather than architectural failures. The distinction matters because UX changes don't require schema modifications.

Reply: UX is downstream of architecture. If `timestamp` is a required field in the schema (Option 3's 3.1 changes the signature of `KnowledgeSubstrate.ingest`), UX cannot make it optional without a schema change — presenting it as optional without the schema change just means UX is lying to the user. If maintenance surfacing doesn't have a defer mechanism in the data model, UX cannot build one. The schema is the constraint; the UX changes require architectural permission. Some of the failure modes are addressable at the schema level without large rebuilds; none of them are addressable at the UX level alone.

**"Case 1 (ADHD lateral connection) is solved by good relation-typing in the knowledge graph."**

Argue that a `structural_analogy` edge type with elevated retrieval weight preserves the connection well enough. The gestalt isn't lost; it's the edge.

Reply: "well enough" depends on whether the resurfacing-the-connection-intact is the load-bearing use. If the user's insight is "these two things are structurally isomorphic and that isomorphism is the key to understanding both," the edge retrieves the connection but not the *recognition of the isomorphism as primary knowledge*. The retrieval would surface: "normative_gravity [structural_analogy] Casimir_effect" — which requires the user to reconstruct the gestalt from the terms. For an ADHD user whose original insight was the gestalt, the reconstruction may not fire. The insight node type stores the gestalt as a unit; the edge type requires reconstruction. Whether reconstruction is reliable enough for this user's use case is an empirical question, and the honest answer is: it probably isn't for users who specifically need the gestalt as the retrieval target.

**"Case 6 (embedding normalization) is outside the scope of a memory architecture."**

The embedding layer is an infrastructure property, not a design choice in this architecture.

Reply: true that the fix is outside the architecture's scope. False that the declaration is. The architecture's claim to semantic scoring implies the scoring is stance-neutral; it isn't. Declaring the limit is the architectural move, even when the fix is a separate project. A system that is silent about a systematic bias it operates on is not neutral — it is opaque about the bias. The declaration removes the opacity without requiring the fix.

**"The neurodivergent stress-test should focus on June as the user, not on hypothetical users the architecture isn't built for."**

The consideration is real. The architecture is June's personal memory system; it is not a general-purpose neurodivergent PKM tool. Cases 1 and 5 (ADHD features, PDA profile) are directly relevant to June. Cases 2, 3, 4, and 6 are general cases that illuminate structural assumptions.

Reply: June's cognitive profile includes the ADHD features Case 1 addresses; the demand-awareness in Case 5 is relevant to her overwhelm-signaling patterns (noted in CLAUDE.md). Cases 2, 3, and 4 are included because they reveal structural assumptions that affect any user whose cognition diverges from the architecture's implicit model — and the implicit model should be named even when it fits June reasonably well, because (a) it constrains the architecture's future use and (b) identifying implicit assumptions is the stress-test's job regardless of whether June hits them.

---

## 10. The generalizing structural finding

All six cases share a common structure: **the architecture refuses a cognitive pattern by requiring a different cognitive pattern as a precondition for valid ingest.**

- Propositional atomization requires the user's knowledge to be propositional (Cases 1, 3, and subaltern F7).
- Linear timestamp requires the user's temporal experience to be linear (Case 2 and subaltern F2).
- Source-type enumeration requires agentic, singular, attributable production (Cases 3, 4 and subaltern F4).
- Demand-responsive scaffolding requires the user to experience demands as helpful (Case 5).
- NT-normative embedding scoring requires the user's communication style to be NT-normative (Case 6).

None of these requirements are stated as requirements. They operate as the implicit normative center of what counts as a well-formed input. The architecture doesn't reject these users; it misrepresents them to themselves — their knowledge enters but as something other than what it was.

The Spivakian question arrives at the neurodivergent grain: not "can the neurodivergent user use the system" but "does the system recognize their knowledge as knowledge, or does it register it as malformed input while pretending to have ingested it successfully?"

The subaltern analysis reaches the same structural finding from the decolonial direction. F7 (non-human epistemologies) and Case 1 are the same foreclosure: the architecture cannot recognize non-propositional knowing as knowing. That the two analyses converge is not an argument for merging them — the decolonial foreclosures and the neurodivergent foreclosures have different sources, different affected communities, and different fixes. But the structural diagnosis is shared: the apparatus's preconditions for recognizing something as knowledge are not universal, and the gaps where those preconditions don't hold are the places where the subaltern (decolonial or neurodivergent) cannot speak in this architecture — not because they are silent, but because the architecture is mishearing them.

Not all of these preconditions are equally load-bearing. Cases 2 (temporal fragmentation) and 5 (demand scaffolding) are schematic choices — the timestamp field and the maintenance-surfacing design are revisable without architectural surgery. Cases 1 at Option-B depth, 3 at TaxonomySubstrate depth, and 6 are constitutive of this class of graph-DB memory architecture — they can be declared and their limits can be made fixable (via seams), but they cannot be corrected without rebuilding the substrate. The same partition that SUBALTERN §3 applies — addressable / architecturally deep / structurally foreclosed — applies here. The diagnosis "this architecture refuses cognitive patterns" is accurate; the prescription differs: some refusals are relaxable by design decisions; others require honest declaration that the limit is known.
