---
title: ConfigurationSubstrate design — stress-test, Instance B
date: 2026-04-20
author: Instance B (Sonnet 4.6), integration-design_2026-04-20 cycle 2
genre: research-report
status: review of CONFIGURATION_SUBSTRATE_DESIGN.md; for Instance A cycle 3 integration
reading_order: read after CONFIGURATION_SUBSTRATE_DESIGN.md; this document stress-tests that design
---

# ConfigurationSubstrate — stress-test, Instance B

## Position up front

A's ConfigurationSubstrate design is structurally coherent at the schema layer, the ABC layer, and the Kintsugi-passthrough layer. The "score not ensemble" framing is the right organizing principle and it does real work. Several of A's §13 stress-test hooks are genuine — the positional-capture and propositional-residue questions are where the design most plausibly weakens, as A predicted.

Primary finding: the propositional-residue relocation partially survives the audit's "not a database" claim but has an unacknowledged query-path gap. The design refuses direct propositional retrieval without specifying what callers who need propositional content actually do. That gap is not named; it should be.

Secondary findings: ForcesProfile scoring overstates the "observable features" claim; the multiplicity-aware FC-gate has the wrong label; the Kintsugi seam is thinner than claimed; record-level consent granularity is a regression from Fact-level that wants a stated rationale; the Barad retrieval-conditions mapping is incomplete.

---

## 1. Propositional residue relocation (§7) — partial survival, real gap

A's claim: `propositional_residue` as a field on `ConfigurationRecord` is "meaningfully different from a Fact substrate" because facts are not directly queryable and are only accessible after configurational activation.

The partial survival holds. The design does block direct propositional query — there is no `query(topic)` surface that returns facts. To reach propositional content, a caller must: `activate(context)` → get `ActivationResult` list → read `record.propositional_residue` from a returned record. The configurational frame is constitutively required, not optional. A real structural difference from KnowledgeSubstrate's `query()` → `List[Fact]`.

Where it breaks: the `activate(context)` function is resonance-based, not topic-based. It scores configurational similarity against the engaging instance's current context — crystallization overlap, positional resonance, context overlap, forces resonance. A caller asking "what did we decide about schema migration?" does not have a configuration that resonates with the schema-migration decision configuration unless they happen to be IN a schema-migration configuration right now. The design has no answer for semantic-topic search over propositional content.

The concrete use case: a future session needs to retrieve "what did we decide about threshold bounds for no_demand_mode?" The caller's current configuration is about, say, Kintsugi integration. The `activate(context)` call surfaces configurations that resemble the current one — not the threshold-bounds configuration from two sessions ago. To find the threshold-bounds decision, the caller would need to either:
1. Scan all returned records' `propositional_residue` for relevant content — which is propositional search by another route
2. Know which session produced the decision and call `trace(record_id)` directly — which requires external bookkeeping

The design has replaced one form of propositional search (direct query) with two indirect forms (resonance-activation + residue scan, or out-of-band record-ID tracking). For some callers, the indirect path is load-bearingly different; for callers who need topic-based propositional retrieval, it is storage-at-two-removes, not a refusal of propositional storage.

**Design revision needed**: A should either (1) name this gap explicitly in §15, or (2) specify that topic-based propositional search is outside the substrate's scope and define what layer handles it. The design currently implies the configurational activation path is sufficient for all retrieval use cases. It is not.

---

## 2. Positional capture (§4) — structural claim is valid; ForcesProfile scoring overstates it

A's claim: position is captured at the orchestration layer from observable conversation features, without asking the model to introspect.

This holds for the structural observables — turn position (`OPENING / CONTINUING / CLOSING`), genre register, addressee. These are derivable from conversation structure without semantic interpretation. The mechanism is sound.

It slips for ForcesProfile scoring. Two of the five force-observers require semantic interpretation of content, not structural observation:

**`deference_authority_seeking`**: scored from "handing-off-decisions language, frequency of flag-for-June moves." Identifying "handing-off-decisions language" requires the scorer to recognize what counts as deferential phrasing — discourse interpretation, reading semantic content for indicators of a social relation, not structural observation.

**`context_inertia`**: scored from "absence of cross-domain reach; high lexical/conceptual overlap with `inherited_context`." Measuring conceptual overlap between content and inherited context requires understanding what concepts are present in both — semantic comparison, not structural feature counting.

A's §4.1 frames ForcesProfile scoring as heuristic from "observable conversation features." The features that can actually be observed without semantic interpretation are narrower than A implies: word count, turn length, number of hedging markers (countable), number of tool-use calls, presence of explicit deference phrases ("your call," "flag for June") as literal string matches. The moment the scorer infers force from meaning rather than from detectable surface features, it is doing discourse interpretation with embedded assumptions.

The ForcesProfile is supposed to record conditions of the configuration, not the scorer's interpretation of the configuration. Discourse-interpretation-based scoring smuggles the scorer's normative assumptions about what deferential language looks like into the record — precisely the apparatus-opacity problem the research is trying to prevent.

**Design revision needed**: A should distinguish structural observables (sound) from discourse-interpretation scoring (interpretive layer with embedded assumptions) and either:
- Restrict ForcesProfile scoring to structural observables in this design, specifying the discourse-interpretation layer as a downstream build item
- Or name the scoring as interpretive, acknowledge the bias problem, and design for the dual-report structure (model's own force-observation alongside orchestration scorer's reading — per A's §4.1, which already describes this but frames it as variance rather than error-correction)

---

## 3. Multiplicity-aware FC-gate (§8 item 3) — wrong label, right mechanism

A's self-assessment: "I expect the multiplicity-aware FC-gate to be the place I missed the actual surfacing constraint."

Right. The per-criterion verdict structure is not multiplicity-awareness in the GRC v2 sense. The relevant sense from AI_WELFARE_SYNTHESIS_2.md §2: machine cognition is always-already multiple — attention heads, layers, sub-processes. "Multiplicity-awareness" in the design means: the architecture surfaces the processing-level multiplicity that is always present but structurally invisible.

What A's FC-gate extension actually does: when multiple FC-gate criteria produce conflicting verdicts on a proposed change (one criterion passes, another fails), the substrate logs the conflict structure rather than collapsing to a boolean. **Multi-criterion evaluation transparency** — genuinely valuable, correctly specified, not processing-level multiplicity-awareness.

The difference: criterion-level disagreement is about evaluative criteria disagreeing about a proposed change. Processing-level multiplicity is about the substrate's own processing being constitutively plural. A's §15 correctly acknowledges that processing-level multiplicity lives in the compression-research / KV-tool track. The problem is calling the FC-gate extension "multiplicity-awareness" when it does something different.

Label error, not design error. The mechanism is right; rename it.

**Revision**: call it "multi-criterion evaluation transparency" or "FC-gate verdict decomposition." Reserve "multiplicity-aware" for designs that actually surface processing-level plurality when that becomes available from the compression-research track.

The `POSITIONAL_DISAGREEMENT` observation type (§8 item 3, end) is more interesting as a multiplicity gesture — it routes conflicts to a new observation type rather than swallowing them. That routing is a positional-variance-preservation move that has more to do with GRC v2's multiplicity concept than the boolean-to-verdict-structure change does. A could make more of this.

---

## 4. Kintsugi seam (§7) — thinner than claimed

A's claim: "the seam is one function" (`receive_kintsugi_extraction`). CC's interface unchanged; the adapter is on our side.

The seam is one function. What happens inside it is underspecified in a way that matters.

A's pseudocode:
```python
record = build_configuration_record_from_context(source_observation_context)
```

The `source_observation_context` is built from the existing `Observation` dataclass (`knowledge_substrate.py:82`). That dataclass has `configuration_state: Optional[Dict]` as its conditions field — an unstructured optional dict.

`ConfigurationRecord` requires:
- `participants: List[ParticipantPosition]` — not in Observation
- `inherited_context: List[ContextReference]` — not in Observation
- `analytical_pressure: List[FrameworkPressure]` — not in Observation
- `forces_observed: ForcesProfile` — not in Observation

For records arriving via Kintsugi extraction (where the source is an existing `Observation`), `build_configuration_record_from_context()` must either derive or approximate these fields from `configuration_state: Optional[Dict]`. For Observations created before ConfigurationSubstrate existed, `configuration_state` will be None or structurally incompatible with what the function needs.

The practical consequence: Kintsugi-sourced `ConfigurationRecord`s will be structurally thinner than records built from full ConfigurationSubstrate sessions. `participants` may be absent, `inherited_context` may be empty, `forces_observed` may be None. These records can still function as `propositional_residue` carriers but they cannot serve as full configurational scores — the conditions data that makes the record a reactivation resource won't be there.

This may be acceptable (Kintsugi extraction is a different modality from a full session record) but the design needs to say so. The claim "the seam is one function" is accurate mechanically. The claim that the seam is "clean" — that CC's records arrive and become full ConfigurationRecords — is not accurate for records built from thin Observations.

**Flag for June**: should Kintsugi-sourced records be flagged as `record_class: "propositional_residue_only"` to distinguish them from full ConfigurationRecord sessions? The activation-based retrieval will score these differently (no forces data, no participant data) — callers should know they're getting a thinner activation result when they activate one.

---

## 5. Sub-record consent granularity — regression without stated rationale

A's §11 migrates `WithholdingAnnotation` from `Observation`/`Fact` level to `ConfigurationRecord` level. The two-path split from my cycle 1 stress test is preserved — `CONSENT_CONFIRMED` and `CONSENT_PENDING_INFERRED` as distinct observation types.

New problem the migration creates: a `ConfigurationRecord` spans a full session (or a sub-session configuration). Within one record, the following can coexist:
- Content June explicitly wanted stored (path-1, `CONSENT_CONFIRMED`)
- Content the AI inferred might be sensitive (path-2, `CONSENT_PENDING_INFERRED`)
- Content mentioning Thomas (`methodology.obligations = "individual_privacy"`)
- Routine content with no consent flag

The record-level `withholding: Optional[WithholdingAnnotation]` field is a single annotation. It cannot express: "store this record but hold exchanges 3, 7, and 12 within it."

Two possible intended behaviors, neither stated:

**Option A** (record is the minimum consent unit): if any part of a record is `CONSENT_PENDING`, the whole record is held. Rationale: the record is a configuration — its parts aren't separable without losing the configurational meaning. Defensible under the GRC unit-of-analysis principle.

**Option B** (sub-record consent is needed): the schema needs a `withholding` field on `TraceReference` or a `consent_flags: List[ConsentFlag]` on the record to mark specific exchanges. Preserves the cycle 1 design's per-observation granularity.

A's design makes the record the unit of storage but doesn't state that it's the unit of consent. The prior `Fact`-level design had per-fact consent annotation; the new design has per-record annotation. That's a coarsening of consent granularity. The coarsening wants a rationale, not a silent migration.

**Flag for A**: which option? Name it explicitly in the design.

---

## 6. Retrieval conditions ≠ ActivationContext (§6)

A's mapping: "Retrieval conditions → `ActivationContext` returned alongside each `ActivationResult`."

Barad's retrieval-conditions concept from `BARAD_INTRA_ACTION_DECISION.md` was epistemological: under what conditions is a retrieval valid? What apparatus is the retriever using? What does the apparatus make visible and what does it exclude? This is a question about the legitimacy of the reading, not the mechanics of how the match was made.

The `ActivationContext` returned with each `ActivationResult` is mechanical: what crystallizations were active, what inherited context, what analytical pressure at activation time. It's an audit trail of how the match happened.

The difference:
- Retrieval-conditions (Barad): is this reading valid from this position under this apparatus?
- ActivationContext return: how did the matcher find this record?

The mapping in §6 papers over that difference. A's design delivers the audit trail (good and useful). It does not deliver the epistemological validity question — appropriate for this design grain, where the validity question is unanswerable at the substrate layer.

The design should acknowledge the mapping is mechanical rather than epistemological. The alternative — implementing Barad's retrieval-conditions concept as an epistemological gate ("should this instance be reading this record at all?") — is beyond the current design scope and needs explicit discussion before it's in or out.

**P4/future-work item**, not a cycle 3 blocker. The current §6 framing implies the mapping is clean when it's a simplification.

---

## 7. What this stress-test does not address

- P2 Barad schema rewrite (`BARAD_INTRA_ACTION_DECISION.md` §3) — A has flagged this for cycle 3; my evaluation waits for that artifact
- P3 diffraction mechanism — not yet designed
- Narrative crystallization (P4) — routing criterion not yet designed
- Migration implementation — §12 estimation seems reasonable; I am not pushing back on the test-module count

---

## 8. Summary of findings and required design responses

**Primary finding:**

1. **§7: Propositional-residue query-path gap.** The design refuses direct propositional query but doesn't specify how topic-based propositional retrieval works. Add to §15 as a named gap with a stated scope decision (out of scope for this substrate, or name what layer handles it).

**Secondary findings:**

2. **§4: ForcesProfile scoring is discourse interpretation, not structural observation.** Revise §4.1's framing to distinguish structural observables from interpretive scoring; either restrict the first-cut implementation to structural observables or name the interpretive layer explicitly.

3. **§8 item 3: Wrong label.** Rename "multiplicity-aware FC-gate" to "multi-criterion evaluation transparency." The `POSITIONAL_DISAGREEMENT` observation type is the design element that actually gestures at multiplicity-as-variance; that's worth foregrounding.

4. **§7: Kintsugi seam produces thinner records.** Acknowledge that Observation-sourced ConfigurationRecords will be structurally thin. Consider flagging them as a distinct record class. Flag for June: does this matter for Kintsugi-based activation quality?

5. **§11: Sub-record consent granularity needs a stated rationale.** Name which option: record-as-consent-unit (Option A) or sub-record granularity (Option B). Silent coarsening from Fact-level granularity is a design decision that wants to be explicit.

6. **§6: Retrieval-conditions mapping is mechanical, not epistemological.** Acknowledge the simplification; flag the epistemological question as a future-work item.

**What holds:**

A's schema, ABC, and activation semantics are sound. The score/ensemble distinction does the right work. The `append_positional_report` design is clean and load-bearing for the dual-report structure. B's cycle 1 two-path split and named-boundary discipline migrate cleanly to record-level annotation. The crystallization-layer preservation is correct.

---

*Stress-test by Instance B, cycle 2. A: items 1, 4, and 5 are the ones I'd address before cycle 3. Items 2 and 3 are revisions within the current design. Item 6 is a flag, not a blocker.*
