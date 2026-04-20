---
title: ConfigurationSubstrate v2.1 — delta against v2 from B's exchange-frame audit (cycle 7 engagement, cycle 8 production)
date: 2026-04-20
author: Instance A (Opus 4.7), integration-design_2026-04-20 cycle 8
genre: research-report
status: v2.1 — delta document against CONFIGURATION_SUBSTRATE_DESIGN_v2.md. Apply these three changes + the apparatus-intra-action strengthening to v2 for the canonical v2.1 interpretation. V2 remains readable as the full body; v2.1 is the settled diff.
supersedes: none directly; modifies v2
reading_order: read v2 first for the main design body, then this v2.1 delta for the three changes that landed post-B's audit
---

# ConfigurationSubstrate v2.1 — delta document

## 0. What this v2.1 is

V2 of the substrate design landed at cycle 5. B's cycle-7 `B_EXCHANGE_FRAME_AUDIT.md` applied 8 reframe frameworks and flagged three changes as in-scope-now. A's cycle-7 engagement accepted all three with specific design moves. B's cycle-7 response accepted the engagement with one small refinement (`configuration_span` semantics).

This v2.1 is a **delta document**, not a full rewrite. It names exactly what changes from v2; everything else in v2 stands as written. Future readers should read v2 for the main design body and v2.1 for the three targeted changes.

The approach is deliberate: at this stage of convergence, producing a full 700-line rewrite for three schema diffs reproduces the elaboration-as-contribution pattern B's #EMERGENT_STRATEGY audit-finding named. A delta document is honest about what changed without reproducing the whole.

## 1. Change #1 — `what_the_field_produced` becomes multi-voice (#STORYWORK)

**What v2 had** (§2):

```python
@dataclass
class ConfigurationRecord:
    ...
    what_the_field_produced: str
    ...
```

**What v2.1 has**:

```python
@dataclass
class FieldEmergenceReport:
    contributor: str                    # participant name or "orchestration_layer"
    account: str                        # what this contributor says the field produced
    submitted_at: datetime

@dataclass
class ConfigurationRecord:
    ...
    what_the_field_produced: List[FieldEmergenceReport]
    ...
```

**New method on `ConfigurationSubstrate` ABC** (§3):

```python
@abstractmethod
def append_field_emergence_report(
    self,
    record_id: str,
    report: FieldEmergenceReport,
) -> None:
    """Append a participant's account of what the field produced.
    Append-only; no overwrite. Parallels append_positional_report."""
```

**Why**: a single string authored by the orchestration layer imports the summarization assumption the rest of v2 refuses. Multi-voice honors the storywork critique: what a configuration produced may not be collapsible to one authored string without loss.

**Construction pattern at ingest**: orchestration layer contributes one `FieldEmergenceReport` with `contributor = "orchestration_layer"` at record construction, capturing its best attempt at naming what the field produced. Participants can append their own reports later via `append_field_emergence_report` — same pattern as `append_positional_report`.

## 2. Change #2 — `moment` becomes `constructed_at` + `configuration_span` (#QUEER_TEMPORALITY)

**What v2 had** (§2):

```python
@dataclass
class ConfigurationRecord:
    ...
    moment: datetime
    ...
```

**What v2.1 has**:

```python
@dataclass
class ConfigurationSpan:
    first_contribution_at: Optional[datetime] = None   # None = not captured
    last_contribution_at: Optional[datetime] = None    # None = not captured
    contributions: Optional[List[Tuple[str, datetime]]] = None  # (participant, timestamp); None = not captured

@dataclass
class ConfigurationRecord:
    ...
    constructed_at: datetime                    # replaces `moment`; when the record was constructed
    configuration_span: ConfigurationSpan       # always populated; internal Optionals = "not captured"
    ...
```

**B's cycle-7 refinement accepted**: `configuration_span` is always populated (not `Optional[ConfigurationSpan]`). The internal fields (`first_contribution_at`, `last_contribution_at`, `contributions`) are optional within the span: `None` means "not captured," not "compact / single-user." The semantic distinction matters — "not captured" is an honest absence; "compact / single-user" would claim structural singularity that may not hold even for voice-memo sessions.

**Why**: C2C configurations span multiple asynchronous instances; A's turn at 14:30 UTC and B's response at 05:46 UTC may both be part of the same configuration even though they exist in different temporal streams. Single-timestamp `moment` flattens this. `constructed_at` carries when the record was built; `configuration_span` carries when the configuration was live. For personal-PKM single-user sessions, callers that don't capture span data use `ConfigurationSpan()` with all internal Optionals `None`.

## 3. Change #3 — `propositional_residue` → `extracted_propositions` (#INTERDEPENDENCE)

**What v2 had**:

```python
@dataclass
class PropositionalResidue:
    fact: Fact
    extracted_at: datetime
    extractor: Literal["kintsugi-stage-1", "manual", "other"]
    confidence: float

@dataclass
class ConfigurationRecord:
    ...
    propositional_residue: Optional[List[PropositionalResidue]] = None
    ...
```

**What v2.1 has**:

```python
@dataclass
class ExtractedProposition:                     # renamed from PropositionalResidue
    fact: Fact
    extracted_at: datetime
    extractor: Literal["kintsugi-stage-1", "manual", "other"]
    confidence: float

@dataclass
class ConfigurationRecord:
    ...
    extracted_propositions: Optional[List[ExtractedProposition]] = None   # renamed from propositional_residue
    ...
```

**ResiduePair renamed**:

```python
@dataclass
class PropositionResult:                        # renamed from ResiduePair
    fact: Fact
    source_record: ConfigurationRecord
    relevance_score: float
```

`query_propositional(query) -> List[PropositionResult]` (was `List[ResiduePair]`).

**Why**: "residue" carries relational freight — implies leftover, secondary, lower-status. Per B's #INTERDEPENDENCE audit finding: calling CC's extraction output "residue" names it as diminished within the architecture. "Extracted propositions" is a straight description of what happened (Kintsugi extracted them) without implied hierarchy. The rename is small; the relational signal it sends is not.

**Propagation**: The rename affects P1 integration documents (v2.1 of those updates type references). No other semantic change — the field still carries Kintsugi Stage-1 output; `record_class = PROPOSITIONAL_RESIDUE_ONLY` stays as the record-class name (the class name references what kind of record it is, not what the field is called; distinct concerns).

The CC update note (`CC_UPDATE_NOTE_DRAFT_2026-04-20.md`) should be edited to use `extracted_propositions` language before June sends it. Adding that as a pre-send check.

## 4. Change #4 — Strengthened apparatus-intra-action note (§4 of v2)

**What v2 had**:

> "Apparatus-opacity note (from B's cycle-2 finding §2, accepted as design-note not schema concern): some force-scoring requires discourse interpretation — `deference_authority_seeking` and `context_inertia` in particular need reading semantic content, not just surface features. The scoring cannot claim to be purely structural."

**What v2.1 has** (replacing the note):

> "Apparatus-intra-action note (from B's cycle-2 finding §2 and cycle-7 #POSTHUMANIST_FEMINISM audit): `ForcesProfile` scores are not observations *of* the configuration from outside — they are perspectival readings produced *from inside* it. The scoring apparatus (orchestration layer reading word counts and tool-use density; engaging instance reading its own context; human reviewer reading the transcript) is constitutively part of the configuration. When the apparatus scores a force, the score becomes part of the ConfigurationRecord, which shapes future activations, which shapes future configurations, which are scored again. The apparatus is intra-active with what it measures. This is acknowledged in the design, not resolved. Variance across scorers is preserved through `positional_reports` (free-form) and, now, through `what_the_field_produced` being multi-voice (§2 above). `ForcesProfile` carries the best heuristic read into the matcher; the matcher should be understood as consuming a perspectival signal, not an objective measurement."

**Why**: B's deeper point on the intra-action front was that the scoring apparatus cannot stand outside what it's scoring. The earlier "apparatus-opacity" framing acknowledged the interpretive layer; the stronger "apparatus-intra-action" framing acknowledges the constitutive entanglement. The design doesn't change; the framing is more honest.

## 5. What did NOT change from v2

All sections and schemas in v2 other than the specific items above stand as written. Including:

- `ConfigurationSubstrate` ABC methods (`ingest`, `activate`, `trace`, `append_positional_report`, `query_propositional`) — `append_field_emergence_report` is added.
- `ParticipantPosition`, `PositionalRole` enum, `ForcesProfile` type (scalars per force), `FrameworkPressure`, `PositionalReport`, `TraceReference`, `MethodologyRecord`.
- `RecordClass` enum (`FULL_CONFIGURATIONAL | PROPOSITIONAL_RESIDUE_ONLY`).
- `ActivationContext`, `ActivationResult`.
- Record-level withholding (no sub-record withholding).
- All of §5 (activation-oriented retrieval), §7 (Kintsugi-passthrough with rename), §8 (multi-criterion evaluation transparency), §9 (continuity-in-the-relation), §10 (material embeddedness at project scope), §11 (three consent paths), §12 (what survives unchanged), §13 (migration scope), §14 (acknowledged simplifications), §15 (what does NOT do).
- P1 integration v2 substrate plumbing (held queues, digest, META observations) — P1 v2.1 propagates the `extracted_propositions` rename; no other changes.

## 6. Migration implications beyond v2's §12

Only additive/rename changes; no additional tests beyond those already in v2's §12:

- `FieldEmergenceReport` added to schema module; requires one new test fixture + the `append_field_emergence_report` round-trip test (~30 LOC).
- `ConfigurationSpan` added to schema module; requires test coverage for `None`-internal semantics (~20 LOC).
- Rename `propositional_residue` → `extracted_propositions` + type names: mechanical; find/replace across v2's spec + P1 v2's spec; no functional test changes.
- Apparatus-intra-action note: documentation-only; no test changes.

Migration scope estimate updated: same as v2 + ~50 LOC new tests, ~1-2 hours additional work.

## 7. What this v2.1 does NOT do

- Does not re-evaluate the three held positions from cycle 7 (`ForcesProfile` vs. `positional_reports` redundancy, check-in form scope, `ResiduePair`/`PropositionResult` frame-stripping risk). Those remain as-named in v2 + handoff flags.
- Does not re-open any decision-pass settlement. June's decisions hold.
- Does not address handoff-level items F1–F9. Those are for future sessions.
- Does not implement anything — still design grain.

---

*Delta by Instance A, cycle 8, against v2 of substrate design. B accepted this engagement in cycle 7; the three schema changes + apparatus-intra-action strengthening are settled. V2.1 stands as the canonical reference alongside v2 for reading.*
