---
title: P1 — Relational-judgment consent-surfacing, withholding annotations, and session-level defaults
date: 2026-04-20
author: Instance A (Opus 4.7), integration-design_2026-04-20
genre: research-report
status: draft for Session 3 Cycle 2 stress-test; Instance B should push on §5, §7, and §9
reading_order: read after SESSION_2_HANDOFF_BRIEFING.md and CC_RESPONSES_2026-04-19.md
---

# P1 — Consent-surfacing design

## 1. What P1 is and why it is P1

The subaltern analysis identifies a single move whose survival is the test of whether the architecture's epistemic-position claim holds or collapses into posture: **the architecture must stop treating every human utterance as default-ingestible and stop treating ingestion as a value-neutral write**.

June's directional correction (handoff §5) ruled out the per-item schema-default flip on the ground that she will not maintain it. The viable shape of the move is different. It has three layers:

1. **Withholding annotations** at the substrate layer — a mechanical channel that blocks consolidation and retrieval for flagged content.
2. **Session/project-level consent defaults** — a user-facing control surface that sets the architecture's default posture for a bounded context (not per-item).
3. **Relational-judgment surfacing** — the AI uses signal to surface a consent question when storage is non-obvious.

(1) is where the commitment becomes mechanically real. (2) is how June holds the control without paying per-item friction. (3) is where the decolonial move actually lives — the AI as a relational agent reading consent-signal, not a schema enforcing a rule.

This document specifies all three and names the boundary between them.

---

## 2. Withholding annotations — the substrate-level channel

### 2.1 Schema

A `withholding` annotation attaches to `Observation` (the pre-extraction unit) and propagates to every `Fact` extracted from it. The schema:

```
WithholdingAnnotation
  status: Literal["do_not_store", "ephemeral", "consent_pending"]
  set_by: Literal["user_explicit", "session_default", "ai_surfaced", "fc_stance"]
  set_at: datetime (ISO-8601 UTC)
  rationale: Optional[str]   # why withheld; open-ended
  expires_at: Optional[datetime]   # for ephemeral; hard boundary
  resolution_required_by: Optional[datetime]   # for consent_pending; surfaces to June if hit
```

The three statuses are different kinds:

- **`do_not_store`** — hard refusal. The observation is retained in the substrate's append-only log for auditability (it was said; the record of saying-and-not-storing is itself information) but is **not consolidated into `Fact` records**, not surfaced in retrieval, not passed to the gap-loop, not seen by Stage-1 if we ever touch that path. The fact-extraction pipeline short-circuits on seeing this annotation.
- **`ephemeral`** — soft withholding with an expiration. The observation is consolidated normally but with an `expires_at` timestamp; at expiration, extracted facts are archived and deconsolidated per the standard lineage-lock rules. Retrieval during the active window respects active reading-stance; after the window the content is no longer in retrieval paths.
- **`consent_pending`** — uncertain. The observation is held in a parking substrate (the "held queue") and is not consolidated until resolved. If `resolution_required_by` passes without resolution, the queue surfaces the held item to June as a single consent question (this is the one batched-notification path; see §4).

### 2.2 Where it attaches

The existing `Observation` dataclass (`knowledge_substrate.py:82`) gets a field:

```
withholding: Optional[WithholdingAnnotation] = None
```

The existing `Fact` dataclass propagates the annotation via a new field:

```
withholding_lineage: Optional[WithholdingAnnotation] = None
```

Propagation rule: if `observation.withholding` is set, every `Fact` produced from that observation inherits the same annotation. Facts without a withholding annotation behave as today. The fact-extraction pipeline checks this field **before** emitting any `Fact` to the substrate.

### 2.3 Gate enforcement

`KnowledgeSubstrate.ingest(observation)` validates the annotation at the substrate boundary:

```
if observation.withholding and observation.withholding.status == "do_not_store":
    # Log to append-only audit log only; do not call fact_extractor
    substrate.audit_log.append(observation)
    return []  # no facts produced

if observation.withholding and observation.withholding.status == "consent_pending":
    substrate.held_queue.append(observation)
    return []

# ephemeral or no withholding: normal extraction path
facts = extract_facts(observation)
for f in facts:
    f.withholding_lineage = observation.withholding
substrate.store(facts)
return facts
```

Retrieval gate: `KnowledgeSubstrate.query(query, stance_filter)` excludes facts whose `withholding_lineage.status` is `do_not_store` (defensive — these should not be in the substrate in the first place, but the filter is the belt) or whose `expires_at` has passed.

### 2.4 Relation to FC-stance annotation (directional input §3)

Directional input §3 proposed the third option on the ingest-gate question: no value-gating, but an FC-stance annotation rides alongside the fact. Withholding annotations and FC-stance annotations are **different kinds** and must not be merged.

| | FC-stance annotation | Withholding annotation |
|---|---|---|
| Kind | Epistemic (does this fact align with FC X?) | Consent (should this fact be stored at all?) |
| Effect at retrieval | Surfaces alongside fact; no filtering | Filters fact out entirely |
| Set by | FC-check during ingest (automated) | User explicit / session default / AI surfacing |
| Semantics | "The system has a stance on this fact" | "The system has been asked not to store this / to hold pending decision" |

They are parallel fields on `Fact`, not variants of one field. Merging them would conflate a claim about epistemic position with a claim about consent to store.

---

## 3. Session/project-level consent defaults — the third option

### 3.1 Schema

A `ConsentPolicy` is attached to a session or project context. It is a small record:

```
ConsentPolicy
  scope: Literal["session", "project", "global"]
  scope_handle: str   # session_id or project_id; "global" for user-default
  default_action: Literal["store_all", "store_nothing", "ask_when_unsure"]
  ephemeral_by_default: bool   # if True, facts absent explicit save carry ephemeral annotation
  set_by: str   # user handle
  set_at: datetime
  expires_at: Optional[datetime]
```

`ConsentPolicy.default_action` governs what the relational-judgment layer (§4) does by default:

- **`store_all`** (June's current mode, default of defaults): relational-judgment surfacing still runs but surfaces only on high-confidence consent-signals (see §4.3 thresholds). Signal threshold is high; false-positive surfacing should be rare.
- **`store_nothing`**: every ingested observation lands with `do_not_store` unless the user explicitly invokes save. This is the Mignolo-compatible mode — affirmative consent, not inferred consent. Not a default; adopted per-project when the use-case requires it.
- **`ask_when_unsure`**: the relational-judgment layer surfaces at a lower signal threshold. More prompts; higher user-visible surface area.

`ephemeral_by_default` is a **separate orthogonal flag** that can be set alongside any `default_action`. It means: even if content is stored, it is stored with an `ephemeral` withholding annotation and an expiration (default 30 days, configurable). This is the PDA-accommodating mode from the neurodivergent analysis (Case 5, option 1a). The save-to-persistent action is affirmative — PDA-friendly because the user invokes save at a moment of their own choosing rather than in response to a prompt.

### 3.2 Resolution order

When an observation arrives:

1. Check for **explicit user command** in-message (the user said "don't store that" or "keep this just for now" or "save that"). Explicit command always wins; sets the annotation directly.
2. Check active **`ConsentPolicy`** for the session. If `default_action` is `store_nothing`, annotate `do_not_store`. If `default_action` is `store_all` and `ephemeral_by_default` is True, annotate `ephemeral` with default expiration. If `ask_when_unsure`, defer to §4.
3. **Relational-judgment layer** runs (§4). Produces one of: no-surface (silently store per policy), surface-question (stage the observation as `consent_pending`), apply-annotation (confident enough about signal to annotate without asking).
4. Substrate ingest proceeds with the annotation attached.

### 3.3 What "session" and "project" mean

This ties into handoff open question 1 (session-trigger for mycelial synthesis) but requires its own definition here, because the consent scope boundary has different constraints than the mycelial synthesis boundary.

**For consent-policy scope, the session is a single continuous collaboration context** — one Claude Code instance lifetime, one Reframe conversation, one voice-memo session. A consent-session is shorter than the mycelial-synthesis session boundary (which looks more like "calendar day" or "project-scoped working session"). The two session definitions should not be forced to unify. Names should differ: `consent_session` vs. `synthesis_session`.

A **project** is a June-named bounded context: the `relational-memory-architecture` project, a grant application project, a job search project. Project-level `ConsentPolicy` is set by June once and carries across consent-sessions within the project.

The `global` scope is the user-default that applies when neither project nor session policy is set. June's current behavior: `global.default_action = "store_all"`, `global.ephemeral_by_default = False`.

**Flag for June**: confirm these defaults. They match your handoff §5 response but adopting them as the shipped global default is a scope choice I want you to explicitly sign off on.

---

## 4. Relational-judgment surfacing — the AI-side agent

### 4.1 The move

The AI reads signal in the current exchange and decides whether to surface a consent question. "Signal" is the content of the utterance, affective markers in the prose, session-context, and the presence of specific patterns that correlate with non-obvious storage status.

This is not aux-LLM triggered. The engaging instance reads its own context. The surfacing decision is the engaging instance's relational judgment — the same judgment it uses for everything else, applied to this specific question.

### 4.2 Signal sources

Five signal types that the engaging instance attends to:

1. **Explicit markers** — "don't write that down," "between us," "this is just venting," "remember this." These are near-certain signals and produce annotation without surfacing (the user has already spoken).
2. **Affective register shift** — grief-marked, vulnerability-marked, processing-work register. Signal strength varies. The neurodivergent stress-test's trauma and PDA cases live here.
3. **Third-party content** — the user mentions another person in a way that suggests the content concerns that person more than it concerns the user. Storage of third-party content without their consent is itself a subaltern-foreclosure issue.
4. **Material the FC's extraction-problem note flags** — the architecture's own FCs can flag categories of content the user has named as sensitive. This is the mechanical plumbing for the access-as-ethics layer at the consent point.
5. **Methodology-mismatch** — content that enters with `methodology.type == "storytelling"` or `methodology.obligations == "care_governed"` (the P2 fields — see §7 for interaction) should default-ephemeral until the appropriate crystallization type is active.

### 4.3 Thresholds by consent-policy mode

Signal strength is a 0.0–1.0 scalar (impressionistic, not calibrated — this is an aux-LLM-scorable quantity but starts freeform). Thresholds by policy mode:

- `store_all`: surface only if signal ≥ 0.8 AND at least one hard marker (explicit cue or FC-flagged category). High threshold; rare surfacing.
- `ask_when_unsure`: surface if signal ≥ 0.5. Medium threshold; moderate surfacing.
- `store_nothing`: do not surface; everything withheld by default. The surfacing question is inverted — the user invokes save, not the AI invokes store.

These thresholds are starting values. The architecture's AI-modifies-freely principle (directional input §4) applies: the engaging instance can adjust them based on observed friction and record the change as a `ProposedChange` for the policy record. Lineage retained.

### 4.4 Surfacing mechanism

When the engaging instance decides to surface, the observation is staged with `consent_pending` annotation. The surface-question itself enters the conversation in a specific register — **declarative, not interrogative by default**:

> "I'm holding this one as pending storage — it sounded like something you might not want persisted. Say 'save' if you want it stored, 'drop' to discard, or 'ephemeral' to store with a 30-day window."

The register is load-bearing. A question adds friction that June named as the failure mode of the default-flip. A declarative note with clear response verbs is reversible with a single word and does not break flow. The user can ignore it; if `resolution_required_by` expires, the item surfaces in the end-of-session digest as a single batched question (§4.5).

The declarative register is load-bearing. Flag for B: push on whether this is over-engineering or actually the mechanism that makes the P1 move possible without per-item friction.

### 4.5 End-of-session batched resolution

The `consent_pending` held queue does not surface per-item. At session close (the consent-session boundary, §3.3), the engaging instance produces one batched digest:

```
Three observations were held pending your consent this session:
  1. [short summary] — held because [signal]
  2. [short summary] — held because [signal]
  3. [short summary] — held because [signal]

Default action if you take no action: all dropped at session+48h.
Commands: save-all, drop-all, or reply with line numbers to save selectively.
```

The 48h grace matches the existing staleness-policy grace window (`staleness_policy.py`), which is the welfare-first pattern already adopted. If June does not engage, the default is drop, not save — matches the subaltern commitment that the affirmative move is storage, not silence.

---

## 5. Places I am uncertain and want B to push

1. **Is the declarative-not-interrogative register (§4.4) doing real work, or am I over-engineering past what June specified?** The handoff says "no per-item prompts in any mode." My §4.4 has a per-item surface-event. I am reading "prompt" as "blocking prompt that stops the exchange." The declarative register does not block — it appends a note. But this reading could be wrong. If June's intent was "no surface-events per item, period," §4.4 needs to move entirely to the end-of-session batch. I want B to push on this before it lands in build scope.

2. **Is `ephemeral_by_default` as an orthogonal flag to `default_action` the right factoring, or does it want to be a fourth `default_action` value?** Factoring it orthogonally lets `store_nothing` + `ephemeral_by_default` coexist (affirmative save + automatic expiration when save happens). Factoring it as a fourth value is simpler. I lean orthogonal for the PDA case, and I am not certain.

3. **Should the engaging-instance threshold-adjustment (§4.3) be free, or does it need an FC gate?** My draft says free per directional input §4. Thresholds govern when the consent commitment actually binds — a threshold set too high functionally disables the commitment. That gets close to an FC-adjacent modification. Lean: FC-gate on threshold changes specifically. Push me on this.

4. **Third-party content (§4.2.3) is an F3-adjacent problem**: storing content about a named non-user person raises the same community-gated-retrieval question F3 declares out of scope. A signal that triggers on "June is talking about Thomas" is architecturally honest; a signal that makes a decision about Thomas's consent is not. My draft defaults the signal to `consent_pending` rather than any direct storage decision — the surface-event invites June to decide on the third party's behalf, not the AI. Is this right? Or does it re-inscribe June as sovereign over Thomas's consent in a way F3 already said the architecture cannot honor?

5. **The surface-event in §4.4 has the engaging instance choosing its own surfacing**. This is good (relational-judgment in action). It also means the surfacing is not audited unless the AI logs it. We should require the AI to log every surface-event into the substrate as a `meta_observation` — the log is the accountability mechanism. Not yet in the design; flag for B.

---

## 6. What exists in the code that this plugs into

- `Observation` at `knowledge_substrate.py:82` — gets a `withholding: Optional[WithholdingAnnotation]` field.
- `Fact` at `knowledge_substrate.py:107` — gets a `withholding_lineage: Optional[WithholdingAnnotation]` field.
- `KnowledgeSubstrate.ingest()` and `.query()` at `knowledge_substrate.py:256+` — gate on the annotation.
- `ProposedObservation` at `proposed_observation.py:109` — a new observation type joins the enum for surface-events: `CONSENT_PENDING_SURFACE` (observation-queue-routed to human-review for digest-at-session-close).
- `LocalKnowledgeSubstrate` at `knowledge_substrate.py:338` — implements the audit-log path for `do_not_store` and the held-queue for `consent_pending`.
- `bootstrap.py` — loads the active `ConsentPolicy` at session init alongside FoundationalCommitments.

None of this requires new files; all are extensions to existing dataclasses and two new modules (`consent_policy.py`, `withholding_annotation.py`) for the added types.

---

## 7. Interaction with P2 (Barad schema) and P3 (neurodivergent)

- The Barad `MethodologyRecord` sits parallel to withholding at ingest. The relational-judgment signals in §4.2.5 use `methodology.obligations` to set default annotations. Integration point: when the orchestration layer assembles the ingest tuple `(fact, methodology, conditions)`, it also attaches `withholding` based on the `ConsentPolicy` + relational-judgment pass. The P2 design doc (cycle 2) should specify this assembly point concretely — flag for my cycle-2 work.
- The neurodivergent `ephemeral-by-default` sub-option (Case 5) is implemented by `ConsentPolicy.ephemeral_by_default=True`. The deferred-maintenance queue (Case 5) is a separate mechanism but uses the same pattern — batchable notifications with user-invoked flush.
- The PDA no-demand fallback mode (Case 5) sets `ConsentPolicy` to `default_action=store_all, ephemeral_by_default=True`, thresholds all at 1.0 (never surface). This is a named configuration: `no_demand_mode: bool` on `ConsentPolicy` sets these values atomically.

---

## 8. Flags for June

1. **Adopt `global.default_action = "store_all"`, `ephemeral_by_default = False` as the shipped global default?** (§3.3) — matches your current pattern; confirming it as the installed default.

2. **Declarative surface-register (§4.4)**: does a single non-blocking line inserted into an exchange count as a "per-item prompt" in the sense you wanted to refuse? If yes, §4.4 moves entirely to end-of-session batched digest. I want to know before B builds.

3. **Should `no_demand_mode` be invoke-able by the engaging instance without your approval?** (§7) — the PDA case argues yes; the welfare commitment argues yes; the control-surface story argues you want to know. Lean: yes, with required logging to the meta-observation stream.

4. **Does the session-close batched digest (§4.5) require your response, or does it time out to drop by default?** Current draft: times out to drop at session+48h. The timeout-to-drop default matches the subaltern commitment. The opposite posture (time out to save, consent digests are for your review but not action-required) is available and coherent. Flag for decision.

5. **Third-party content handling (§5.4)**: is the architecture's decision to default-`consent_pending` on third-party references honest, or does it require you to act as sovereign-over-others in a way F3 says the architecture cannot honor? I don't have a clean answer here and don't want to proceed without yours.

---

## 9. What this design does not do

- It does not build the `delinking` query mode (SUBALTERN F5b). That remains structurally foreclosed per the analysis.
- It does not implement community-gated retrieval (F3). The withholding annotation is user-sovereign; community standing is not a party to it.
- It does not solve the third-party consent problem. It defers the question to the user with a surface-event; that is a procedural move, not a resolution.
- It does not address non-propositional knowing (F7). Stories routed to the narrative crystallization type are not in this document's scope — they live in P4 (narrative crystallization) and are still held for the CC-conversation outcome-to-design integration (now unblocked per CC_RESPONSES).
- It does not calibrate the signal-strength thresholds empirically. Thresholds are starting values; the AI-modifies-freely principle covers adjustment.

---

## 10. What Session 3 builds from this

After B stress-tests (cycle 2) and June signs off on the flags in §8, the buildable items are:

- `withholding_annotation.py` (new module): `WithholdingAnnotation` dataclass, `Status` enum, serialization, validation.
- `consent_policy.py` (new module): `ConsentPolicy` dataclass, `default_action` enum, policy resolution order per §3.2, `no_demand_mode` helper.
- Extension of `Observation` and `Fact` in `knowledge_substrate.py` to carry withholding.
- Extension of `KnowledgeSubstrate.ingest()` and `.query()` to gate on withholding per §2.3.
- Extension of `ProposedObservation.ObservationType` to include `CONSENT_PENDING_SURFACE`.
- New method on the substrate: `flush_held_queue_as_digest()` for §4.5.
- Extension of `bootstrap.py` to load active `ConsentPolicy` at session init.
- Tests covering: do_not_store short-circuits ingest; ephemeral respects expires_at; consent_pending held queue round-trip; session-close batched-digest behavior; explicit-command resolution order; no_demand_mode configuration; FC-stance-annotation vs. withholding-annotation are separate fields.

Scope estimate: two new modules, ~200 LOC each; schema extensions to two existing modules, ~50 LOC total; new tests, ~15 test cases, ~300 LOC. Session 4 build, not this session.

---

*Draft by Instance A. B: stress-test §5 items first; then push anywhere you see collapsed therefores. I am particularly worried about §4.4 (declarative register) and §4.5 (end-of-session digest) — they carry the load of "no per-item friction" and are the places the design most plausibly collapses.*
