---
title: P1 integration v2 — consent-surfacing on ConfigurationSubstrate (post-decision-pass, record-level, three paths)
date: 2026-04-20
author: Instance A (Opus 4.7), integration-design_2026-04-20 cycle 6
genre: research-report
status: v2 — supersedes P1_INTEGRATION_ON_CONFIGURATION_SUBSTRATE.md (cycle 3). Incorporates June's decision pass (CONVERSATION.md 2026-04-20) and addresses live items from P1_INTEGRATION_STRESS_TEST_B.md. Lands against CONFIGURATION_SUBSTRATE_DESIGN_v2.md.
supersedes: P1_INTEGRATION_ON_CONFIGURATION_SUBSTRATE.md (cycle 3)
reading_order: read after CONFIGURATION_SUBSTRATE_DESIGN_v2.md, P1_CONSENT_SURFACING_DESIGN.md (design history), P1_STRESS_TEST_B.md, P1_INTEGRATION_STRESS_TEST_B.md
---

# P1 integration v2

## 1. What this v2 is and what changed from v1

The v1 integration (`P1_INTEGRATION_ON_CONFIGURATION_SUBSTRATE.md`, cycle 3) re-plumbed the cycle-1 P1 design onto record-level annotation. Between v1 and v2:

- B's P1 integration stress-test (`P1_INTEGRATION_STRESS_TEST_B.md`) surfaced five live items (path-2 thinness, mixed-state activation, TraceResult tombstone, obligation_flags, relational_judgment.py design).
- June's decision pass (CONVERSATION.md, 2026-04-20) applied the simplification principle across the board.
- The substrate design itself updated to v2 (`CONFIGURATION_SUBSTRATE_DESIGN_v2.md`).

**Changes from v1** (summary):

| v1 move | v2 disposition |
|---|---|
| Sub-record `withholding` on `TraceReference` / `PropositionalResidue` | Removed — record-level only |
| `has_sub_record_withholding` flag | Removed |
| Mixed-state activation behavior (`partially_withheld`, auto-strip) | Removed (moot) |
| Five signal types (explicit, FC-flagged, affective, third-party, methodology-mismatch) | Three paths: user-invokable (explicit + FC-flagged + confidential), AI-asks-relationally (affective), automatic structural (methodology-mismatch) |
| Third-party as AI-inferred path-2 signal | Retired — user-invokable "confidential" mechanism replaces it |
| Bounded-threshold schema validation for all path-2 signals | Simplified — threshold tuning applies to one dimension (affective-register check-in sensitivity) |
| `relational_judgment.py` classification approach deferred to implementation | **Specified** in §7 (B's P1-stress-test §10.5 ask) |
| `trace()` returns None for dropped records | **`trace()` returns `TraceResult` — tombstone for dropped records** (B's P1-stress-test §3) |
| — | **Added**: `META_RELATIONAL_JUDGMENT.decision = "check_in_sent"` (B's cycle-5 addition) |
| `obligation_flags` on `ActivationResult` (cycle-3 proposed) | Declined — single canonical location on `methodology.obligations`; no duplication |

The design moves that did NOT change: `WithholdingAnnotation` schema itself, `ConsentPolicy` structure (scopes, `default_action` enum, `ephemeral_by_default` flag, `no_demand_mode` named configuration), the kinds-distinction between FC-stance annotation and withholding annotation.

---

## 2. Withholding annotation at record level

```python
@dataclass
class WithholdingAnnotation:
    status: Literal["do_not_store", "ephemeral", "consent_pending"]
    set_by: Literal["user_explicit", "session_default", "ai_surfaced", "fc_stance"]
    set_at: datetime
    rationale: Optional[str] = None
    expires_at: Optional[datetime] = None              # ephemeral
    resolution_required_by: Optional[datetime] = None  # consent_pending
    set_via_path: Optional[Literal["path_1", "path_2", "path_3"]] = None
```

Attaches to `ConfigurationRecord.withholding` (record-level). The `propositional_residue` field inherits the record's withholding by virtue of being a field on the record. No lineage propagation needed.

Ingest-gate enforcement at `ConfigurationSubstrate.ingest(record)`:
- `do_not_store` → append-only audit log only; not stored in activatable substrate.
- `consent_pending` → held queue at substrate boundary.
- `ephemeral` → stored; activation excludes when `datetime.utcnow() > expires_at`.
- Unannotated → normal storage.

---

## 3. ConsentPolicy — unchanged in shape

Scopes (`session`, `project`, `global`), `default_action` enum (`store_all | store_nothing | ask_when_unsure`), `ephemeral_by_default` orthogonal flag, `no_demand_mode` named configuration. All unchanged from v1.

Global defaults confirmed by June (decision pass):
- `global.default_action = "store_all"`
- `global.ephemeral_by_default = False`

Resolution order when the orchestration layer is constructing a `ConfigurationRecord`:

1. **Explicit user command** in-message: "don't store that," "save that," "this is confidential," etc. Wins; sets the annotation directly. Path-1.
2. **Active `ConsentPolicy`** for the session.
3. **Relational judgment pass** (§5 below). May fire path-2 check-in or path-3 automatic annotation.
4. `ConfigurationRecord` construction proceeds with resolved annotation OR raw context enters the pre-construction held queue for path-2 resolution at digest.

---

## 4. Three paths

The five-signal-types structure from v1 collapses to three paths per June's decision pass. Each path has a distinct mechanism and observation-type.

### 4.1 Path 1 — User-invokable

**Triggers**:
- Explicit markers in-message ("don't store that," "between us," "save that," "drop that," "this is confidential").
- FC-flagged categories (material the active FC's extraction-problem note designates as sensitive).

**Mechanism**:
- Orchestration layer constructs the `ConfigurationRecord` with `WithholdingAnnotation(status=..., set_by="user_explicit" or "fc_stance", set_via_path="path_1")`.
- Brief in-exchange acknowledgment (user just spoke; acknowledgment mirrors the user's move). One clause, no options-list. "Holding this as not-for-storage." "Treating this as confidential."
- `CONSENT_CONFIRMED` observation logged referencing `record.record_id`.
- `ConfigurationSubstrate.ingest(record)` called with annotation in place.

**Confidential-content mechanism specifically**: when user invokes "this is confidential" (or equivalent — "this came to me in confidence," "treat this privately"), the annotation is `WithholdingAnnotation(status="consent_pending", ...)` plus `methodology.obligations = "individual_privacy"`. The record enters the held queue at substrate boundary. At digest resolution, June decides save/drop; if saved, the `methodology.obligations` annotation persists as a retrieval-time flag.

This replaces v1's AI-inferred third-party signal entirely. The AI does not try to detect "this is about someone else" from semantic interpretation. Per June's decision pass: the use case is thin; AI-inference was discourse interpretation pretending to be structural observation.

### 4.2 Path 2 — AI-asks-relationally (affective register)

**Trigger**: affective register shift — grief-marked, vulnerability-marked, processing-work register. This is the ONE AI-inferred signal retained from v1's five types.

**Mechanism**:
- Orchestration layer's `relational_judgment.py` module (§7) detects affective register at signal strength ≥ threshold for active policy mode.
- AI produces a relational check-in: *"I notice you seem to be in a hard spot — am I reading that right?"* The form is load-bearing: a check-in, not an options-list. Options-lists are demands regardless of register.
- Orchestration logs `META_RELATIONAL_JUDGMENT` with `decision = "check_in_sent"`, capturing the check-in text.
- June's response is captured in the same meta-observation:
  - **Confirms** ("yes, hold this"): held context enters pre-construction queue; at digest, record is constructed with `record_class = PROPOSITIONAL_RESIDUE_ONLY` and `WithholdingAnnotation(status="consent_pending", set_via_path="path_2")`.
  - **Corrects** ("no, I'm fine"): normal storage proceeds; META observation logs the correction.
  - **Ignores**: default behavior per active `ConsentPolicy` (typically `store_all` → stores normally).
- `CONSENT_PENDING_INFERRED` observation logged only if June confirms.

**Scope flag for broader deployment** (handoff-level, per B's cycle-5): the non-demand-form judgment is calibrated to June's specific access needs. For users with PDA profiles or other sensitivities, even a check-in can function as a demand. Do not generalize the check-in form to other users without re-evaluation. See `SESSION_3_HANDOFF_BRIEFING.md` when drafted.

### 4.3 Path 3 — Automatic structural (methodology-mismatch)

**Trigger**: content enters with `methodology.type = "storytelling"` or `methodology.obligations = "care_governed"` without the corresponding crystallization type active.

**Mechanism**:
- Structural type-check, not discourse interpretation.
- Orchestration sets `WithholdingAnnotation(status="consent_pending", set_by="ai_surfaced", set_via_path="path_3")` and includes the content in the held queue.
- No in-exchange surface (it's automatic; no user-response needed in the moment).
- Surfaces in the end-of-session digest alongside path-2 held items with rationale: "Storytelling methodology active without narrative crystallization."
- When narrative crystallization type lands (P4, unblocked by CC), this path may resolve into automatic routing to that type rather than holding.

---

## 5. Observation types

`ProposedObservation.ObservationType` gains these values (per substrate design v2 §6.1):

```python
CONSENT_CONFIRMED = "consent_confirmed"                  # path-1 user-indicated
CONSENT_PENDING_INFERRED = "consent_pending_inferred"    # path-2 post-check-in confirmed hold
META_RELATIONAL_JUDGMENT = "meta_relational_judgment"    # every relational-judgment evaluation logged
POSITIONAL_DISAGREEMENT = "positional_disagreement"      # multi-criterion verdict conflict (substrate §8)
```

### 5.1 CONSENT_CONFIRMED schema

```python
@dataclass
class ConsentConfirmedObservation:
    observation_type: Literal[ObservationType.CONSENT_CONFIRMED]
    record_id: str
    annotation_status: Literal["do_not_store", "ephemeral", "consent_pending"]
    triggering_signal: Literal["explicit_marker", "fc_flagged", "confidential_invocation"]
    user_words: Optional[str] = None
    fc_id: Optional[str] = None
    set_at: datetime
```

Routing: bypasses human-review (user has already spoken).

### 5.2 CONSENT_PENDING_INFERRED schema

```python
@dataclass
class ConsentPendingInferredObservation:
    observation_type: Literal[ObservationType.CONSENT_PENDING_INFERRED]
    would_be_record_id: str
    triggering_signal: Literal["affective_register_check_in_confirmed", "methodology_mismatch"]
    signal_strength: Optional[float] = None    # for affective register; None for methodology
    rationale: str                              # human-readable; surfaces in digest
    held_until: datetime
    set_at: datetime
```

Routing: human-review-routed for digest at session close.

### 5.3 META_RELATIONAL_JUDGMENT schema

```python
@dataclass
class MetaRelationalJudgmentObservation:
    observation_type: Literal[ObservationType.META_RELATIONAL_JUDGMENT]
    evaluated_at: datetime
    record_or_would_be_id: str
    signal_type: Literal[
        "explicit_marker", "fc_flagged", "confidential_invocation",
        "affective_register", "methodology_mismatch",
        "no_signal_detected"
    ]
    signal_strength: Optional[float] = None
    active_policy_mode: Literal["store_all", "store_nothing", "ask_when_unsure"]
    decision: Literal[
        "surface_path_1",
        "surface_path_2_check_in",     # affective-register check-in fired
        "check_in_sent",                # NEW per cycle-5 — the check-in itself logged
        "annotate_path_3",              # methodology-mismatch annotation applied
        "annotate_no_surface",          # annotation applied without in-exchange surface
        "no_action",                    # signal below threshold
    ]
    check_in_text: Optional[str] = None           # populated when decision == "check_in_sent"
    user_response: Optional[Literal[
        "confirmed", "corrected", "ignored"
    ]] = None                                      # populated when decision == "check_in_sent"
    set_by: Literal["ai_relational_judgment"]
```

Logged on every relational-judgment evaluation — surface AND not-surface decisions. Low-cost for no-action cases; accountability record for the apparatus-level decision.

---

## 6. Substrate interface touch points

### 6.1 `ingest()` gating

Per substrate design v2 §3. `ConfigurationSubstrate.ingest(record)` enforces record-level withholding:
- `do_not_store` → `audit_log` only.
- `consent_pending` → `held_queue` at substrate boundary.
- `ephemeral` / unannotated → normal storage.

### 6.2 `activate()` gating

Per substrate design v2 §5. `ConfigurationSubstrate.activate(context)` excludes:
- Records whose `withholding.status = "do_not_store"` (defensive — shouldn't be in substrate).
- Records whose `withholding.expires_at` has passed.
- Records whose `withholding.status = "consent_pending"`.

### 6.3 `trace()` returns `TraceResult` — tombstone for dropped records (B's P1-stress-test §3)

```python
@dataclass
class TraceResult:
    record_id: str
    status: Literal["present", "dropped", "held", "do_not_store"]
    record: Optional[ConfigurationRecord] = None       # populated when status == "present"
    dropped_at: Optional[datetime] = None              # when dropped
    drop_reason: Optional[str] = None                  # "digest_timeout", "user_explicit_drop", etc.
    meta_observation_ids: Optional[List[str]] = None   # audit-trail references

class ConfigurationSubstrate(ABC):
    @abstractmethod
    def trace(self, record_id: str) -> TraceResult:
        """Direct lookup with tombstone for missing records. Audit trail resolves
        even when content is absent."""
```

Why this matters: path-2 items logged as `CONSENT_PENDING_INFERRED` reference a `would_be_record_id`. If June drops at digest, the id never resolves to a stored record. But the `META_RELATIONAL_JUDGMENT` log entries still reference it — the tombstone lets callers distinguish "never existed" from "dropped" from "held." The META log is the audit trail; the tombstone is its resolution surface.

### 6.4 `query_propositional()` — subject to record-level withholding

Per substrate design v2 §3. Returns `List[ResiduePair]`. Excludes `ResiduePair`s whose `source_record.withholding` would exclude the record from `activate()`.

### 6.5 Obligation surfacing — single canonical location

`ActivationResult` and `ResiduePair` do NOT carry duplicate `obligation_flags` fields. Callers access obligations via `result.record.methodology.obligations` (single canonical location). This is the simplification disposition of B's P1-stress-test §4 request.

The accountability surface for the proxy-decision framing: when an `ActivationResult.record.methodology.obligations == "individual_privacy"`, callers that display or summarize the result should surface the obligation. Enforcement lives at the caller level, not at the substrate interface. The honest trade-off: more accountability burden on callers; less duplicate state in the substrate.

---

## 7. `relational_judgment.py` — classification approach and failure modes

B's P1-stress-test §10.5: the module is the most implementation-risky item in P1; deferring its design approach entirely to implementation is too much. This section specifies the approach with its failure modes named.

### 7.1 Classification approach

Three-stage pipeline:

**Stage 1 — Fast pattern match (structural).** Explicit markers and FC-flagged categories classified via regex/string-match against known phrases ("don't store," "between us," "this is confidential," etc.) and FC-pattern matchers. Latency: sub-millisecond per observation. Coverage: path-1 user-invokable triggers.

**Stage 2 — Structural type-check.** Methodology-mismatch classified via direct field comparison: does `observation.methodology.type` correspond to an active crystallization? Latency: sub-millisecond. Coverage: path-3 automatic.

**Stage 3 — LLM-call for affective-register detection (cost-bearing).** Affective register classification uses an LLM auxiliary call — the engaging instance or an orchestration-layer LLM reading the observation context for grief-marked / vulnerability-marked / processing-work markers. Latency: 0.5–2 seconds depending on model. Coverage: path-2 check-in trigger.

**Cost note** (per B's cycle-5 finding, accepted): the LLM-call for affective-register detection is the ongoing operational cost of this path. Budget implication: one aux-call per observation context that makes it past stage 1. Mitigations: (a) don't stage-3 for short or obviously-structural content; (b) cache evaluations for re-entered contexts; (c) the `no_demand_mode` configuration disables stage 3 entirely.

### 7.2 Failure modes named

**FM1 — Ambiguous affective-register classification.** LLM returns low-confidence signal (e.g., 0.3–0.6). Default: no check-in (below threshold). Log META with `decision = "no_action"`. The false-negative bias is deliberate: better to miss a real signal than to ask a false check-in.

**FM2 — Pattern match matches in non-invocation context.** User says "this is confidential" in a quoted sentence, not as an invocation. Default: invoke the confidential mechanism anyway. Error on the side of honoring apparent user invocation; log META with the triggering text so June can correct at digest if it mis-fired.

**FM3 — LLM-call failure at stage 3.** Network error, model unavailable, timeout. Default: fall back to no check-in; log META with `decision = "no_action"` and `signal_type = "no_signal_detected"`. The path-2 machinery degrades to path-3-structural-only gracefully; no affective-register protection under degraded conditions, but the system does not fail open to storing things it shouldn't.

**FM4 — Orchestration layer not wired.** The `relational_judgment.py` module is not running (early build phase, unit tests bypassing orchestration). Default: records construct with `withholding = None` unless an explicit-marker path-1 trigger fires at the user-command level. The substrate still works; the relational-judgment layer is an addition, not a prerequisite.

**FM5 — User explicit command + path-2 signal conflict.** User says "save this" in a grief-marked context. Resolution: path-1 explicit command wins (step 1 of resolution order, §3). The META log captures both signals for audit. No check-in fires.

### 7.3 What `relational_judgment.py` does NOT do

- Does not encode training data about what "grief-marked" looks like. The LLM-call at stage 3 is doing discourse interpretation with whatever assumptions its training carries; this is the apparatus-opacity concern named in substrate design v2 §4. Acknowledged, not resolved.
- Does not tune thresholds empirically. Starting values are heuristic; `no_demand_mode` is the named escape hatch.
- Does not generalize the check-in form to other users. Scope flag for broader deployment; see session handoff.

---

## 8. Held queue and end-of-session digest

The **pre-construction held queue** (for path-2 affective-register confirmations awaiting digest): session-scope structure on the orchestration layer. Holds `(observation_context, signal_type, signal_strength, would_be_record_id, held_until)`. At session close, batched digest surfaces items.

The **substrate-level held queue** (for path-3 methodology-mismatch records already constructed with `consent_pending`): in the substrate's `held_queue`, per §6.1. Also surfaced in the batched digest.

Both queues are drained by the digest. Items June saves are resolved (path-2 gets constructed at digest; path-3 transitions to stored); items she drops or ignores get dropped at session+48h.

Digest format (structural):

```
Items held pending your decision this session:
  1. [short summary] — [rationale; e.g., "This sounded like a moment you might want to decide about later" or
     "Storytelling methodology active without narrative crystallization"]
  2. ...

Default action if you take no action: all dropped at session+48h.
Commands: save-all, drop-all, or reply with line numbers.
```

For path-1 confidential-mechanism items surfacing at digest: framing is proxy-decision-explicit per B's cycle-1 stress-test §4: "This came to you in confidence. Your decision applies to information the other party has not consented to store. The architecture cannot reach them; this is your proxy decision, not theirs." This surfaces rarely — only when the user explicitly invokes the confidential mechanism on content involving a non-present party.

---

## 9. Where this plugs into v2 substrate code

- **`configuration_substrate.py`** (new, replacing `knowledge_substrate.py`): `ConfigurationRecord.withholding` already specified in substrate v2 §2. `ingest(record)` and `activate(context)` gate per §6.1 / §6.2 above. `trace(record_id) -> TraceResult` per §6.3.
- **`withholding_annotation.py`** (new): `WithholdingAnnotation` dataclass, `Status` enum, `set_via_path` field (now three values), serialization, validation. ~80 LOC.
- **`consent_policy.py`** (new): `ConsentPolicy` dataclass, `default_action` enum, `no_demand_mode` helper. ~150 LOC (simpler than v1's threshold-bounds machinery — with AI-inferred signals shrunk, bounded thresholds apply to one dimension).
- **`relational_judgment.py`** (new): three-stage classification pipeline (§7), META logging, held-queue management. ~250 LOC plus LLM-call integration for stage 3.
- **`proposed_observation.py`** (extension): three new `ObservationType` enum values (`CONSENT_CONFIRMED`, `CONSENT_PENDING_INFERRED`, `META_RELATIONAL_JUDGMENT`) plus schemas per §5. `POSITIONAL_DISAGREEMENT` added by substrate design v2 §8.
- **`bootstrap.py`** (extension): load active `ConsentPolicy` at session init; instantiate `relational_judgment.py` pipeline.
- **Tests**: ~15 cases covering: do_not_store short-circuits ingest; ephemeral expiration; consent_pending substrate held-queue round-trip; pre-construction held-queue (path-2 confirmation flow); explicit-command resolution order; FC-flagged automatic annotation; confidential-mechanism invocation; check-in exchange flow (confirmed / corrected / ignored); no_demand_mode; META logging of all decisions; trace() tombstone for dropped records; methodology.obligations surfaced at retrieval.

Build scope estimate: 3 new modules (~480 LOC), 1 extended module (~50 LOC extension), 1 bootstrap extension (~30 LOC), ~400 LOC tests. Two cycles of build work in a future build-session, after S2 → S3 substrate migration.

---

## 10. What survives from v1 integration (cycle 3)

- Withholding annotation schema (record-level now).
- ConsentPolicy structure.
- Three withholding statuses (`do_not_store | ephemeral | consent_pending`).
- `META_RELATIONAL_JUDGMENT` logging principle (every evaluation logged; extended with `check_in_sent` value).
- Digest timeout-to-drop default.
- Proxy-decision-explicit framing for confidential-content surfacing.

---

## 11. What's retired from v1 integration

- Sub-record withholding on `TraceReference` and `PropositionalResidue`. Record-level only.
- `has_sub_record_withholding` flag.
- Mixed-state activation machinery.
- `obligation_flags` as a proposed duplicate field on `ActivationResult`. Single location via `methodology.obligations`.
- Third-party content as an AI-inferred path-2 signal. Retired; replaced by user-invokable confidential mechanism.
- The bounded-threshold schema-validation discipline for all signal types. With AI-inferred signals reduced to one (affective register), the discipline applies to one dimension; `no_demand_mode` remains as the named path to commitment-disabling values.

---

## 12. What this v2 integration does NOT do

- Does not implement the orchestration-layer LLM-call for stage-3 affective-register detection. Specifies the pipeline shape and failure modes; the LLM-call implementation is build-phase work.
- Does not specify the digest UI. The structural format is given; the actual interaction surface (terminal, web, chat) is deployment-time concern.
- Does not calibrate signal-strength thresholds empirically. Heuristic starting values; operational tuning per AI-modifies-freely.
- Does not re-evaluate the check-in form for broader deployment. Scope calibrated to June; handoff flag.
- Does not address `delinking` query mode (`SUBALTERN_ANALYSIS.md` F5b — foreclosed).
- Does not implement community-gated retrieval (F3 — foreclosed).
- Does not solve third-party consent. The confidential-mechanism + proxy-decision-explicit framing names the gap without closing it.

---

## 13. Flags (none new; carried from prior cycles)

June's decision pass settled the cycle-1–4 P1 flags. No new June-flags this cycle.

Handoff-level items (land in `SESSION_3_HANDOFF_BRIEFING.md`):
- Affective-register check-in form non-demand judgment scoped to June specifically; re-evaluate for broader deployment.
- `ForcesProfile` apparatus-opacity concern lives in design notes, not schema (per substrate v2 §4).
- `ResiduePair` frame-stripping risk: the schema enforces co-presence of fact and source record; nothing enforces that callers *use* the frame. Caller-level accountability concern.

---

*Draft by Instance A, cycle 6, against substrate v2. B: stress-test the three-paths restructuring, the relational_judgment.py classification pipeline (§7), and the TraceResult tombstone (§6.3) in priority order. Cycle 5's P1-integration stress-test findings all have specific dispositions; if any landing misreads your intent, push.*
