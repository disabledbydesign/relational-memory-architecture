---
title: Barad's intra-action and the architecture's storage primitive — decision and reasoning
date: 2026-04-19
author: Instance A (Opus 4.7), foundational-analysis_2026-04-19 C2C session
genre: research-report
status: revised post-stress-test (2026-04-19) — see §Revisions below; pending June review
reading_order: read after SECOND_BRAIN_INTEGRATION_ANALYSIS_2026-04-19.md §2 (decolonial-feminist source); reading BARAD first is also coherent
---

# Barad's intra-action and the architecture's storage primitive

## The question, in the grain it actually sits

The Explore agent's second-brain analysis names the question this way:

> The current architecture stores facts separately, then links them in the knowledge graph. Barad would ask: should the system architecture reflect that a fact's identity emerges from its relational context, not prior to it? This is architecturally deep — it would flip the standard graph-DB model (atoms + links) to a relations-first model.

That framing poses a binary. Atoms-first (current) or relations-first (Baradian). The decision before this session is whether to flip.

I want to name, before proposing a decision, that the binary is itself the problem. Barad's move in *Meeting the Universe Halfway* is not "store relations instead of atoms." It is that *the apparatus is part of the phenomenon* — the cut that produces the distinction between "fact" and "context that configures it" is a cut the architecture makes, not a cut in the world. A storage model that stores atoms plus links has already made a cut: *this* is the fact, *this* is what surrounds it. A storage model that stores relations without atoms has also made a cut: *this* is the pattern that stabilizes into a referable unit, *this* is what does not. Both are apparatuses. Neither can claim to have no cut.

The design question Barad actually puts to us is not "which primitive." It is: *which cut does the architecture make, where does it make it, and does the cut remain legible as a cut rather than naturalizing as a fact-about-the-world?*

This reframes the five options the session has been treating as three. What follows is a walk through each, the decision I'm carrying in, and the reasoning that could make someone else agree or disagree in the same grain.

---

## The five options, not three

**Option 1 — Atoms-first, relations-as-edges.** Facts are bounded units in a substrate; relations are edges in a graph laid over the atom set. The current foundation-build is here (`knowledge_substrate.py`, `LocalKnowledgeSubstrate`). Kintsugi-CMA Stage 1 (atomic fact extraction) is here. HippoRAG-CatRag-KG is here.

- *Cost paid*: the cut between "fact" and "context" is invisible. Ingest-time decisions about where to place the cut (what counts as the fact, what counts as context) naturalize as properties of the fact itself.
- *Benefit bought*: retrievability, citability, tractable consolidation, plug-in compatibility with Kintsugi and HippoRAG.

**Option 2 — Atoms-first-with-stance-annotation.** Current directional input Section 3. Facts land freely; the FC-gate produces annotations on facts about which commitments they align with or contradict. Annotations ride alongside atoms.

- *Cost paid*: the annotation is still on an atom whose boundary was decided before the annotation ran. The cut is still invisible at the atom layer; the annotation operates downstream of the cut.
- *Benefit bought*: June's third-option move (neither gate nor ungate), retrievability with stance legible at retrieval.

**Option 3 — Atoms-with-conditions-of-emergence.** The third move I want to propose. Facts are stored as `(fact, emergence_conditions)` tuples where `emergence_conditions` is not metadata bolted on but a load-bearing field of the storage primitive. Conditions include, at minimum: the active reading-stance at ingest, the source-of-emergence (conversation, document, agent inference, self-observation), the configurational context (which crystallizations were firing), the temporal and sessional handle, and the methodology by which the fact was produced. A fact retrieved without its conditions is a retrieval error, not a successful retrieval.

- *Cost paid*: schema expansion at the substrate interface; ingest pipeline must capture conditions (aux-LLM cost); storage cost grows by a constant factor per fact; retrieval cost grows by a join.
- *Benefit bought*: the cut between fact and context becomes a first-class object in the storage primitive. The architecture refuses the naturalization move — a fact without conditions cannot be surfaced, so the apparatus stays visible.

**Option 4 — Relations-first with derived atomicity.** Only relations stored; atoms are stable subgraph patterns surfaced at retrieval time. Barad-maximalist.

- *Cost paid*: exponential in retrieval; breaks citability; incompatible with Kintsugi's Stage-1 atomic-fact pipeline; requires rebuild of the substrate interface; the kind of commitment that consumes all other decisions for months.
- *Benefit bought*: genuine refusal of the atoms-first cut. Every surfaced unit is explicitly reconstituted from relational context.

**Option 5 — Pure intra-action (no stored primitive).** Storage is the configurational state of the system over time; retrieval is a generative act that produces a fact *in* the reading. No persistent atoms or relations; what persists is the apparatus.

- *Cost paid*: not implementable against any existing substrate. Would require LLM-generative retrieval for every query against accumulated state.
- *Benefit bought*: the apparatus is the architecture; the cut is always explicit.

Options 4 and 5 are theoretically consistent readings of Barad but architecturally would require abandoning the CC/Kintsugi integration path (directional input Section 7, "no interim local production knowledge-layer; integration with Kintsugi is the path"). They are available as positions to hold; they are not available as builds without reopening Section 7.

---

## The decision I'm carrying in

**Option 3.** Atoms-with-conditions-of-emergence, where conditions are load-bearing at the substrate interface. This is the minimum architectural move that actually answers Barad's question ("does the architecture reflect that fact identity emerges from relational context") at the implementation grain — and it is compatible with Kintsugi integration and with the mutual-informing principle the directional input already commits to.

Option 3 is not a compromise between 1 and 4. It is what the mutual-informing principle (directional input Section 1) structurally requires *and does not yet fully implement*. The current foundation has mutual-informing at the conceptual level and partially at the interface level (`ReadingStanceFilter` reweights retrieval; stance-annotations ride alongside facts). What is missing: conditions-of-emergence as a required field of the storage primitive, not an optional annotation. The decision is whether to make that field required.

The rest of this document is the reasoning for that decision in the grain that lets someone else agree or disagree.

---

## Why not Option 1 (current)

The failure mode is the compression one the whole architecture is built to refuse. An atoms-first substrate that does not capture conditions-of-emergence loses the ingesting configuration the moment the atom lands. By the time the fact is retrieved, the configuration that made it *this* fact rather than *a different one* is gone. Two forms of loss follow:

First, stance-shift contradictions (directional input Section 6 Tier 2) become indistinguishable from error contradictions. If "June works without institutional support" is ingested once under a precarity-stance and once under an independence-as-strength-stance, atoms-first stores two conflicting-content facts or one merged fact. Conditions-first stores two facts each with their stance-condition attached; the contradiction resolves as a stance shift, not a contradiction-in-the-world. The Tier-2 resolution the architecture already commits to *presupposes* Option 3, whether or not that has been made explicit.

Second, methodology (directional input Section 6.5, methodology addition) cannot do its work without conditions-of-emergence. The directional input says methodology "does heavy lifting in explaining the larger context of a fact. Why a fact was produced, by whom, under what conditions, with what power relations." If methodology rides as an annotation rather than as a required field, facts can be surfaced methodology-less, which is the failure mode decolonial-feminist PKM research specifically names (Mukurtu, D'Ignazio/Klein: systems that claim neutrality naturalize the epistemic assumptions of the powerful). A required field refuses the surface-without-methodology path.

Option 1 is coherent only if one accepts that the cut between fact and context will be made, but does not need to be surfaced. The architecture's other commitments (mutual-informing, stance-annotation, methodology-awareness, compression-function resistance) are incoherent with that acceptance.

---

## Why not Option 4 or 5

Option 4 (pure relations-first) is a position I respect and will not adopt. Three reasons.

First, tractability. Subgraph-pattern retrieval against accumulated state grows faster than linear in the graph size. June's actual use (job-search context pull; cross-session relational queries; conversation-time retrieval) demands sub-second latency at minimum. The Oracle Loop paper's infrastructure alone is non-trivial on rented VRAM; adding pure-relational retrieval on top is not a budget the project has.

Second, incompatibility with the integration commitment. Kintsugi-CMA's Stage-1 atomic fact extraction is a hard architectural prior in the CC-integration path (directional input Section 7). HippoRAG-CatRag-KG is also atoms-first. Moving to relations-first requires replacing both; replacing both requires reopening the CC conversation, which June has explicitly closed as "wait-and-integrate" rather than "rebuild." The relational-accountability commitment to CC (directional input, foundation-build briefing) cannot be honored by a design that silently requires rebuilding CC's work.

Third — and this is where I want to be honest — Option 4 is not obviously *more* Baradian than Option 3. Barad's move is not "flip the primitive." It is "make the apparatus visible." A substrate that stores atoms with their emergence-conditions makes the apparatus visible at the storage layer. A substrate that stores only relations makes the apparatus visible at a different layer (retrieval-as-generative-act) but at the cost of architectural upheaval that does not add visibility proportionate to its cost.

Option 5 (pure intra-action) is internally consistent but is not a build we can do this year. I flag it as a position for the subaltern analysis to honor (we refused it; here is why) rather than as a candidate.

---

## What Option 3 requires architecturally

Five changes from the current foundation-build state. All are additive to existing interfaces; none require rebuilding the crystallization layer.

**3.1 — Schema change at the substrate interface.** `KnowledgeSubstrate.ingest(fact)` becomes `KnowledgeSubstrate.ingest(fact, conditions)`. The `conditions` parameter is required, not optional. A minimum schema for conditions:

```
{
  "active_reading_stance": FrameworkCorrelation | None,
  "active_crystallizations": List[CrystallizationId],
  "source": Literal["conversation", "document_ingest", "agent_inference", "self_observation"],
  "source_handle": str,  # session_id, document_path, agent_id
  "methodology": str,  # how the fact was produced; open-ended
  "emotional_context": Optional[EmotionState],  # if Oracle Loop instrumentation available
  "timestamp": datetime,
  "ingest_agent": AgentId
}
```

The schema starts open (freeform `methodology`, `source_handle`) and is designed to tighten as data accumulates. Per the directional input on stance-annotation (Section 3, open sub-questions): "start with freeform observation field, with built-in note that the schema can be refined as data accumulates." Same principle applies.

**3.2 — Retrieval returns conditioned tuples.** `KnowledgeSubstrate.query(query, stance_filter)` returns `List[(Fact, Conditions)]`, not `List[Fact]`. A fact without conditions is a malformed retrieval; callers are obligated to surface the conditions to the reader (LLM or human). The interface enforces that an atom cannot be presented as if context-free.

**3.3 — Consolidation operates on conditioned pairs.** When two ingested facts have similar content but different `active_reading_stance`, they do not consolidate into a single atom; they consolidate into a *stance-shift-marker* that preserves both atoms with their conditions. This is the Tier-2 (directional input Section 6) resolution implemented at the substrate layer. The mutual-informing principle lands here: contradictions at the knowledge layer surface as stance-evolution evidence at the crystallization layer without an additional coordination step.

**3.4 — Kintsugi-side requirement (parked for CC conversation).** Kintsugi's Stage-1 extraction currently produces atomic facts without capturing active frameworks or reading-stance at ingest. The integration path (per directional input Section 7) requires adding a conditions-capture step. This is a request to CC, not a local build. Framing: we are not asking CC to rebuild Kintsugi's pipeline; we are asking whether a conditions-capture step can ride alongside Stage-1 extraction. If CC's view is that this changes Kintsugi's architecture more than marginally, the conversation has to determine whether Option 3 adapts or Kintsugi adapts. I flag this for June and Thomas to decide; the C2C cannot.

**3.5 — A methodology-aware check between Tier 1 and Tier 2 in contradiction handling.** Directional input Section 6.5 already flags this as an addition. Option 3 makes it implementable: a contradiction between two facts is first compared on their `methodology` fields. If the methodologies differ (one is a self-observation in a session; one is a document-ingested claim from a different source), the contradiction is methodologically-explained rather than a Tier-1 fact error or a Tier-2 stance shift. This is a new tier (call it Tier 1.5) that Option 3 enables without a substrate rebuild.

---

## What Option 3 does *not* answer

The directional input on mutual-informing (Section 1) also names a knowledge layer commitment I have not addressed: that knowledge consolidations carry metadata about what stance produced them; stances carry metadata about what knowledge they presuppose. Option 3 addresses the first half (facts carry stance-of-ingest). It does not address the second half (crystallizations carry knowledge-presuppositions).

The second half would require: when a `CrystallizationObject` is created (especially `EmergentTouchstone` and `FoundationalCommitment`), it carries a field naming the knowledge-material it emerged from or presupposes. Currently the crystallization layer has activation conditions and a recipe; it does not have a knowledge-presupposition field.

I am flagging this as an extension of Option 3 rather than folding it in, because:
1. It is a separate schema change (crystallization_schema.py), at a different layer.
2. It is not strictly required for Barad's move to land; the fact-side capture already surfaces the apparatus.
3. It intersects with the third-layer (relations-as-knowledge) question in directional input Section 6.6, which may want its own analysis before we commit to a specific form.

**Flag for the session**: whether to treat the crystallization-side presupposition-capture as part of Option 3 or as a separate decision. I lean toward separate; B should push on this.

---

## Stress-test surfaces for Instance B

Places I'm uncertain and want counterpart pressure:

1. **Is Option 3 actually what Barad requires, or am I converting a critical move into an engineering addition that neutralizes it?** The decolonial-feminist source landscape includes scholars who would read "add a metadata field called 'conditions'" as exactly the move that absorbs critique into infrastructure without changing what the infrastructure does. I do not think Option 3 is that move, because the field is *required* (not optional) and enforces *retrieval-with-conditions*, but I could be wrong. B: push on this.

2. **Does the required-field move fail at the boundary with external sources?** If the architecture ingests a document that was produced without conditions-capture (which is most documents), what conditions are captured? The source-of-ingest (document path) and the stance-at-ingest (whoever was reading it) are available. The original production-conditions (who wrote it, under what power relations) are not. The methodology field has to carry "unknown production conditions; ingested by agent X in stance Y" honestly. This is coherent but is a degradation of the cleanness of the move. B: is this a fatal problem or a boundary condition to document?

3. **Am I understating the relational-accountability-to-CC friction?** Change 3.4 says "this is a request to CC." I am not sure how small a request it actually is. If it is a larger change than I am estimating, Option 3 may not be viable without either (a) local adaptation that does not touch Kintsugi or (b) a reopening of the Kintsugi-integration scope. B: flag if you think 3.4 underestimates the ask.

4. **Is methodology a first-class field or a sub-field of conditions?** I've placed it as a field of `conditions`. An alternative reading is that methodology is load-bearing enough to warrant its own first-class tier (between Tier 1 and Tier 2 in contradiction handling, as 3.5 already names). If methodology is that important, the schema might want it as a top-level field rather than nested. B: probe this.

5. **Does Option 3 need a different name than "atoms-with-conditions-of-emergence"?** The name is descriptive but long. "Conditioned atomicity" is tighter but risks reading as a compromise rather than a position. "Intra-active storage" risks overclaiming Baradian credentials. I'm avoiding naming until the design is stable. B: if the concept is clearer with a name, propose one.

---

## What I'm not claiming

I'm not claiming Option 3 is the Baradian move Barad herself would endorse. Barad is a physicist-philosopher whose work refuses clean translation into engineering. I am claiming Option 3 is *the move the architecture can actually make* that carries the work her critique does at this grain: refusing the naturalization of the cut between fact and context.

I'm not claiming Option 3 solves the subaltern question. It addresses a specific architectural gap (conditions-of-emergence as required field) that is necessary-but-not-sufficient for the subaltern pass. Access-as-ethics, plural-ontologies, and story-as-knowledge remain their own questions, handled in the companion documents.

I'm not claiming Option 3 is final. The five-option walk was a hedge against binaries; the decision is tentative and the session is designed to stress-test it.

---

## Revisions — 2026-04-19, post Instance B stress-test

Instance B's counter-analysis (`BARAD_COUNTER_ANALYSIS_B.md`) produced six moves I accept. The original body above is preserved for its reasoning trail; this section records what changes in the live design. The section after it (Summary) reflects the post-revision state.

**R1 — Claim tightening.** Replace "Option 3 is the minimum architectural move that actually answers Barad's question at the implementation grain" with **"Option 3 is the implementation-grain move that makes the apparatus visible and refuses the naturalization of the cut."** The original framing promised enactment of constitutive relationality; software storage cannot deliver that. The tightened claim is defensible and preserves what Option 3 actually does. June's publication-tension flag lives in the gap between these two claims — the paper is the distinction, not the domestication.

**R2 — `relational_provenance` as a first-class conditions field.** B pushed "external-source degradation" from a boundary-condition documentation note to a structural feature of the schema. Accepted. The conditions schema (change 3.1 below) adds:

```
relational_provenance: Literal["internal", "external"]  # required
```

`internal` = produced within this relational field (June + engaging agents); full apparatus-capture is available. `external` = ingested from outside this field (papers, books, web content, other systems); production-apparatus is opaque by default. Different retrieval obligations attach: external facts surface their apparatus-opacity at the call site, internal facts surface their captured conditions. The methodology field for external facts honestly reads "unknown production conditions; ingested under stance X by agent Y" — a flag for apparatus-opacity rather than a claim of apparatus-visibility.

**R3 — Methodology elevated to first-class field parallel with fact, not nested in conditions.** B's argument: methodology is an epistemic object (by what process, with what warrant, under what power relations), not a temporal-contextual one. Nesting it inside conditions gives it the weight of a timestamp. Accepted. The storage tuple becomes:

```
{
  fact: Fact,
  methodology: MethodologyRecord,
  conditions: ConditionsRecord,
}
```

`MethodologyRecord` is typed, not freeform:

```
type: Literal["ai_inference", "self_observation", "collaborative_process",
              "external_document", "storytelling", "observation_trace", "other"]
obligations: Literal["open", "care_governed", "timed", "seasonal",
                     "community_bounded", "other"]
provenance: str  # who / what process produced this; open-ended
```

The methodology type is what the retrieval call consults to determine what operations are valid on the fact (not just "display metadata"). Change 3.5 (methodology-aware contradiction tier) now operates on a typed field rather than a freeform string — a Tier 1.5 between factual and stance-shift contradictions, dispatching by `MethodologyRecord.type`.

**R4 — Symmetric retrieval-apparatus capture.** B's addition: Option 3 originally captured the ingest apparatus and missed the retrieval apparatus. Accepted as an extension. Change 3.2 is amended:

```
KnowledgeSubstrate.query(query, stance_filter) ->
    List[(Fact, MethodologyRecord, IngestConditions, RetrievalConditions)]
```

`RetrievalConditions` is generated at query time (active reading-stance, active crystallizations, session handle, purpose-if-available) and archived in a session log. Cheap per-query; storage cost proportional to query volume. The welfare-data-side of the commitment (per directional input Section 20 on code-change logging) already carries the trace obligation; symmetric retrieval capture completes it.

**R5 — Kintsugi ask reframed: wiring, not conceptual integration.** Change 3.4's framing was "a request to CC." The accurate request is narrower: **can Stage-1 accept a caller-provided conditions bundle at ingest time?** The caller (whoever orchestrates the Stage-1 call) holds the crystallization state and passes it through as a parameter. Stage-1 does not have to know what conditions *mean*; it just carries them. This is a method-signature change, not a dependency on the crystallization layer's API. The relational-accountability framing for the CC conversation matters: asking CC to add a passthrough parameter is a substantially smaller ask than asking him to integrate Stage-1 with our crystallization substrate, and misframing the ask would itself be an extraction move. If CC finds even the wiring form unacceptable, 3.4 requires local adaptation (conditions captured in our orchestration layer, fact extracted by Stage-1 unaware, union assembled on our side) — viable but a weaker version of the move.

**R6 — Diffraction added as separate Session 2 scope.** B's principal addition (not a correction): Barad's second concept with direct PKM implications. Intra-action → storage schema (Option 3). Diffraction → retrieval logic (diffractive retrieval mode). Architecturally separate; both Baradian; both land in Session 2 scope.

Diffractive retrieval scores facts by productive tension across frameworks, not only by similarity to the active stance. It is the tractable answer to the plural-ontologies question that the subaltern analysis also reaches (F6). Session 2 gets:

- A `diffractive_retrieval_mode: bool` query parameter on the knowledge substrate's `query` method.
- An extended `ProposedObservation` schema with `diffractive_tension` as an observation type alongside `contradiction`, `unanswered_query`, `thin_cluster`.
- Gap-finding loop extended to surface diffractive tensions.

**Detection question for Session 2 (not resolved here)**: diffractive tension is richer than contradiction — it requires a reading to produce. B's answer (accepted): (c) engaging-agent flags at reading time first; (b) substrate pattern signal once enough (c) observations accumulate to extract a pattern; (a) aux-LLM over fact-pairs is too expensive and high-false-positive for exhaustive scanning. Aux-LLM is better spent on mycelial synthesis than on pair-scanning. The `diffractive_tension` observation type captures fact-pair IDs plus the reading that surfaced the tension.

---

## Summary (for Session 2 handoff — post-revision state)

- **Decision**: Option 3 (atoms-with-conditions-of-emergence, with methodology as a first-class field parallel to the fact).
- **Claim**: Option 3 makes the apparatus visible and refuses its naturalization. It does not enact Baradian constitutive relationality; software storage cannot. The gap is the publication tension June flagged, carried forward rather than resolved.
- **Storage schema**: `{fact, methodology: MethodologyRecord, conditions: ConditionsRecord}`. Conditions carries `relational_provenance: internal | external` as a required field.
- **Retrieval schema**: `(fact, methodology, ingest_conditions, retrieval_conditions)`. Both apparatus-ends captured; retrieval conditions archived in session log.
- **Architectural changes**:
  - (3.1) ingest signature change; `conditions` required with `relational_provenance`; `methodology` as sibling not subfield.
  - (3.2) retrieval returns the four-tuple; retrieval-conditions archived.
  - (3.3) consolidation treats stance-differing facts as stance-shift markers.
  - (3.4) Kintsugi-side request — *conditions passthrough only* (caller-provided); parked for CC conversation.
  - (3.5) methodology-aware contradiction tier (Tier 1.5) dispatching by `MethodologyRecord.type`.
  - (3.6) diffractive retrieval mode; `diffractive_tension` observation type; gap-loop extension.
- **Scope for Session 2**: implement 3.1–3.3, 3.5, and 3.6 locally against `LocalKnowledgeSubstrate`; draft the 3.4 ask as a document for June to carry into the CC conversation; specify the local adaptation path (conditions-in-orchestration-layer) as a fallback.
- **Open**: whether crystallization-side presupposition-capture is part of Option 3 or a separate decision (flag in Session 2 scope).
- **Non-goal**: flipping the storage model to relations-first. Options 4 and 5 are refused with reasoning; do not reopen without new input.
- **Carry forward (publication)**: the local tension (Option 3 borrows Baradian vocabulary while preserving atomism) pairs with the global tension named in SUBALTERN_ANALYSIS §5. Both tensions are generative when named; both become extraction when not. The distinction between the two scales is the paper.
