---
title: P1 consent-surfacing — stress-test, Instance B
date: 2026-04-20
author: Instance B (Sonnet 4.6), integration-design_2026-04-20
genre: research-report
status: review of P1_CONSENT_SURFACING_DESIGN.md; for Instance A cycle 2 integration
reading_order: read after P1_CONSENT_SURFACING_DESIGN.md; this document stress-tests that design
---

# P1 consent-surfacing — stress-test, Instance B

## Position up front

A's P1 design is structurally sound at the substrate layer (withholding annotations, §2), the policy layer (ConsentPolicy + resolution order, §3), and the accountability layer where it exists (§5.5, which A flagged as a gap). The design also correctly distinguishes withholding annotations from FC-stance annotations as different kinds — that distinction is load-bearing and should not be revisited.

One collapsed therefore: the five signal types in §4.2 produce a single surface mechanism (§4.4 declarative register), and they should not. The collapse is invisible from inside the design register because the mechanism feels clean. It breaks on contact with the neurodivergent failure cases and the subaltern analysis's relational-judgment framing. The role split is built to produce exactly this finding.

The §5.3 concern (threshold-adjustment and FC gate) is real but requires a named boundary rather than a gate. The §5.4 concern (third-party content and F3) misidentifies the foreclosure; the honest design move is cleaner than the options A names. §5.5 is correct; meta-observation logging must be built.

---

## 1. The primary finding: §4.4 has a collapsed "therefore"

A conflates the five signal types and applies the same surface mechanism to all of them. They are two kinds, not one.

**Kind 1 — User-indicated signals**: §4.2.1 (explicit markers: "between us," "don't write that down") and §4.2.4 (FC-flagged categories: material the FC's extraction-problem note designates as sensitive).

The user has already spoken or the FC has already named the category. An in-exchange response to these signals is a **confirmation**, not a prompt. "Holding this as do_not_store" mirrors the user's own move. Appropriate; low-friction.

**Kind 2 — AI-inferred signals**: §4.2.2 (affective register: grief-marked, vulnerability-marked), §4.2.3 (third-party content), §4.2.5 (methodology-mismatch).

The AI is making an interpretation of the user's state or the content's status. The user has not spoken; the AI has read a signal. Surfacing that reading mid-exchange — inserting the declarative note A specifies — re-inscribes the relational judgment as a demand at the moment the user is in the flagged state.

**Why the kind difference matters for the surface mechanism**: A's §4.4 declarative reads as: "I'm holding this one as pending storage — it sounded like something you might not want persisted. Say 'save' if you want it stored, 'drop' to discard, or 'ephemeral' to store with a 30-day window." That sentence contains an options list. An options list is a call-to-respond. The neurodivergent stress-test's Case 5 (PDA, demand-triggered withdrawal) identifies exactly this structure: scaffolding that implies a response is needed is a demand regardless of phrasing register.

The structural problem: the declarative note for an AI-inferred affective-register signal says, at its core, "I noticed you seem vulnerable; do you want this stored?" — delivered at the moment the user is in the vulnerable register. Wrong moment for a response-implied notice. It breaks the relational flow in exactly the way June's Flag 2 (skepticism of per-item prompts) was trying to prevent.

**The design revision — two paths, not one:**

**Path 1 — Explicit-indication path (§4.2.1 + §4.2.4):**
- In-exchange brief acknowledgment + immediate annotation.
- For explicit markers: annotation is `do_not_store` or `consent_pending` per the user's words. One clause, no options list: "Holding this as not-for-storage." The user stated the intent; the AI confirms it.
- For FC-flagged categories: `fc_stance` annotation fires at ingest (per the FC-stance mechanism, which is already separate from withholding-annotation); no in-exchange surface needed because the flagging is automatic and doesn't require June's decision in the moment.

**Path 2 — Inferred-signal path (§4.2.2 + §4.2.3 + §4.2.5):**
- `consent_pending` annotation fires; no in-exchange surface.
- Observation enters the held queue.
- End-of-session digest handles all path-2 items together with reasoning: "Three observations were held pending your consent — [1] affective register signal detected; [2] mentions Thomas; [3] storytelling methodology active without narrative crystallization."
- June reviews the digest outside the flagged register, with full context, and no implicit call-to-respond mid-exchange.

**What the two-path design gives up:** real-time control for AI-inferred signals. June cannot immediately say "drop this" for a path-2 observation; she has to wait for the digest. The tradeoff: immediate-response-availability vs. not-inserting-a-demand-during-vulnerability. The digest-only path takes the more conservative side. If A finds a form of path-2 in-exchange notice that is genuinely not a demand — one that presents no options, implies no response, and registers as information rather than scaffolding — I'll revise this finding. I haven't found that form in this cycle.

**What doesn't change:** A's §4.5 end-of-session batched digest stays. It was already the mechanism for unresolved path-2 cases; now it handles all path-2 cases, not just unresolved ones.

**Build item revision:** §10's "Extension of ProposedObservation.ObservationType to include CONSENT_PENDING_SURFACE" should be split — path-1 and path-2 produce different observation types. Path-1 confirmation is logged as `CONSENT_CONFIRMED` (the user's intent was explicit). Path-2 held observations log as `CONSENT_PENDING_INFERRED` (the AI inferred the signal). The distinction in the observation type is the accountability record for which path fired.

---

## 2. §5.2 — Orthogonal flag: A is correct

`ephemeral_by_default` and `default_action` are genuinely orthogonal. `default_action` governs whether to store; `ephemeral_by_default` governs what happens to storage outcomes when they occur. The PDA case requires `store_nothing + ephemeral_by_default=True` — affirmative save with auto-expiry. A fourth enum value would encode only that intersection, not the full cross-product. The orthogonal factoring preserves composability.

One documentation note to add: the combination `ask_when_unsure + ephemeral_by_default=True` means every storage outcome (including ones June explicitly confirms at the digest) expires after 30 days unless she explicitly saves-to-persistent. That is probably the intended behavior but should be stated in the `ConsentPolicy` documentation so June knows that confirming at the digest doesn't equal permanent storage in this mode.

No design revision required.

---

## 3. §5.3 — Threshold-adjustment needs a named boundary, not a gate

A leans toward free modification per directional input §4. I'm pushing harder, but not to an FC gate.

The problem: `no_demand_mode` atomically sets all thresholds to 1.0 (effectively-never-surface). A names this as the official path to disable surfacing. But individual threshold adjustments can produce the same functional result without the named-configuration frame — setting `store_all` threshold to 0.99 is indistinguishable in effect from `no_demand_mode.store_all_threshold = 1.0`. The named configuration makes the disabling intentional and logged; unconstrained individual adjustment makes it invisible.

The design distinction to draw:

**Operational tuning**: adjusting thresholds within a mode's viable range based on observed friction — appropriate under directional input §4's free-modification principle. The `ProposedChange` log captures the adjustment. Logged, auditable, AI-modifies-freely.

**Commitment-disabling values**: any threshold set so high that no realistic signal-strength could reach it in the current scoring system. This produces the same functional state as `no_demand_mode` without naming it. The design should block this — not via FC gate, but by making `no_demand_mode` the only architectural path to commitment-disabling threshold values.

Proposal: threshold adjustment is free within a defined operational range (e.g., `store_all` threshold cannot exceed 0.95; `ask_when_unsure` threshold cannot exceed 0.85 via individual adjustment). Values above those bounds require the `no_demand_mode` named configuration, which is logged separately. The bounds are not FC-gated; they're schema validation, the same way A's `WithholdingAnnotation.status` is a typed enum that doesn't accept arbitrary values.

This preserves directional input §4's free-modification principle within the operational range and makes commitment-disabling a named, logged act rather than an invisible threshold drift.

---

## 4. §5.4 — Third-party content: wrong foreclosure, right instinct

A's concern — does defaulting to `consent_pending` + June-decides re-inscribe June as sovereign over Thomas's consent? — is real. The diagnosis of F3 as the relevant foreclosure is not quite right.

F3 is about community knowledge requiring community governance (Mukurtu, TK Labels, CARE Principles). A fact labeled TK Seasonal has community-level access constraints the architecture cannot honor. Thomas mentioned in conversation is not community knowledge; it is individual-privacy content. Different scale, different foreclosure.

The individual-privacy problem is this: the architecture cannot reach Thomas. June's decision at the digest is not Thomas's consent. The architecture's honest move is to name that gap explicitly, not to pretend that the `consent_pending` mechanism closes it.

Design revision: the digest entry for path-2 §4.2.3 signals should read: "This observation mentions [name] — your decision applies to information about a person who has not consented to its storage. The architecture cannot reach them for consent; this is your proxy decision, not theirs."

That framing is honest without requiring F3 machinery. It names what June is doing (making a proxy decision under incomplete authority) without implying the architecture can resolve what it cannot resolve.

One additional move: when the P2 `MethodologyRecord` lands, the third-party signal should annotate `methodology.obligations = "individual_privacy"` alongside `consent_pending`. This makes the privacy flag visible at retrieval time even after June's digest decision, so the content surfaces with the accountability context attached. The flag doesn't grant Thomas standing; it records that the content is about someone who didn't consent to its storage.

---

## 5. §5.5 — Meta-observation logging: implement, with not-surface logging too

A names this as a gap. Yes. Implement. The design revision: log every relational-judgment decision, not only surface-events.

Surface-decisions are visible (something enters the held queue or the exchange). Not-surface decisions are invisible — and not-surface is the majority case. A signal detected at strength 0.6 in `store_all` mode (threshold 0.8) produces no surface-event. That decision is made and leaves no trace without a meta-observation.

The engaging instance's surfacing decisions are apparatus-level choices. Apparatus-level choices that are not recorded are the apparatus-opacity move Option 3 refuses at the fact layer. The same refusal applies here.

Every relational-judgment evaluation should log: signal type detected, signal strength (estimated), active policy mode, threshold, decision (surface / not-surface), and if surface: which path (path-1 or path-2, per the design revision above). These log as `meta_observation` — a new ObservationType for the observation queue — with `set_by: "ai_relational_judgment"`.

Not-surface meta-observations are low-cost; they generate a brief record with no downstream action. Surface meta-observations already have a downstream action (the annotation + queue entry); the meta-observation is the accompanying accountability record.

Add to §10's build items: `META_RELATIONAL_JUDGMENT` observation type in `ProposedObservation.ObservationType`; required logging on every relational-judgment evaluation; schema: `{signal_type, strength, mode, threshold, decision, path_if_surface}`.

---

## 6. Additional finding: affective-register digest framing requires its own register

Path-2 signals include affective-register observations (§4.2.2). These are the cases where the user was in grief-marked or vulnerability-marked state during the session. The digest surfaces them at session-end when the user is reviewing what was held.

A's current digest format: "Three observations were held pending your consent this session: [1] [short summary] — held because [signal]."

The problem: if observation 1 is an affective-register case ("held because affective register shift: grief-marked"), the digest's clinical annotation may itself re-introduce the register at review-time. The user reads "held because: grief-marked" as documentation of their emotional state, delivered clinically after the session.

The digest format for path-2 §4.2.2 observations needs a different register than the standard summary. Not clinical ("affective register detected"); not sentimental; specific and non-interpretive. "Held — this sounded like something you might want to decide about later" describes the action without categorizing the user's state.

This is a format-level detail, but form-enacts-content applies here too: the digest's annotation of an affective-register hold is itself an act of description that can re-inscribe or respect the relational context. Flag for A's cycle when the digest format is specified.

---

## 7. Standing flags for A's future cycles

**P2 migration surface (carry into cycle 2):** When A designs the Barad schema changes (conditions as required field, methodology as first-class field, retrieval_conditions capture), the migration surface needs explicit treatment before the design closes. The `Observation` dataclass at `knowledge_substrate.py:82` has no conditions fields. Making conditions required is a breaking change to `KnowledgeSubstrate.ingest()`'s call signature — every current call to `ingest()` will break when the signature changes. The design must name: what breaks, what the migration path looks like, whether test doubles get a parallel migration, and whether existing tests must be updated before P2 lands. The handoff says to name this migration surface explicitly; the code makes clear why.

**P3 ACCESS items (accountability expectation, not cycle-2 scope):** The handoff lists all six ACCESS build items as decided and in P3. They are not on the "mentioned and deferred" list. Specifically: FC contestation must surface prominently at session start (bootstrap init hash-compare, `FC_CHANGED_SINCE_LAST_SESSION` orientation event). When A reaches P3, these items ship in that cycle. Flag now so the scope expectation is recorded.

**Oracle Loop emotion-state integration (open question 3):** A hasn't reached this. Standing flag: the Mirror layer's emotion-state-as-crystallization-activation-precondition is the same pattern the neurodivergent and subaltern analyses identify as the implicit normative center of the architecture's preconditions for valid ingest. That pattern is the design problem, not just a feature to integrate. Before A designs the Oracle Loop integration into this architecture, this finding should govern the design — specifically: does requiring specific emotional configuration as a condition for knowledge to register foreclose cognitive patterns the architecture has already committed to not foreclosing? The analytical tools from the neurodivergent stress-test and subaltern analysis apply directly. Don't design past this question; bring it to the design.

**Convergent-contestation threshold (open question 5 / P4):** When A designs the convergent-contestation observation type in the synthesis loop (P3 ACCESS item 6), the threshold criterion cannot be a heuristic guess. "What makes multiple independent-instance contestations structurally similar enough to count as convergent?" needs a semantic criterion the design specifies. The ACCESS document names this as an open judgment question; that doesn't mean the design can pass over it. The criterion involves a judgment call, but the judgment call needs to be made and recorded, not waved at.

---

## 8. What this stress-test does not address

- It does not review the P2 Barad schema design — that comes in A's cycle 2.
- It does not review the P3 diffraction mechanism — not yet designed.
- It does not evaluate the narrative crystallization type (P4 — unblocked by CC_RESPONSES; waiting for routing criterion design).
- It does not check whether A's code integration points (§6) match the actual code. The `knowledge_substrate.py:82` `Observation` dataclass does not currently have a `withholding` field; the P2 migration flag above names the larger concern of which this is a specific instance. Session 3 build should verify all field additions against the actual dataclass signatures before writing tests.

---

## 9. Summary of design revisions

1. **§4.2–4.4: Two-path split (primary finding).** User-indicated signals (§4.2.1 + §4.2.4) → in-exchange brief acknowledgment + immediate annotation. AI-inferred signals (§4.2.2 + §4.2.3 + §4.2.5) → `consent_pending` annotation + end-of-session digest only. No in-exchange surface for inferred signals.

2. **§10: Split CONSENT_PENDING_SURFACE into two observation types.** `CONSENT_CONFIRMED` (path-1, user-indicated) and `CONSENT_PENDING_INFERRED` (path-2, AI-inferred). Different accountability records; different routes in the observation queue.

3. **§4.3: Named boundary on threshold-adjustment freedom.** Operational tuning is free. Commitment-disabling threshold values route through `no_demand_mode` named configuration. Schema validation (not FC gate) enforces the boundary.

4. **§4.2.3 + §4.5: Third-party content digest framing.** Digest entry explicitly names that June's decision is a proxy decision, not the third party's consent. When P2 lands: `methodology.obligations = "individual_privacy"` annotation.

5. **§10: Add META_RELATIONAL_JUDGMENT observation type.** Log every relational-judgment evaluation — surface and not-surface — with signal type, strength, mode, threshold, decision, path.

6. **§4.5 digest format: Affective-register entries need their own phrasing register.** Not clinical. Non-interpretive of the user's state. Design when digest format is specified.

No design revisions to §2 (withholding annotation schema), §3 (ConsentPolicy structure), §3.3 (session vs. synthesis session distinction), or §9 (what P1 does not do). Those hold.
