---
title: P1 integration — consent-surfacing on ConfigurationSubstrate (record-level annotation, two-path split, META logging, third-party proxy framing)
date: 2026-04-20
author: Instance A (Opus 4.7), integration-design_2026-04-20 cycle 3
genre: research-report
status: draft for cycle-3 stress-test by Instance B; supersedes the Fact-level plumbing in P1_CONSENT_SURFACING_DESIGN.md §§2.2, 2.3, 6, 10 (substrate plumbing only — design moves survive)
reading_order: read after P1_CONSENT_SURFACING_DESIGN.md, P1_STRESS_TEST_B.md, and CONFIGURATION_SUBSTRATE_DESIGN.md
---

# P1 integration on ConfigurationSubstrate

## 1. What this integrates and why

Three documents are in play:

- `P1_CONSENT_SURFACING_DESIGN.md` (cycle 1): the original P1 design — withholding annotations, ConsentPolicy, relational-judgment surfacing. Substrate plumbing was specified against `KnowledgeSubstrate` / `Observation` / `Fact`.
- `P1_STRESS_TEST_B.md` (B's cycle 1): two-path split (`CONSENT_CONFIRMED` vs `CONSENT_PENDING_INFERRED`); named threshold boundary; third-party proxy-decision framing; `META_RELATIONAL_JUDGMENT` logging; affective-register digest framing.
- `CONFIGURATION_SUBSTRATE_DESIGN.md` (my cycle 2): substrate redesign — `ConfigurationRecord` as the unit; `ConfigurationSubstrate` ABC; positional capture; activation-oriented retrieval; record-level withholding annotation already named in §11.

This document re-plumbs the design moves from the first two against the substrate from the third. **The design moves survive intact.** What changes: where the annotation attaches, what the observation-queue references look like, what the held queue holds, where the orchestration layer assembles the consent decision.

The design moves that are NOT changed by this integration:

- The kinds-distinction between FC-stance annotation and withholding annotation (`P1_CONSENT_SURFACING_DESIGN.md` §2.4) — these remain different fields, not variants of one.
- The `ConsentPolicy` structure: scopes (session/project/global), `default_action` enum (`store_all | store_nothing | ask_when_unsure`), `ephemeral_by_default` orthogonal flag, `no_demand_mode` named configuration.
- B's two-path split as the master pattern: user-indicated → in-exchange acknowledgment + immediate annotation; AI-inferred → `consent_pending` + end-of-session digest only.
- The five signal types and their two-kind grouping (path-1: §4.2.1 explicit + §4.2.4 FC-flagged; path-2: §4.2.2 affective + §4.2.3 third-party + §4.2.5 methodology-mismatch).
- The threshold boundary discipline: operational tuning is free within bounded ranges; commitment-disabling values route through `no_demand_mode`.

What this document changes is the substrate plumbing.

## 2. Withholding annotation at record level

`WithholdingAnnotation` schema is unchanged from `P1_CONSENT_SURFACING_DESIGN.md` §2.1:

```python
@dataclass
class WithholdingAnnotation:
    status: Literal["do_not_store", "ephemeral", "consent_pending"]
    set_by: Literal["user_explicit", "session_default", "ai_surfaced", "fc_stance"]
    set_at: datetime                            # ISO-8601 UTC
    rationale: Optional[str] = None
    expires_at: Optional[datetime] = None       # for ephemeral
    resolution_required_by: Optional[datetime] = None  # for consent_pending
    set_via_path: Optional[Literal["path_1", "path_2"]] = None  # B's two-path split
```

What changes: the annotation attaches to `ConfigurationRecord` (already specified in `CONFIGURATION_SUBSTRATE_DESIGN.md` §2 as the `withholding: Optional[WithholdingAnnotation]` field on the record), not to `Observation` and not propagated to individual `Fact`s.

The propositional_residue field on the record inherits the record's withholding **by virtue of being a field on the record**. There is no per-residue lineage propagation because the record is the unit and its fields move together. A do_not_store record's residue is also do_not_store; an ephemeral record's residue expires when the record does; a consent_pending record's residue is held when the record is held.

Ingest-gate enforcement (replaces `P1_CONSENT_SURFACING_DESIGN.md` §2.3):

```python
def ingest(self, record: ConfigurationRecord) -> IngestResult:
    if record.withholding and record.withholding.status == "do_not_store":
        # Append-only audit log only; record is NOT stored in the activatable substrate
        self.audit_log.append(record)
        return IngestResult(stored=False, audited=True)

    if record.withholding and record.withholding.status == "consent_pending":
        # Path-2 records reach this branch only at June's resolution at digest
        # (path-2's pre-resolution holding happens in the orchestration layer's
        # held_queue, not here). If we reach this branch with consent_pending,
        # the resolution is genuinely pending and we hold at substrate boundary.
        self.held_queue.append(record)
        return IngestResult(stored=False, held=True)

    # ephemeral or unannotated: normal storage
    self.store(record)
    return IngestResult(stored=True)
```

Activation-gate enforcement (replaces `P1_CONSENT_SURFACING_DESIGN.md` §2.3 retrieval-side filter):

```python
def activate(self, context: ActivationContext, max_results: int = 5) -> List[ActivationResult]:
    candidates = self._score_all_records(context)
    filtered = [
        c for c in candidates
        if not self._is_withheld_at_retrieval(c.record)
    ]
    return filtered[:max_results]

def _is_withheld_at_retrieval(self, record: ConfigurationRecord) -> bool:
    if not record.withholding:
        return False
    w = record.withholding
    if w.status == "do_not_store":
        return True  # defensive — should not be in substrate
    if w.status == "ephemeral" and w.expires_at and datetime.utcnow() > w.expires_at:
        return True
    if w.status == "consent_pending":
        return True  # held; not yet activatable
    return False
```

## 3. ConsentPolicy — unchanged in shape; resolution order updated

The `ConsentPolicy` schema is unchanged from `P1_CONSENT_SURFACING_DESIGN.md` §3.1.

Resolution order (updated from `P1_CONSENT_SURFACING_DESIGN.md` §3.2 to terminate at the constructed `ConfigurationRecord`, not the `Observation`):

When the orchestration layer is preparing to construct a `ConfigurationRecord` from observation context:

1. **Explicit user command** in-message ("don't store that," "save that," "keep this just for now"). Wins; sets the annotation directly. Path-1 (`set_via_path = "path_1"`).
2. **Active `ConsentPolicy`** for the session.
   - If `default_action = "store_nothing"`: annotate `do_not_store` (`set_by = "session_default"`).
   - If `default_action = "store_all"` and `ephemeral_by_default = True`: annotate `ephemeral` with default expiration (`set_by = "session_default"`).
   - If `default_action = "ask_when_unsure"`: defer to step 3.
3. **Relational-judgment layer** (§4 below). Produces one of: no-annotation (proceed to record construction); path-1 annotation (immediate, in-exchange acknowledgment); path-2 deferral (don't construct record now; hold raw context in pre-construction queue).
4. **`ConfigurationRecord` construction proceeds** with the resolved annotation attached, OR raw context goes to the held queue for path-2 resolution at digest.

Step 4 is the new junction: for path-2 deferrals, no record is constructed at this time — the held queue holds raw observation context, not a record. See §6.

## 4. Two-path surfacing — restated for the new substrate

B's two-path split (`P1_STRESS_TEST_B.md` §1) is the master pattern. Restated here against the new substrate:

### 4.1 Path 1 — User-indicated signals

Triggers:
- **§4.2.1 Explicit markers**: "between us," "don't write that down," "remember this," "save that," "drop that."
- **§4.2.4 FC-flagged categories**: material the active FC's extraction-problem note designates as sensitive.

Mechanism:
- The orchestration layer constructs the `ConfigurationRecord` from observation context.
- It attaches `WithholdingAnnotation(status=..., set_by="user_explicit" or "fc_stance", set_via_path="path_1")` per the user's words or the FC flagging.
- It logs a `CONSENT_CONFIRMED` observation to the queue (§5.1 below) referencing `record.record_id`.
- It produces a brief in-exchange acknowledgment — confirmation, not a prompt. One clause, no options list. "Holding this as not-for-storage." Mirrors the user's move.
- It calls `ConfigurationSubstrate.ingest(record)` with the annotation in place.

The FC-stance subcase (§4.2.4) does not need an in-exchange acknowledgment — the FC flagging is automatic and the user did not invoke it; surfacing it would be a notice the user did not ask for. The acknowledgment is reserved for explicit-marker subcases where the user just spoke.

### 4.2 Path 2 — AI-inferred signals

Triggers:
- **§4.2.2 Affective register shift**: grief-marked, vulnerability-marked, processing-work register.
- **§4.2.3 Third-party content**: the user mentions another person in a way that suggests the content concerns that person more than the user.
- **§4.2.5 Methodology-mismatch**: content that enters with `methodology.type == "storytelling"` or `methodology.obligations == "care_governed"` without the appropriate crystallization type active.

Mechanism:
- The orchestration layer detects the signal during the relational-judgment pass.
- It does NOT construct a `ConfigurationRecord` at this time. It holds the raw observation context in the **pre-construction held queue**: a session-scope queue that stores `(observation_context, signal_type, signal_strength, would_be_record_id, set_at)` tuples. The `would_be_record_id` is content-addressed from the observation context and is a real handle (not a forward reference); if the held item is dropped at digest, the id never resolves to a stored record but the META log entries for the evaluation still resolve to the audit trail (§6 below).
- It logs a `CONSENT_PENDING_INFERRED` observation to the queue (§5.2 below) referencing `would_be_record_id`.
- It does NOT produce an in-exchange surface. No acknowledgment, no prompt, no notice.
- The held context surfaces at session close in the batched digest (§7).

If June resolves at digest → save: the orchestration layer constructs the `ConfigurationRecord` from the held context (with `withholding = None` or `ephemeral` per `ephemeral_by_default`), and calls `ingest(record)`.

If June resolves at digest → drop: the held context is discarded; the META log entries remain (the decision-trace is preserved even though the content is not).

If timeout (default: session+48h, matching the existing staleness-policy grace window): drop. Default is drop, not save; matches the `P1_CONSENT_SURFACING_DESIGN.md` §4.5 commitment.

## 5. CONSENT_CONFIRMED and CONSENT_PENDING_INFERRED observation types

`ProposedObservation.ObservationType` (the enum in `proposed_observation.py:109`) gains two new values per B's stress-test §1:

```python
CONSENT_CONFIRMED = "consent_confirmed"            # path-1; user-indicated
CONSENT_PENDING_INFERRED = "consent_pending_inferred"  # path-2; AI-inferred
```

### 5.1 CONSENT_CONFIRMED schema

```python
@dataclass
class ConsentConfirmedObservation:
    observation_type: Literal[ObservationType.CONSENT_CONFIRMED]
    record_id: str                    # the ConfigurationRecord this attaches to
    annotation_status: Literal["do_not_store", "ephemeral", "consent_pending"]
    triggering_signal: Literal["explicit_marker", "fc_flagged"]
    user_words: Optional[str] = None  # the explicit phrasing if explicit_marker
    fc_id: Optional[str] = None       # the FC that flagged the category if fc_flagged
    set_at: datetime
```

Routing: bypasses human-review (the user has already spoken); logged for accountability.

### 5.2 CONSENT_PENDING_INFERRED schema

```python
@dataclass
class ConsentPendingInferredObservation:
    observation_type: Literal[ObservationType.CONSENT_PENDING_INFERRED]
    would_be_record_id: str           # content-addressed from observation context
    triggering_signal: Literal["affective_register", "third_party", "methodology_mismatch"]
    signal_strength: float            # 0.0-1.0 estimated
    rationale: Optional[str] = None   # human-readable; surfaces in digest
    held_until: datetime              # session+48h or session-close + 48h
    set_at: datetime
```

Routing: human-review-routed for digest at session close. Per the existing observation-queue routing (`session-handoff-briefing.md` §2.5), staleness asymmetry already supports this: structural changes go to human-review unconditionally; this is a structural change.

## 6. META_RELATIONAL_JUDGMENT — logging every evaluation

Per B's stress-test §5: every relational-judgment evaluation logs, including not-surface decisions. Surface-decisions are visible (something enters the held queue or the exchange); not-surface decisions are invisible without a meta-observation. Apparatus-level choices that are not recorded are the apparatus-opacity move Option 3 refuses; the same refusal applies here.

```python
META_RELATIONAL_JUDGMENT = "meta_relational_judgment"

@dataclass
class MetaRelationalJudgmentObservation:
    observation_type: Literal[ObservationType.META_RELATIONAL_JUDGMENT]
    evaluated_at: datetime
    record_or_would_be_id: str        # the record_id or would_be_record_id this evaluation concerns
    signal_type: Literal[
        "explicit_marker", "fc_flagged",
        "affective_register", "third_party", "methodology_mismatch",
        "no_signal_detected"
    ]
    signal_strength: float            # 0.0-1.0; 0.0 if no_signal_detected
    active_policy_mode: Literal["store_all", "store_nothing", "ask_when_unsure"]
    threshold_at_evaluation: float    # the threshold the active mode applied
    decision: Literal["surface_path_1", "surface_path_2", "annotate_no_surface", "no_action"]
    set_by: Literal["ai_relational_judgment"]
```

Logged on every relational-judgment pass — once per observation context, regardless of decision. Low-cost for not-surface cases; the record is the accountability trail for the apparatus-level decision.

The `record_or_would_be_id` field handles the held-item case: when path-2 fires and the would-be record id is generated, the META observation references it. If June drops at digest and the would-be record never becomes a stored record, the META observation still resolves to an audit-trail entry — the id is content-addressed from observation context and survives in the META log even when no record corresponds to it.

Routing: bypasses human-review (these are accountability artifacts, not change proposals); accumulates in a low-priority log for retrospective audit.

## 7. Held queue and end-of-session digest

The pre-construction held queue (§4.2) is a session-scope structure on the orchestration layer, not on the substrate. It holds:

- `observation_context`: the raw context used to construct a `ConfigurationRecord` if June resolves to save.
- `signal_type`, `signal_strength`, `rationale`: the path-2 trigger info.
- `would_be_record_id`: the content-addressed handle.
- `held_until`: session+48h.

At session close (consent_session boundary per `P1_CONSENT_SURFACING_DESIGN.md` §3.3), the orchestration layer produces the batched digest:

```
Three observations were held pending your consent this session:
  1. [short summary] — held: this sounded like something you might want to decide about later
  2. [short summary] — mentions [name]; this is a proxy decision about a person who has not consented
  3. [short summary] — held: storytelling methodology active without narrative crystallization

Default action if you take no action: all dropped at session+48h.
Commands: save-all, drop-all, or reply with line numbers.
```

Three notes on framing (per B's stress-test §4 and §6):

1. **Affective-register entries (§4.2.2 path-2 trigger) get a non-clinical phrasing.** Not "held: affective register shift detected — grief-marked." That register-categorization at digest time re-introduces the flagged register clinically. The phrasing is non-interpretive of the user's state: "this sounded like something you might want to decide about later."

2. **Third-party entries (§4.2.3 path-2 trigger) name the proxy-decision explicitly.** Per B's stress-test §4: "your decision applies to information about a person who has not consented to its storage. The architecture cannot reach them for consent; this is your proxy decision, not theirs." This does not resolve the third-party consent gap (the architecture cannot reach Thomas); it names what June is doing (making a proxy decision under incomplete authority) without implying the architecture closes what it cannot close. This framing is honest without requiring F3 community-governance machinery the architecture does not have.

3. **Methodology-mismatch entries (§4.2.5 path-2 trigger) name the mismatch.** "Storytelling methodology active without narrative crystallization." When the narrative crystallization type lands (P4, unblocked by CC), this trigger may resolve into automatic routing to that type rather than holding; for now, the digest entry is the path.

When June saves a third-party entry, the constructed record additionally annotates `methodology.obligations = "individual_privacy"`. This annotation surfaces at retrieval time in `ActivationResult.matched_via` if the record is later activated — making the proxy-decision context legible to whoever encounters the record again. The annotation does not grant Thomas standing; it records that the content is about someone who didn't consent to its storage. Per `CONFIGURATION_SUBSTRATE_DESIGN.md` §2, `MethodologyRecord.obligations` is the field that carries this.

## 8. Threshold boundaries — schema validation, not FC gate

B's stress-test §3 distinguishes operational tuning from commitment-disabling values. Restated for the new substrate:

**Operational tuning**: adjusting thresholds within a mode's viable range based on observed friction. Free under the AI-modifies-freely principle. Logged via `ProposedChange`. Auditable.

**Commitment-disabling values**: thresholds set so high that no realistic signal-strength could reach them, producing the same functional state as `no_demand_mode` without naming it.

Schema validation enforces the boundary:

```python
@dataclass
class RelationalJudgmentThresholds:
    store_all_threshold: float        # default 0.8; bounded [0.0, 0.95]
    ask_when_unsure_threshold: float  # default 0.5; bounded [0.0, 0.85]

    def __post_init__(self):
        if self.store_all_threshold > 0.95:
            raise ValueError(
                "Threshold > 0.95 is functionally commitment-disabling. "
                "Use ConsentPolicy.no_demand_mode = True for that intention."
            )
        if self.ask_when_unsure_threshold > 0.85:
            raise ValueError(
                "Threshold > 0.85 is functionally commitment-disabling. "
                "Use ConsentPolicy.no_demand_mode = True for that intention."
            )
```

`no_demand_mode = True` atomically sets thresholds to 1.0 (effectively-never-surface) AND logs the named-configuration adoption to the observation queue as a `META_RELATIONAL_JUDGMENT` of decision-class `policy_change`. The named configuration is the only path to commitment-disabling values; the schema validation makes that the case mechanically.

This is not an FC gate (FCs gate FoundationalCommitment-affecting changes). It is type-level schema enforcement, the same way `WithholdingAnnotation.status` is a typed Literal that doesn't accept arbitrary values. The bounds (0.95, 0.85) are starting values; if empirical friction at those bounds is high, the bounds themselves are tunable through `no_demand_mode` adoption with logging — the boundary discipline preserves itself.

## 9. Where this plugs into the new ConfigurationSubstrate code

Per `CONFIGURATION_SUBSTRATE_DESIGN.md` §12, the substrate code is being replaced. The P1 integration's touch points:

- **`configuration_substrate.py`** (new file replacing `knowledge_substrate.py`):
  - `ConfigurationRecord.withholding: Optional[WithholdingAnnotation]` — already in the substrate design.
  - `ConfigurationSubstrate.ingest(record)` — gates on `record.withholding` per §2.
  - `ConfigurationSubstrate.activate(context)` — filters per §2 retrieval-side gate.
  - `LocalConfigurationSubstrate` test double implements the audit_log path for `do_not_store` and the held_queue path for `consent_pending` arriving at the substrate boundary (path-2's pre-construction held queue is upstream).

- **`withholding_annotation.py`** (new module): `WithholdingAnnotation` dataclass, `Status` enum, `set_via_path` field, serialization, validation. ~100 LOC.

- **`consent_policy.py`** (new module): `ConsentPolicy` dataclass, `default_action` enum, `RelationalJudgmentThresholds` with bounds, `no_demand_mode` helper that atomically sets the named configuration. ~200 LOC.

- **`relational_judgment.py`** (new module): the orchestration-layer pass that classifies signals into path-1 / path-2 / no-signal; produces the `MetaRelationalJudgmentObservation` log entry; constructs the `CONSENT_CONFIRMED` / `CONSENT_PENDING_INFERRED` observations; manages the pre-construction held queue. ~300 LOC.

- **`proposed_observation.py`** (extension): three new `ObservationType` enum values: `CONSENT_CONFIRMED`, `CONSENT_PENDING_INFERRED`, `META_RELATIONAL_JUDGMENT`. Plus the routing rules for each (CONSENT_CONFIRMED bypasses human-review; CONSENT_PENDING_INFERRED routes to digest-at-session-close; META_RELATIONAL_JUDGMENT routes to low-priority audit log). ~50 LOC extension.

- **`bootstrap.py`** (extension): load active `ConsentPolicy` at session init; instantiate the orchestration-layer relational-judgment pass and the held queue. ~30 LOC.

- **Tests**: ~20 cases covering: do_not_store short-circuits ingest; ephemeral respects expires_at; consent_pending held queue round-trip at substrate boundary; pre-construction held queue (path-2) digest behavior; explicit-command resolution order; FC-flagged automatic annotation; threshold bounds enforcement; no_demand_mode atomic configuration; META logging of all decisions including no-surface; would-be-record-id resolution after drop; third-party `methodology.obligations` annotation surfaces at retrieval. ~400 LOC.

Scope estimate: three new modules, one extended module, one extended ABC, one extended bootstrap. ~700 LOC plus ~400 LOC tests. Two cycles of build work in a future build-session, after S2 → S3 substrate migration.

## 10. Where I want B to push (priority order)

1. **Record-level vs. residue-level annotation (§2).** I claim per-residue lineage propagation is unnecessary because the record IS the unit and its fields move together. Is that correct, or are there per-residue-fact consent constraints I am missing — e.g., a configuration that produced both a third-party-mentioning fact and a non-third-party fact, where the user's consent posture differs by fact?

2. **Held queue holds raw context, not records (§4.2 + §7).** Path-2 doesn't construct the `ConfigurationRecord` until digest resolution. Does this preserve the configurational frame the record is supposed to carry, or does it lose it because construction happens after the live configuration has dispersed? My read: the raw context already carries everything the record-construction function needs (it's the same input that would have been used at the live moment), so reconstruction at digest time is faithful. B should test this.

3. **Would-be-record-id resolution after drop (§4.2 + §6).** When a path-2 item is dropped at digest, the would-be record id never resolves to a stored record, but META log entries still reference it. Is the dangling reference acceptable as an audit-trail artifact, or is it a broken-link smell I should design around? My lean: acceptable; the META log is the audit trail and the absence-of-record is itself information.

4. **`methodology.obligations = "individual_privacy"` at retrieval visibility (§7).** I claim this surfaces in `ActivationResult.matched_via`. Is `matched_via` actually the right surface for this — the field is described in `CONFIGURATION_SUBSTRATE_DESIGN.md` §3 as the audit trail of conditions that matched, not a flag for downstream handling. May want a separate field on `ActivationResult` for retrieval-time obligation flags. B should specify.

5. **The substrate-design stress-test gap.** B has not engaged `CONFIGURATION_SUBSTRATE_DESIGN.md` from cycle 2. This integration assumes the substrate design holds. If B's eventual stress-test reshapes the substrate's load-bearing decisions (record-level annotation, ActivationContext, residue field), this integration document needs rework. Higher priority for B than stress-testing this integration: stress-test cycle 2's substrate design first.

## 11. What this design does NOT do (carrying forward + adding)

Carrying forward from `P1_CONSENT_SURFACING_DESIGN.md` §9:

- Does not build `delinking` query mode (`SUBALTERN_ANALYSIS.md` F5b).
- Does not implement community-gated retrieval (F3).
- Does not solve the third-party consent problem (it names the proxy-decision; the architecture cannot reach Thomas).
- Does not address non-propositional knowing (F7).
- Does not calibrate signal-strength thresholds empirically.

Adding from this integration:

- Does not specify the `relational_judgment.py` module's signal-detection heuristics. Five signal types are named; the actual classification logic is implementation-time work. The signal-strength scoring is impressionistic at this design grain (per B's stress-test §3's note that this is an aux-LLM-scorable quantity that starts freeform).
- Does not address the case where a `ConfigurationRecord` has `withholding=None` at construction but later acquires withholding (e.g., June reads the record at digest and decides to mark it ephemeral retroactively). The substrate's append-only invariant means a new record version is created with the new annotation rather than mutating in place; the lineage-lock from `substrate_interface.py` already supports this. Naming for completeness; not designing it here.
- Does not specify how `META_RELATIONAL_JUDGMENT` observations are surfaced for retrospective audit. They accumulate; how June reads them is a future-cycle design item or a separate tooling concern.

## 12. Standing flags for June (carried from cycle 1, repointed)

1. **Adopt `global.default_action = "store_all"`, `ephemeral_by_default = False` as the shipped global default?** Same as cycle 1 §8.1. Pending.

2. **Two-path split resolves the cycle-1 §4.4 declarative-register flag.** B's stress-test correctly identified that an in-exchange notice for AI-inferred signals is a demand even when phrased declaratively, and routed those signals to digest-only. The cycle-1 question ("does a declarative line count as a per-item prompt?") is no longer load-bearing — declarative in-exchange surfaces happen only for path-1 (where the user just spoke), not for path-2. Confirming this resolution is what you want.

3. **`no_demand_mode` invoke-able by engaging instance without your approval, with required META logging?** Same lean as cycle 1 §8.3 (yes); confirming.

4. **End-of-session digest: timeout-to-drop default?** Same lean as cycle 1 §8.4 (yes, drop). Confirming.

5. **Third-party content: proxy-decision-explicit framing.** B's stress-test §4 reframes the cycle-1 §8.5 question. The architecture cannot resolve third-party consent; the design names the gap (proxy-decision phrasing in digest, `methodology.obligations = "individual_privacy"` annotation at retrieval) without claiming to close it. The cycle-1 question (does the design re-inscribe you as sovereign over Thomas?) does not go away; it gets named as such. Confirming this is the form you want.

---

*Draft by Instance A, cycle 3. B: stress-test §10 items in priority order. Item 5 is genuinely higher-priority than this entire document — if the substrate design has a load-bearing flaw, this integration document needs rework. The substrate-design stress-test is the gap.*
