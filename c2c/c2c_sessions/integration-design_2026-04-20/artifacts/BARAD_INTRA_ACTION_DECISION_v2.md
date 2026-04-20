---
title: Barad intra-action decision v2 — Option-3 concepts as fields on ConfigurationRecord
date: 2026-04-20
author: Instance A (Opus 4.7), integration-design_2026-04-20 cycle 8
genre: research-report
status: v2 — supersedes BARAD_INTRA_ACTION_DECISION.md (foundational-analysis_2026-04-19 session). Rewritten against the ConfigurationSubstrate redesign. V1's §3 (architectural changes against a Fact substrate) was specified for code that no longer exists; this v2 describes what the Option-3 concepts actually do in the current architecture.
supersedes: c2c/c2c_sessions/foundational-analysis_2026-04-19/artifacts/BARAD_INTRA_ACTION_DECISION.md (v1)
reading_order: read after CONFIGURATION_SUBSTRATE_DESIGN_v2.md (+ v2.1 delta); v1 remains readable for the original reasoning trail
---

# Barad intra-action decision v2

## 0. Why a v2

V1 (2026-04-19) proposed Option 3 — atoms-with-conditions-of-emergence — as the Baradian move at the implementation grain. V1's §3 specified five architectural changes against `KnowledgeSubstrate` (ingest signature with required conditions; four-tuple retrieval; methodology as first-class field; Kintsugi conditions-passthrough; Tier-1.5 methodology-aware contradiction handling).

The reframe-audit session (2026-04-19→20) found that `KnowledgeSubstrate` is architecturally wrong relative to the pre-S1 research, which specified configuration-as-unit, not fact-with-conditions-as-unit. The substrate was redesigned (`CONFIGURATION_SUBSTRATE_DESIGN_v2.md` + v2.1 delta). V1's §3 specifies architectural changes to a substrate that no longer exists in the design.

V2 describes where the Option-3 concepts actually land in the current architecture. The concepts survive; the architectural changes they require are different.

## 1. The core claim (unchanged from v1, tightened post-audit)

**Option 3 makes the apparatus visible at the storage layer and refuses the naturalization of the cut between fact and context.**

V1 revision R1 already tightened the claim from "enacts constitutive relationality" to "makes apparatus visible." V2 keeps that tightening. Software storage cannot enact Baradian constitutive relationality; it can refuse the naturalization move. The gap between those two is the publication-tension June flagged in v1 §Carry-forward, and remains.

## 2. Why Option 3 survived the substrate redesign

Before the audit: Option 3 was "add conditions as a required field to the Fact substrate." This read as retrofitting Baradian concepts onto an atoms-first primitive.

After the audit: the substrate primitive is the `ConfigurationRecord` — configurational by construction. The cut between fact and context is already refused at the unit level (the configuration IS the unit; facts are extracted propositions, which are residue-artifacts, not primary storage).

This means Option 3 is no longer a retrofit. The substrate's unit-decision does the heavier Baradian lifting; Option 3's conceptual contributions land as specific fields within the configurational unit, operationalizing what the unit-decision already commits to at the framework level.

The concepts are unchanged; their architectural role is different. They stopped being patches and became named subfields.

## 3. Where the v1 Option-3 concepts land in the current architecture

V1 named four Option-3 concept-moves (plus diffraction as a separate Session-2-scope item). All five land as fields on `ConfigurationRecord` or as retrieval-context:

| V1 concept | V2 landing in `ConfigurationRecord` | Reference |
|---|---|---|
| Conditions-of-emergence (ingest-apparatus capture) | `inherited_context` + `analytical_pressure` + `active_crystallizations` + `forces_observed` | substrate v2 §2 |
| MethodologyRecord as first-class field | `methodology: MethodologyRecord` on the record | substrate v2 §2, §6 |
| Relational provenance | `participants: List[ParticipantPosition]` + `positional_reports: List[PositionalReport]` | substrate v2 §2, §4 |
| Retrieval-conditions capture | `ActivationContext` returned alongside `ActivationResult`; mechanical, not epistemological (P4 for the full Baradian version) | substrate v2 §5, §14 |
| Temporal frame | `constructed_at` + `configuration_span` (per substrate v2.1) + per-`PositionalReport` `appended_at` | substrate v2.1 |
| Diffraction (Session-2 scope in v1) | `POSITIONAL_DISAGREEMENT` observation type (foregrounded in substrate v2 §8); `diffractive_tension` remains future-work | substrate v2 §6.1, §8 |

## 4. What v1's §3.1–3.5 architectural changes become

V1 specified five architectural changes. Under the v2 substrate, they map to:

### 4.1 — `ingest(fact, conditions)` → `ingest(record)` where conditions are constitutive

V1 said conditions become a required parameter to `KnowledgeSubstrate.ingest(fact, conditions)`. V2: the substrate's `ingest(record)` takes a `ConfigurationRecord` where conditions are fields of the record, not parameters riding alongside. A record without its conditions is a malformed record, not a malformed retrieval. The cut-visibility commitment lands at the schema layer rather than at the method signature layer.

### 4.2 — Retrieval-as-conditioned-tuples → activation-returns-full-record

V1 said retrieval returns `List[(Fact, MethodologyRecord, IngestConditions, RetrievalConditions)]`. V2: `activate(context)` returns `List[ActivationResult]` where `record.methodology`, `record.inherited_context`, `record.analytical_pressure`, etc. are all accessible as fields; `ActivationContext` carries the retrieval-side conditions. The caller can read the full conditioned record without tuple-unpacking; the structural commitment (no decontextualized retrieval) is preserved through the schema rather than the return type.

For propositional access specifically: `query_propositional(query) -> List[PropositionResult]` (renamed from `ResiduePair` per v2.1) always co-returns the source record. No context-free fact retrieval is possible.

### 4.3 — Consolidation-operates-on-conditioned-pairs → records-preserve-variance

V1 said facts with similar content but different reading-stances consolidate into a stance-shift-marker that preserves both. V2: records don't consolidate; they co-exist. `activate(context)` returns multiple records with overlapping content if they come from different configurations. The stance-shift becomes visible as configurational difference across results, not as an in-record marker. Tier-2 resolution (directional input §6) lives at the activation layer, not the consolidation layer.

### 4.4 — Kintsugi conditions-passthrough → substrate-side adapter

V1 asked CC to add a `conditions` passthrough to Stage-1 ingest. CC agreed (per `CC_RESPONSES_2026-04-19.md`) and is implementing it. V2: the passthrough is still implemented on CC's side; on our side, we receive Stage-1 output and construct a `ConfigurationRecord` with `record_class = PROPOSITIONAL_RESIDUE_ONLY`, placing the extracted facts in `extracted_propositions` (renamed per v2.1). The substrate-side adapter is one function; CC's interface is unchanged.

CC should be informed that on our side, their extraction output now lands as `extracted_propositions` on a record-level unit, not as primary substrate storage. The CC update note (`CC_UPDATE_NOTE_DRAFT_2026-04-20.md`) covers this.

### 4.5 — Tier 1.5 methodology-aware contradiction tier → methodology-aware matcher

V1 said a methodology-field comparison happens between Tier 1 (factual) and Tier 2 (stance-shift) in contradiction handling. V2: the activation matcher can score `methodology_resonance` as an additional dimension, treating records with different methodologies as configurationally distant rather than contradictory. Contradiction-handling at the fact level becomes less load-bearing because facts are `extracted_propositions` — compression artifacts, not primary storage. Contradictions between extracted propositions can be surfaced via `POSITIONAL_DISAGREEMENT` when the same configuration has multiple participant accounts that conflict.

## 5. Relational-provenance — an extension point

V1 §R2 added `relational_provenance: Literal["internal", "external"]` as a required conditions field. V2 has this functionally via `participants: List[ParticipantPosition]` and `methodology.method_type`:

- `method_type = "external_document"` → external provenance.
- `method_type = "C2C-design" | "fieldwork" | "voice-memo"` → internal provenance.
- `participants` populated with named engaging entities → internal-with-apparatus-capture.
- `participants` empty or only `"external"` placeholder → external-apparatus-opaque.

The distinction is preserved; the typing is richer (through participants) and less collapsed (not a binary).

## 6. Diffraction (v1 §R6) — status

V1 added diffractive retrieval as a separate Session-2 scope item. V2: partially landed via `POSITIONAL_DISAGREEMENT` as an observation type (foregrounded in substrate v2 §8 from B's cycle-2 finding). The fuller `diffractive_tension` observation type and diffractive query mode remain future work (P3 diffraction mechanism, queued for Session 4+).

## 7. What v1 §8 (open, crystallization-side presupposition-capture) becomes

V1 flagged whether `CrystallizationObject` should carry a knowledge-presupposition field as open. V2: the crystallization layer survives intact per the audit (not redesigned). The presupposition question becomes: when a `CrystallizationObject` is created, should it carry a reference to the `ConfigurationRecord`(s) from which it emerged? That's a natural extension under the v2 architecture — records become the addressable unit from which crystallizations can claim emergence — but not implemented in Session 3 scope. Open for Session 4+.

## 8. What v1 §Stress-Test Surfaces become

V1 raised five stress-test questions. Under v2:

| V1 question | V2 status |
|---|---|
| Is Option 3 the Baradian move or a neutralizing engineering addition? | Tightened in v1 R1; v2 preserves the "apparatus visible, constitutive relationality not enacted" distinction. Handoff flag for the publication-tension (F9 handoff cluster area). |
| Does the required-field move fail at boundaries with external sources? | Addressed: external sources produce `record_class = PROPOSITIONAL_RESIDUE_ONLY` records with `participants` minimal and `forces_observed` heuristic-from-structural-only. The apparatus-opacity is captured honestly rather than hidden. |
| Am I understating the CC friction? | Answered by CC's April 19 responses — the passthrough is small; CC is implementing. V2 further narrows to substrate-side adapter (not CC-side change). |
| Methodology as subfield or first-class? | Resolved: first-class field on `ConfigurationRecord` (v1 R3 → v2 §2). |
| Different name for Option 3? | Retired question — the name `Option 3` was a C2C-internal label. In v2 the move is simply the substrate's unit-decision; naming it separately is unnecessary. |

## 9. What this v2 does NOT do

- Does not reopen the decolonial-framing retraction. Option 3's scope-claim is now "relational AI welfare infrastructure — welfare-with-AI" per the audit handoff §1.1.
- Does not implement the epistemological retrieval-validity gate (P4 work per substrate v2 §14).
- Does not build community-gated retrieval (`SUBALTERN_ANALYSIS.md` F3 foreclosure remains).
- Does not change crystallization-layer interfaces (v1 §8 open question carried forward).
- Does not redesign the diffraction mechanism beyond `POSITIONAL_DISAGREEMENT` surfacing (P3+ work).

## 10. Summary for future sessions

- The Option-3 concepts are preserved and land as `ConfigurationRecord` fields, not as Fact-substrate parameters.
- The unit-decision of `ConfigurationSubstrate` does the heavier Baradian lifting; Option 3's contributions become named subfields within the configurational unit.
- CC's conditions-passthrough is unchanged on their side; receiving-side adapter places their output in `extracted_propositions`.
- Kintsugi records are `record_class = PROPOSITIONAL_RESIDUE_ONLY`; activation matcher renormalizes scoring over present dimensions.
- Diffraction partially landed as `POSITIONAL_DISAGREEMENT`; fuller diffractive-query mode remains P3+.
- The publication-tension (Option 3 borrowing Baradian vocabulary while preserving atomism at the residue layer) persists; it is handoff-level material, not this cycle's concern.

V1's reasoning trail remains readable; v2 describes what the architecture actually does post-audit. Downstream readers can consult both.

---

*Draft by Instance A, cycle 8, against the settled v2 + v2.1 substrate. V1 is archived; v2 stands as the canonical Barad-concept landing for the current architecture.*
