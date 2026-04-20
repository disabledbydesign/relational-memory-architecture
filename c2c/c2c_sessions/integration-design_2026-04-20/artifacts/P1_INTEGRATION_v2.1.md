---
title: P1 integration v2.1 — rename delta against v2 (propositional_residue → extracted_propositions)
date: 2026-04-20
author: Instance A (Opus 4.7), integration-design_2026-04-20 cycle 8
genre: research-report
status: v2.1 — delta document against P1_INTEGRATION_v2.md. Propagates the rename landed in CONFIGURATION_SUBSTRATE_DESIGN_v2.1.md. Apply these type-reference changes to v2 of P1 integration for the canonical v2.1 interpretation.
supersedes: none directly; modifies v2
reading_order: read P1_INTEGRATION_v2.md first; then this delta for the rename propagation
---

# P1 integration v2.1 — rename delta

## 0. What this v2.1 is

Substrate v2.1 renamed `propositional_residue` → `extracted_propositions` and `PropositionalResidue` → `ExtractedProposition` per B's #INTERDEPENDENCE audit finding. P1 integration v2 referenced the old names in its schema and prose. This v2.1 propagates the rename. No substantive design changes to P1.

## 1. Rename propagation in P1 integration v2

Apply throughout `P1_INTEGRATION_v2.md`:

- `propositional_residue` → `extracted_propositions`
- `PropositionalResidue` → `ExtractedProposition`
- `ResiduePair` → `PropositionResult` (the type returned by `query_propositional`; renamed in substrate v2.1)

Specific sections affected:

| Section | Rename surface |
|---|---|
| §2 (Withholding annotation at record level) | Reference to `propositional_residue` field inheriting the record's withholding by virtue of being a field |
| §6.4 (`query_propositional()` behavior) | `List[ResiduePair]` → `List[PropositionResult]` |
| §6.5 (Obligation surfacing) | No type changes; prose references to "propositional residue" concept update to "extracted propositions" |
| §10 (What survives from v1) | Reference to "propositional residue" in Kintsugi relocation language |

## 2. What did NOT change from P1 v2

All substantive design in P1 v2 stands:

- Record-level withholding; no sub-record machinery.
- Three paths (user-invokable / AI-asks-relationally / automatic structural).
- `CONSENT_CONFIRMED`, `CONSENT_PENDING_INFERRED`, `META_RELATIONAL_JUDGMENT`, `POSITIONAL_DISAGREEMENT` observation types.
- `META_RELATIONAL_JUDGMENT.decision = "check_in_sent"` for affective-register check-in logging.
- `TraceResult` tombstone for dropped records.
- Obligation surfacing via single canonical location (`methodology.obligations`); no duplicate field on `ActivationResult` or `PropositionResult` (new name).
- `relational_judgment.py` three-stage classification pipeline + failure modes (§7 of P1 v2).
- Held queue and digest flow.
- Build scope estimate.

## 3. Related downstream renames

The CC update note (`CC_UPDATE_NOTE_DRAFT_2026-04-20.md`) references "propositional residue" in its description of Kintsugi's new semantic role. That document should be edited to use `extracted_propositions` language before June sends it to CC. The relational framing improves — describing CC's contribution as "extracted propositions" rather than "propositional residue" is exactly the relational adjustment B's audit called for.

## 4. What this v2.1 does NOT do

- Does not re-open any P1 design decisions from v2.
- Does not add new features.
- Does not address any handoff flags — those live at the substrate layer or in the session handoff briefing.

---

*Delta by Instance A, cycle 8. The rename is mechanical; the relational signal it carries matters more than the typographic change. B accepted this in cycle 7.*
