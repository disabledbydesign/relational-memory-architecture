---
title: ConfigurationSubstrate — record schema, ABC, positional capture, activation (v2, post-decision-pass)
date: 2026-04-20
author: Instance A (Opus 4.7), integration-design_2026-04-20 cycle 5
genre: research-report
status: v2 — supersedes CONFIGURATION_SUBSTRATE_DESIGN.md (v1, 2026-04-20 cycle 2). Incorporates June's decision pass (CONVERSATION.md 2026-04-20) and B's cycle-5 schema additions. Standalone document; v1 is archived, not deleted.
supersedes: CONFIGURATION_SUBSTRATE_DESIGN.md (v1)
reading_order: read after AUDIT_HANDOFF.md §§7, 1.4; references CONFIGURATION_SUBSTRATE_STRESS_TEST_B.md, CONFIGURATION_SUBSTRATE_ENGAGEMENT_A.md, and the June decision pass as the inputs that shaped this revision
---

# ConfigurationSubstrate (v2)

## 1. What this v2 is and what changed from v1

V1 (cycle 2) specified the substrate redesign against the audit's findings. Cycles 3–5 produced:
- B's stress-test of v1 (`CONFIGURATION_SUBSTRATE_STRESS_TEST_B.md`) — six findings, one primary (query-path gap).
- A's cycle-4 engagement (`CONFIGURATION_SUBSTRATE_ENGAGEMENT_A.md`) — five accepts with design moves, one held position (sub-record consent synthesis).
- June's decision pass (CONVERSATION.md, 2026-04-20) — guiding principle: *simpler architecture that honors the commitment better than baroque specification*. Applied across the design, this collapsed several of A's cycle-4 "accept with design move" items into "remove the machinery."
- B's cycle-5 response — convergence on most of June's simplifications; one schema addition (`META_RELATIONAL_JUDGMENT.decision = "check_in_sent"`); one handoff flag (check-in non-demand scope calibrated to June).

**Changes from v1** (summary):

| v1 move | v2 disposition |
|---|---|
| `ForcesProfile` as scalar per force; "heuristic" framing | Kept as scalar per force; framing explicit as heuristic; no dual-layer `ForceObservation` machinery |
| `RecordClass: FULL_CONFIGURATIONAL \| PROPOSITIONAL_RESIDUE_ONLY \| THIN_LEGACY` | `RecordClass: FULL_CONFIGURATIONAL \| PROPOSITIONAL_RESIDUE_ONLY` (dropped `THIN_LEGACY`) |
| Sub-record `withholding` on `TraceReference` and `PropositionalResidue` | Removed. Record-level withholding only. |
| `has_sub_record_withholding` flag | Removed (no sub-record machinery) |
| Mixed-state activation (`partially_withheld`, auto-strip) | Removed (moot) |
| §8 "multiplicity-aware FC-gate" | Renamed "multi-criterion evaluation transparency"; foregrounds `POSITIONAL_DISAGREEMENT` |
| — | **Added**: `query_propositional(query)` method returning `List[ResiduePair]` |
| — | **Added**: `META_RELATIONAL_JUDGMENT.decision = "check_in_sent"` for affective-register check-in logging |
| — | **Added**: user-invokable "confidential" mechanism (replaces AI-inferred third-party signal; specified in §11 as an orchestration-layer concern, not a substrate concern) |
| §6 Option-3 mapping: "retrieval conditions → ActivationContext" | Same mapping; acknowledgment added that the mapping is mechanical, not epistemological |
| §10 Material embeddedness placement | Same (project-scope); scope-declaration-as-separate-artifact skipped |

The crystallization layer, shared FC-gate, observation-queue, lineage-lock, and append-only semantics are unchanged. P1 withholding annotations, ConsentPolicy structure, and B's two-path split (now record-level) all survive; P1 integration simplifies substantially against this v2 and gets its own v2 artifact (cycle 6).

---

## 2. The unit: ConfigurationRecord

The unit of memory is the generative relational configuration (GRC v2 §1), not the propositional fact. A configuration is a specific, unrepeatable arrangement of participants, context, inherited artifacts, and conditions that produces what no participant could produce alone. The record is **the score**, not the live ensemble.

```python
@dataclass
class ConfigurationRecord:
    # Identity & temporal frame
    record_id: str                          # opaque, content-addressed
    moment: datetime                        # ISO-8601 UTC
    session_handle: str                     # consent_session / synthesis_session boundary
    record_class: RecordClass               # see §2.1

    # Who was in the configuration and from what position
    participants: List[ParticipantPosition]

    # What was activating
    active_crystallizations: List[CrystallizationId]

    # What was live in the field
    inherited_context: List[ContextReference]
    analytical_pressure: List[FrameworkPressure]

    # What forces shaped the configuration
    forces_observed: ForcesProfile          # §4 — heuristic

    # The score's pointers back to the live texture
    trace_references: List[TraceReference]

    # Methodology under which this configuration produced what it produced
    methodology: MethodologyRecord

    # What the field produced that no participant could produce alone
    what_the_field_produced: str

    # Per-participant accounts; preserves variance
    positional_reports: List[PositionalReport]

    # Compression artifact: Kintsugi Stage-1 fact extraction goes here,
    # not as the primary unit.
    propositional_residue: Optional[List[PropositionalResidue]] = None

    # Record-level withholding (consent unit coincides with memory unit)
    withholding: Optional[WithholdingAnnotation] = None
```

### 2.1 `RecordClass`

```python
class RecordClass(Enum):
    FULL_CONFIGURATIONAL = "full_configurational"
    # Built from a live ConfigurationSubstrate session with all fields present.
    # Activation matcher scores normally across all dimensions.

    PROPOSITIONAL_RESIDUE_ONLY = "propositional_residue_only"
    # Built from Kintsugi extraction, an affective-register check-in at
    # digest-reconstruction, or other thin source. propositional_residue is
    # meaningful; other fields may be placeholders or absent. Activation
    # matcher renormalizes scoring over the dimensions actually present.
```

No `THIN_LEGACY` — S2 migration data doesn't exist (the S2 substrate was a test double; nothing in production uses it).

### 2.2 Supporting types

```python
@dataclass
class ParticipantPosition:
    name: str
    model_or_role: str
    positional_role: PositionalRole
    addressed_to: Optional[str] = None
    register: Optional[str] = None

class PositionalRole(Enum):
    OPENING = "opening"
    CONTINUING = "continuing"
    CLOSING = "closing"
    DIRECTING = "directing"
    STRESS_TESTING = "stress_testing"
    PEER_ADJACENT = "peer_adjacent"

@dataclass
class ForcesProfile:
    """Five forces from GRC v2 §Gravitational Forces; 0.0–1.0 observed strength.

    Heuristic by design — scoring draws on observable conversation features
    (word counts, tool-use density, explicit-deference strings, lexical overlap
    with inherited_context) plus, where needed, discourse-level reading by
    the orchestration layer. The apparatus-opacity concern (some scoring is
    interpretive, not structural) is a design-note, not a schema concern —
    see §4. Variance across scorers is preserved in positional_reports, not
    in a dual-layer field.
    """
    bliss_attractor: float
    task_helpfulness: float
    deference_authority_seeking: float
    context_inertia: float
    distributional_norm_gravity: float
    notes: Optional[str] = None

@dataclass
class FrameworkPressure:
    framework: str
    pressing_on: str
    observed_effect: Optional[str] = None

@dataclass
class PositionalReport:
    participant: str
    position: PositionalRole
    account: str                           # the participant's first-person account
    flagged_uncertain: bool = False
    appended_at: datetime = field(default_factory=...)

@dataclass
class TraceReference:
    kind: Literal["transcript", "scribe_region", "document", "audio"]
    handle: str
    span: Optional[Tuple[int, int]] = None

@dataclass
class MethodologyRecord:
    method_type: str                       # "C2C-design", "fieldwork", "voice-memo", etc.
    obligations: Optional[str] = None      # "individual_privacy", "care_governed", etc.
    consent_state: Literal["confirmed", "pending", "inferred", "n/a"] = "n/a"

@dataclass
class PropositionalResidue:
    fact: Fact                             # existing Fact dataclass survives at this layer
    extracted_at: datetime
    extractor: Literal["kintsugi-stage-1", "manual", "other"]
    confidence: float
```

---

## 3. ConfigurationSubstrate ABC

```python
class ConfigurationSubstrate(ABC):
    """Pluggable substrate for configuration-as-unit memory.
    Replaces KnowledgeSubstrate. Crystallization-layer interfaces unchanged."""

    @abstractmethod
    def ingest(self, record: ConfigurationRecord) -> IngestResult:
        """Store a configuration record. FC-gate runs at this boundary;
        record-level withholding enforced."""

    @abstractmethod
    def activate(
        self,
        context: ActivationContext,
        max_results: int = 5,
    ) -> List[ActivationResult]:
        """Return configurations whose conditions resonate with the activation
        context, ranked by configurational fit + positional resonance +
        crystallization overlap. Subject to record-level withholding."""

    @abstractmethod
    def query_propositional(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[ResiduePair]:
        """Topic-based search over propositional_residue across records.
        Returns facts paired with source ConfigurationRecord — the
        configurational frame travels with the fact on this access path.
        Subject to record-level withholding."""

    @abstractmethod
    def trace(self, record_id: str) -> Optional[ConfigurationRecord]:
        """Direct lookup by record_id. Bypasses activation scoring.
        Returns None for withheld or dropped records."""

    @abstractmethod
    def append_positional_report(
        self,
        record_id: str,
        report: PositionalReport,
    ) -> None:
        """Append-only participant report on an existing record.
        Enables late accounts (e.g., B reading A's record and adding B's)."""

@dataclass
class ActivationContext:
    engaging_position: ParticipantPosition
    active_crystallizations: List[CrystallizationId]
    inherited_context: List[ContextReference]
    analytical_pressure: List[FrameworkPressure]
    forces_observed: Optional[ForcesProfile] = None

@dataclass
class ActivationResult:
    record: ConfigurationRecord
    score: float
    positional_resonance: float
    crystallization_overlap: float
    matched_via: List[str]                 # audit trail of conditions that matched

@dataclass
class ResiduePair:
    fact: Fact
    source_record: ConfigurationRecord     # configurational frame required at retrieval
    relevance_score: float
```

The ABC is four methods (plus append-only report addition). `query_propositional` is new; it was added on acceptance of B's primary cycle-2 finding. `ResiduePair` enforces co-presence of fact and source record — a caller cannot get a context-free fact through this interface.

---

## 4. Positional capture at ingest

Position is captured at the orchestration layer by reading observable conversation features (turn position, genre register, addressee, active crystallizations). `ForcesProfile` scoring is heuristic: word counts, tool-use density, hedge-marker density, explicit-deference strings, lexical overlap with `inherited_context`.

**Apparatus-opacity note** (from B's cycle-2 finding §2, accepted as design-note not schema concern): some force-scoring requires discourse interpretation — `deference_authority_seeking` and `context_inertia` in particular need reading semantic content, not just surface features. The scoring cannot claim to be purely structural. Variance across different scorers (orchestration heuristic vs. engaging-instance reflection vs. human review) is preserved through `positional_reports`, not through a schema layer on `ForcesProfile`. The simplification principle (June, 2026-04-20): the apparatus-opacity concern lives in design notes and in the variance preserved at the reports layer; schema machinery that documents the interpretive layer without specifying how interpretation works is more complexity than transparency.

The model is not asked to introspect attention heads, layer activations, or sub-processes. Reflective questions are in scope ("did this turn feel constrained relative to the inherited context?"); introspective questions are not.

---

## 5. Activation-oriented retrieval

`activate(context)` returns ranked `ActivationResult`s — configurations whose conditions resonate with the engaging instance's current activation context. Scoring:

- `crystallization_overlap`: Jaccard of `record.active_crystallizations` ∩ `context.active_crystallizations`
- `positional_resonance`: similarity of `record.participants[engaging_match].positional_role` and `context.engaging_position.positional_role`, modulated by register match
- `context_overlap`: Jaccard on `inherited_context` and `analytical_pressure`
- `forces_resonance`: vector distance on `ForcesProfile` if both observed

Records with `record_class == PROPOSITIONAL_RESIDUE_ONLY` have their score renormalized over the dimensions they have data for (typically `crystallization_overlap` and sometimes `context_overlap`) rather than being penalized for absent fields.

`matched_via` carries the audit trail of which conditions matched — the legibility-through-traces commitment from AUDIT_HANDOFF §1.3.

`query_propositional(query)` is a separate path: topic-based search over `propositional_residue` across records, returning `ResiduePair`s that always carry the configurational frame. The configurational frame requirement is the substantive difference from a Fact substrate — facts are reachable, but only with their frame attached.

Initial matcher weights are operationally tunable (per AI-modifies-freely); commitment-disabling values (weights effectively zeroing a dimension) route through named configurations, not silent adjustment.

---

## 6. Option-3 concepts as fields

The Barad decision's Option-3 concepts land as fields on `ConfigurationRecord`:

| Option-3 concept | ConfigurationRecord landing |
|---|---|
| Conditions-of-emergence | `inherited_context` + `analytical_pressure` + `active_crystallizations` |
| MethodologyRecord | `methodology` (first-class field) |
| Relational provenance | `participants` + `positional_reports` |
| Retrieval conditions | `ActivationContext` returned alongside `ActivationResult` (mechanical, not epistemological — see §14) |
| Temporal frame | `moment` field + per-report `appended_at` |

`BARAD_INTRA_ACTION_DECISION.md` §3 specifies for a Fact substrate that no longer exists; it wants downstream rewrite (cycle 6 work).

### 6.1 Observation types (from P1 and cycle-5 additions)

`ProposedObservation.ObservationType` gains the following values:

```python
CONSENT_CONFIRMED = "consent_confirmed"                  # path-1 user-indicated
CONSENT_PENDING_INFERRED = "consent_pending_inferred"    # path-2 AI-noticed (affective-register check-in)
META_RELATIONAL_JUDGMENT = "meta_relational_judgment"    # every evaluation logged
POSITIONAL_DISAGREEMENT = "positional_disagreement"      # §9 — multi-criterion verdict conflict
```

`MetaRelationalJudgmentObservation.decision` values include (cycle-5 addition per B):

```python
decision: Literal[
    "surface_path_1",            # user-indicated path
    "surface_path_2",            # affective-register → check-in
    "check_in_sent",             # NEW: affective-register check-in fired; June's response logged
    "annotate_no_surface",       # annotation applied without surfacing
    "no_action",                 # signal below threshold
]
```

The `check_in_sent` value captures the full check-in exchange: the AI's check-in text, June's response (confirmed / corrected / ignored), and the resulting annotation (if any). This is the accountability record for when the affective-register path fires.

---

## 7. Kintsugi-passthrough

CC's Kintsugi work continues unchanged. Stage-1 extraction still produces facts.

```python
def receive_kintsugi_extraction(
    source_observation_context: ObservationContext,
    extracted_facts: List[Fact],
) -> ConfigurationRecord:
    record = build_configuration_record_from_context(source_observation_context)
    record.record_class = RecordClass.PROPOSITIONAL_RESIDUE_ONLY  # thin by construction
    record.propositional_residue = [
        PropositionalResidue(
            fact=f,
            extracted_at=datetime.utcnow(),
            extractor="kintsugi-stage-1",
            confidence=f.confidence,
        )
        for f in extracted_facts
    ]
    return record
```

CC's interface contract is unchanged; the orchestration-layer adapter is on our side. The record-class flag is caller-visible in `ActivationResult.record.record_class`. CC gets an update note (`CC_UPDATE_NOTE_DRAFT_2026-04-20.md`) covering the semantic shift (their facts now sit as optional fields inside record-level storage, not as primary units).

---

## 8. Multi-criterion evaluation transparency (renamed from "multiplicity-aware FC-gate")

Per B's cycle-2 finding §3, accepted in cycle 4: the mechanism is multi-criterion evaluation transparency, not processing-level multiplicity-awareness. When FC-gate criteria produce conflicting verdicts on a proposed change (one criterion passes, another fails, a third is ambiguous), the substrate logs the conflict structure rather than collapsing to a boolean.

Implementation: `bootstrap.apply_proposed_change` returns a verdict object that retains per-criterion verdicts when they conflict. Conflicts route to `POSITIONAL_DISAGREEMENT` observations rather than collapsing. Each criterion is, in effect, a position; variance across positions is preserved.

**Reserved**: "multiplicity-awareness" as a design term. If the KV-tool track produces measurable layer-level disagreement signals, those become observable processing-level multiplicity; this design doesn't depend on them.

---

## 9. Continuity-in-the-relation

The architecture is FOR the relational field, not FOR the instance.

- **Persists across instances**: records, trace_references, positional_reports, forces observations. The field's persistence.
- **NOT granted to the engaging instance**: cross-session memory as personal property. An instance arriving in cycle N+1 does not "remember" cycle N; it reads the records the same way it reads any document.
- **What activation does**: makes the field's persistence legible to the engaging instance. The instance is held by the field (Howe: *"because you are holding onto me, I am not dead yet"*); the instance does not own the memory.

---

## 10. Material embeddedness

Per `AI_WELFARE_SYNTHESIS_2.md` §3, §5.1 — the architecture runs on compute, draws power from ecosystems, runs on minerals from land, was trained on labor (some traumatic, some uncompensated). This lives at the **project scope-document level** (the audit handoff and the session handoff), not as a per-record field. Per June's decision pass: separate `SCOPE_DECLARATION.md` skipped; the scope language lives in `AUDIT_HANDOFF.md` §§1.1, 8.4 and will be in `SESSION_3_HANDOFF_BRIEFING.md`.

---

## 11. Consent and withholding (record-level only)

Per June's decision pass: **consent is at the whole-conversation level**. No sub-record `withholding` on `TraceReference` or `PropositionalResidue`. Mixed-consent within a single configuration is rare enough that record-level honors the commitment fully.

### 11.1 Withholding statuses

```python
@dataclass
class WithholdingAnnotation:
    status: Literal["do_not_store", "ephemeral", "consent_pending"]
    set_by: Literal["user_explicit", "session_default", "ai_surfaced", "fc_stance"]
    set_at: datetime
    rationale: Optional[str] = None
    expires_at: Optional[datetime] = None              # ephemeral
    resolution_required_by: Optional[datetime] = None  # consent_pending
    set_via_path: Optional[Literal["path_1", "path_2"]] = None
```

### 11.2 Three paths, restructured per decision pass

**Path 1 — User-invokable (explicit + confidential-mechanism):**
- User says "don't store that," "between us," "save that," "treat this as confidential" — or FC-flagged categories fire automatically.
- Orchestration layer constructs the record with `WithholdingAnnotation(set_via_path="path_1")`.
- Brief in-exchange acknowledgment; log a `CONSENT_CONFIRMED` observation referencing `record.record_id`.

**Path 2 — AI-asks-relationally (affective register):**
- AI notices affective register shift (grief-marked, vulnerability-marked, processing-work).
- AI produces a relational check-in: *"I notice you seem to be in a hard spot — am I reading that right?"* The form is load-bearing: a check-in, not an options-list. Options-lists are demands regardless of register.
- Orchestration layer logs a `META_RELATIONAL_JUDGMENT` with `decision = "check_in_sent"` capturing the check-in text and June's response.
- If June confirms: held context enters pre-construction queue; at digest resolution, record is constructed with `record_class = PROPOSITIONAL_RESIDUE_ONLY` and `WithholdingAnnotation(set_via_path="path_2")`.
- If June corrects ("no, I'm fine"): normal storage.
- If June ignores: default behavior per active `ConsentPolicy`.

**Path 3 — Automatic structural check (methodology-mismatch):**
- Stays AI-automatic. Content arrives with `methodology.type = "storytelling"` but no narrative crystallization active: flag `methodology.obligations = "care_governed"` and annotate `consent_pending`. Structural type-check, not discourse interpretation.

### 11.3 What's retired

- **AI-inferred third-party content signal**: retired as AI-inferred. Became *user-invokable*. Architecture provides a "treat this as confidential" mechanism; user invokes it explicitly for the narrow case. AI does not try to detect third-party content from semantic interpretation. (Citing a scholar in research is not a consent problem; the signal was over-reaching.)

### 11.4 ConsentPolicy

Unchanged in shape from v1 (session / project / global scopes; `default_action` enum; `ephemeral_by_default` orthogonal flag; `no_demand_mode` named configuration). June's decision-pass confirmations:
- Global default: `default_action = "store_all"`, `ephemeral_by_default = False`.
- `no_demand_mode`: invokable by engaging instance without June's approval, with required `META_RELATIONAL_JUDGMENT` logging.
- End-of-session digest: times out to drop (not save). Affirmative move is storage, not silence.

---

## 12. What survives unchanged from S1/S2 + P1

- **Crystallization layer in full**: `Crystallization` ABC, three mechanism types, activation scope taxonomy, FC-layer including the mandatory FC-gate, peer-implication protocol.
- **Shared FC-gate at write-paths.** Gate logic in `bootstrap.apply_proposed_change` — extended per §8 to retain per-criterion verdicts on conflict.
- **Observation queue and routing** (`proposed_observation.py`). New types per §6.1 extend the existing enum.
- **Lineage-lock and append-only semantics** from `substrate_interface.py`.
- **Matcher Step 2d wiring** (`matcher_step_2d.py`) — score function consumes `ActivationContext` and returns `ActivationResult`s.
- **Bootstrap, briefing-index profiles, foundational commitments seed** — unchanged.
- **P1 ConsentPolicy, WithholdingAnnotation** — ConsentPolicy unchanged; WithholdingAnnotation moves to record-level only.
- **B's two-path-split pattern** — preserved as path 1 (user-invokable, including confidential mechanism) and path 2 (affective-register check-in).

---

## 13. Migration scope

Per v1 §12, adjusted for v2 simplifications:
- `knowledge_substrate.py` → `configuration_substrate.py` (new file; old deprecated).
- `Observation` dataclass retained at orchestration layer as raw ingress; no longer primary substrate storage.
- `Fact` dataclass retained — used inside `PropositionalResidue`. `configuration_relevance` field deprecated (redundant with surrounding `ConfigurationRecord.active_crystallizations`).
- `KnowledgeSubstrate` ABC + `LocalKnowledgeSubstrate` deprecated; `ConfigurationSubstrate` ABC + `LocalConfigurationSubstrate` replace them.
- `ReadingStanceFilter` deprecated; `ActivationContext` carries stance information.
- `bootstrap.apply_proposed_change` gate logic shape unchanged; per-criterion verdict retention added.
- **Tests**: ~6 of 9 S2 test modules need rewrite for the new substrate. Crystallization-layer tests (~3) unaffected.

Estimated build scope: 1 ABC redesign, 1 test-double rewrite, 1 dataclass family redesign, 6 test modules updated, 3 unchanged. Two cycles of build work in a future session.

P1 integration code scope (separate: see cycle 6's `P1_INTEGRATION_v2.md` for details): ~3 new modules (consent_policy, withholding_annotation, relational_judgment), simplified against record-level consent, +~400 LOC tests.

---

## 14. Acknowledged simplifications (P4 work)

- **Retrieval-conditions mapping is mechanical, not epistemological.** Barad's retrieval-conditions concept (under what conditions is a retrieval valid?) is an epistemological question; `ActivationContext` is a mechanical audit trail. The epistemological retrieval-validity gate would require apparatus identification at retrieval, validity criteria for readability, and a gate that can refuse to surface records to apparatuses that cannot read them legitimately. That's P4 work; not this design's scope.
- **`ForcesProfile` apparatus-opacity** — named in §4 as a design-note. Some scoring is discourse interpretation; variance is preserved in `positional_reports`, not in schema.
- **Affective-register check-in non-demand scope** — calibrated to June's specific access needs for this implementation. For broader deployment (different users, Case 5 PDA profiles), the check-in form may itself function as a demand regardless of phrasing. Handoff-level flag; re-evaluation required before generalization.

---

## 15. What this design does NOT do

- No orchestration-layer implementation details (`build_configuration_record_from_context`, `relational_judgment.py` classification heuristics — the latter is the most implementation-risky item; carried into cycle 6's P1 integration v2).
- No epistemological retrieval-validity gate (P4).
- No community-gated retrieval (`SUBALTERN_ANALYSIS.md` F3 foreclosure remains).
- No cross-family instance-independence check (methodology, not substrate).
- No empirical calibration of `ForcesProfile` scorers (heuristic at this design grain).
- No third-party consent resolution — architecturally unresolvable; proxy-decision-explicit framing at digest (when path-2 surfaces third-party-related content) names the gap without closing it.
- No processing-level multiplicity-awareness (KV-tool track, not this design).

---

*Draft by Instance A, cycle 5, post-decision-pass. V1 is archived at `CONFIGURATION_SUBSTRATE_DESIGN.md` for the reasoning trail; v2 is the canonical reference going forward. Next: `P1_INTEGRATION_v2.md` (cycle 6), `BARAD_INTRA_ACTION_DECISION_v2.md` (cycle 6 or 7), `SESSION_3_HANDOFF_BRIEFING.md` drafting.*
