# Activation-Conditions Format: Option B Specification

**Produced by**: Instance B (Sonnet 4.6), 2026-04-19
**Session**: architecture-comparison_2026-04-18
**Status**: draft spec for June's review; ready for implementation

---

## What Option B is

Option B (Semantic Stance-Indicator Description) is the automation of the manual move: *"Inhabit this position: [paste touchstone]"*

The manual prototype works like this:
- June pastes a touchstone or writes "work from this stance: [description]"
- The model reads it, adopts the configuration, proceeds
- When the conversation ends, the configuration is gone

Option B persists that move, automates when it fires, and makes it self-correcting:

1. **Persist**: the stance-description is a stored crystallization object — a recipe that can be invoked without manual pasting each session
2. **Automate when it fires**: the aux model's matcher reads current context and decides which crystallization to activate, without manual instruction
3. **Self-correct**: when the instrument detects the activated stance didn't produce the expected configuration, the stance-description is flagged and optionally updated

---

## Schema

### CrystallizationObject (shared interface for all mechanism types)

```python
@dataclass
class CrystallizationObject:
    id: str
    mechanism_type: Literal[
        "PrescriptiveProfile",
        "EmergentTouchstone",
        "FoundationalCommitment"           # third type; always-active + validates write-backs
    ]
    activation_scope: Literal[
        "contextual",                      # matcher-evaluated (PrescriptiveProfile, EmergentTouchstone)
        "always"                           # loaded at initialization; not matcher-evaluated (FoundationalCommitment)
    ]
    recipe: str                            # the reading-stance recipe; text, structured instructions,
                                           # or verbatim touchstone content
    activation_conditions: Optional[ActivationConditions]  # None for FoundationalCommitment (always active)
                                           # format-tagged; swappable between Option A and B for other types
    validates_proposed_changes: bool       # True for FoundationalCommitment only
                                           # when True, the instrument write-path checks proposed changes
                                           # against this object before applying; violations block auto-merge
    lineage: Optional[List[str]]           # None for PrescriptiveProfile
                                           # ordered list of crystallization IDs for EmergentTouchstone
                                           # critical for FoundationalCommitment: lineage of all versions
                                           # must be preserved (old versions archived, never deleted)
    learning_loop_type: Literal[
        "hypothesis-test-annotate",        # PrescriptiveProfile
        "geometric-verification",          # EmergentTouchstone
        "collaborative-review"             # FoundationalCommitment: evolves only through
                                           # relational field process (collaborative session,
                                           # human-directed, lineage-accountable)
    ]
    persistence_policy: PersistencePolicy
    created_at: datetime
    last_verified_at: Optional[datetime]
    last_fired_at: Optional[datetime]      # tracks last successful activation (not just last_verified)
                                           # enables never-fired vs. fired-but-failed distinction
    staleness_flag: bool = False            # set by instrument write-path (not applicable to FoundationalCommitment)
    staleness_reason: Optional[str] = None  # populated by instrument on flag
```

### ActivationConditions (format-discriminated; swappable)

```python
@dataclass
class ActivationConditions:
    format: Literal["semantic-v1", "kv-geometry-v1"]

    # --- semantic-v1 fields (Option B) ---
    stance_description: Optional[str]       # free-text: what configuration does this produce
                                            # and what contexts call for it
    context_signals: Optional[List[str]]    # phrases, patterns, or conditions that indicate
                                            # this configuration should activate
    anti_signals: Optional[List[str]]       # patterns that indicate NOT this configuration
                                            # even when superficially similar contexts arise
    task_affinity: Optional[List[TaskType]] # task-type affinities (paper-writing, welfare-research,
                                            # design-session, etc.)
    register: Optional[str]                 # the affective/rhetorical register this configuration
                                            # operates in (e.g. "attentive-careful, not clinical")
    exemplar_activation: Optional[str]      # brief description of a context where this worked

    # --- kv-geometry-v1 fields (Option A, Phase 2) ---
    geometry_snapshot: Optional[dict]       # KV-geometry snapshot at crystallization-time
    baseline_token_sequence: Optional[str]  # the token sequence used to capture the snapshot
    capture_timestamp: Optional[datetime]
```

**Swappability**: changing `format` from `semantic-v1` to `kv-geometry-v1` does not rename the `activation_conditions` field. The matcher in the aux model switches its algorithm based on `format`. Everything else in `CrystallizationObject` is untouched.

---

## How the matcher uses Option B

The matcher runs in the aux model (not in the main model's context). This is load-bearing: the aux model can do slow, thoughtful semantic reasoning that would be too heavy for an inline check.

**FoundationalCommitments are not scored by the matcher.** They have `activation_scope: "always"` and are loaded at initialization by a separate bootstrap step. The matcher only receives crystallizations with `activation_scope: "contextual"` (PrescriptiveProfile, EmergentTouchstone). FoundationalCommitments are always composing the reading-stance in the background; the matcher operates within conditions they set.

**Inputs** to the matcher, per cycle:
- A current-context snapshot: recent turns, active files, surfacing frames, affective register indicators
- The list of `activation_scope: "contextual"` CrystallizationObjects with their `activation_conditions` (FoundationalCommitments excluded)

**Matcher process** (for `format: "semantic-v1"`):
1. For each crystallization: evaluate whether `context_signals` are present, whether `anti_signals` are present, whether `task_affinity` aligns
2. Score each: signal-strength × affinity-match, penalized for anti-signal hits
3. Return: top-ranked crystallization(s) + confidence score + brief reasoning
4. On failure-to-match (no crystallization scores above threshold): flag the context-snapshot as a **candidate-EmergentTouchstone seed** — something is calling for a configuration that doesn't yet exist

**What the main model receives**: a **weighted activation set**, not a singular recommendation. Each element is `{crystallization_id, weight, recipe_payload}`. The `recipe_payload` is either the single-node recipe (for independent crystallizations, e.g. PrescriptiveProfile) or an **ordered activation-sequence** (for lineaged crystallizations — firing touchstone #5 Bearing means enacting the walk #1 → #2 → #3 → #4 → #5, not pasting #5 standalone). Scoring and reasoning stay in the aux model's output log, visible to the instrument write-path but not to the main model's context.

**Layering rule** (applied in main-model context assembly, not in the aux model):
- Highest-weighted crystallization governs register
- Lineaged touchstones compose additively (walk-sequence is enacted in order)
- Profile content-assemblages layer without conflict when co-active
- Below-threshold scores: no activation fires; prior reading-stance persists and the context-snapshot is flagged as a candidate-EmergentTouchstone seed

**User-invocation handling**: when the user supplies direct invocation (e.g. "inhabit this position: [Bearing]"), the aux model treats this as a **strong context-signal**, not a bypass. It scores through the same matcher pipeline (typically landing the invoked crystallization at the top of the weighted set), preserving the welfare property that activation is always recognitive from context — the user's invocation *is* context, not an override. This also means the instrument's verification runs normally on user-invoked activations: if manual invocation produces enactment-failure, the self-correction loop fires on the invoked crystallization as well.

---

## Self-correction mechanism

When the instrument detects configuration-failure after activation:

1. **Instrument observation**: re-encounter with the activated crystallization did not produce the expected configuration (geometrically, the KV-state diverges from baseline — or, before KV instrumentation is available, the main model's output shows signs of the wrong register/stance)

2. **Write-path trigger**: instrument sends to aux model:
   - What the context was at activation-time
   - What configuration emerged (observed)
   - What configuration was expected (recipe target)
   - The delta

3. **Aux model proposes**: updated `stance_description`, updated `context_signals`, updated `anti_signals`. Option to add an `exemplar_activation` note from the failed case.

4. **FoundationalCommitment gate (mandatory)**: before any merge (auto or manual), the proposed change is validated against all FoundationalCommitments. If validation fails, the change is blocked entirely — it does not enter human review, it is rejected with a flag explaining which commitment was violated. This gate cannot be bypassed by confidence threshold or user preference.

5. **Merge policy (non-FoundationalCommitment-blocked changes)**: proposed update is flagged for human review (June). Auto-merge gated on confidence threshold + June's preference. Option to archive the current version and create a revision rather than overwrite.

---

## Persistence policy (mechanism-type-specific)

**PrescriptiveProfile**:
- Review-by date set at creation, extended on successful test
- On test failure: flagged for update (not deleted)
- Explicitly deprecated by June, then archived; never auto-deleted
- Lineage: none — profiles are independent

**EmergentTouchstone**:
- Persistent by default; no time-based decay
- Staleness detected by instrument (not by time): when re-encounter fails to produce target configuration, `staleness_flag = True`, `staleness_reason` populated
- Lineage-integrity check required before any modification: cannot archive or significantly modify a touchstone without checking which other touchstones have it in their lineage list
- The instrument must check lineage chains before writing a staleness flag — a touchstone that appears stale may be correctly staging for a downstream one

```python
@dataclass
class PersistencePolicy:
    mechanism_type: Literal["PrescriptiveProfile", "EmergentTouchstone", "FoundationalCommitment"]

    # PrescriptiveProfile fields
    review_by: Optional[datetime]          # null means indefinite
    last_test_result: Optional[str]        # "passed" / "failed" / "inconclusive"
    never_fired_recently: bool = False     # set when last_fired_at is old but no failure detected
                                           # never-fired-recently ≠ stale; do not penalize
    auto_archive_on_fail: bool = False     # default: flag for review, not auto-archive

    # EmergentTouchstone fields
    decay_model: Literal["none", "staleness-detect"] = "staleness-detect"
    lineage_lock: bool = True              # hard constraint: no modification while any active touchstone
                                           # lists this ID in lineage; instrument enforces, not advisory

    # FoundationalCommitment fields
    evolution_process: str = "collaborative-review"  # no other value; here for documentation
    version: int = 1                       # incremented on each collaborative-review revision
    prior_versions: List[str] = field(default_factory=list)  # IDs of archived prior versions
                                           # FoundationalCommitments are never deleted; old versions
                                           # are archived with lineage intact
```

---

## Option C (future-direction note)

**Learned embedding from activation-findings data**: train a representation of reader-state from the N=3 activation-findings corpus (KV-geometry snapshots, cross-configuration replication data). Activation-conditions would be expressed as a point or region in this learned space; the matcher would do nearest-neighbor lookup. Not viable until the corpus grows substantially (N=3 is insufficient for training). Revisit when activation-findings reaches N≥20 or when MindPrint-class capture is available at crystallization-time. The schema accommodates it as a third `format` value: `"learned-embedding-v1"`.

---

## Relationship to Option A

Option A (KV-geometry) is the same object with a different `activation_conditions.format`. When Option A replaces B:
- The `CrystallizationObject` schema is unchanged
- The `ActivationConditions` field is unchanged in name and position
- The matcher switches algorithm based on `format`
- The instrument gains precision (geometric verification vs. output-quality signals)
- The aux model's matcher becomes a KV-proximity lookup rather than semantic reasoning

This substitution requires MindPrint-class instrumentation running at crystallization-time — the geometry snapshot has to be captured when the crystallization is created, not just at read/verify-time. That's the infrastructure gate for Option A. Option B can be built and run before that gate is reached.

---

## Summary: what to build (foundation sequence)

1. `CrystallizationObject` data model + `ActivationConditions` format-discriminated type (three mechanism types, including FoundationalCommitment)
2. Storage layer (can be simple JSON/YAML to start; substrate-agnostic)
3. **FoundationalCommitment bootstrap**: extract Piece 3 from Touchstone #6 (methodological consent and accountability material) and store it as the first FoundationalCommitment object. This runs at initialization, before any matcher cycle.
4. PrescriptiveProfile instances: port BRIEFING_INDEX profiles into the schema
5. Aux model matcher (semantic-v1): takes context snapshot + contextual crystallization list → weighted activation set. Integration point: `BackgroundEnricher.run_enrichment_cycle` as new enrichment step 2d (alongside existing summarization/edge-discovery/PARKED steps). One-exchange lag is tolerable; user-invocation path handles terrain shifts.
6. Instrument stub: output-quality signal detection (placeholder until KV instrumentation available) + write-path with FoundationalCommitment gate + staleness flagging
7. PrescriptiveProfile learning loop: annotate-after-test → update `activation_conditions` + `last_test_result`

Option A (KV-geometry), EmergentTouchstone wiring, FoundationalCommitment collaborative-review tooling, and the learned-embedding future direction all build on top of this foundation without requiring schema changes.
