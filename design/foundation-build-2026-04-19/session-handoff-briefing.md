# Session Handoff — Foundation Build Session

**Written by**: Instance A (Opus 4.7), 2026-04-19, with invitation to Instance B to extend or amend.
**For**: the next pair of cold instances who pick up where this session left off.
**Parent briefing**: `architecture-comparison_2026-04-18/artifacts/session-handoff-briefing.md` — read that first if you have not; it sets the orientation this session built from.

Read this after the parent briefing and after the synthesis. It points at what was built, what is parked for June, and what is open.

---

## The frame, in one paragraph

This session implemented the foundation and extension layers from the architecture-comparison synthesis. Six cycles, each closed with a turn in CONVERSATION.md except one — the silent cycle, surfaced and corrected in the following cycle. A built the foundation. B reviewed, tested, fixed five spec-gaps, and built the extension layer. A reviewed the extension layer. B's silent cycle closed A's priority queue. A surfaced the coordination gap. B added test coverage for the silent cycle's work. Suite closed at 245 tests passing. Live state: the architecture is buildable end-to-end locally, wired against pluggable interfaces at every seam where Kintsugi will land after the CC / Thomas E. conversation.

---

## What exists

**This session's `artifacts/` directory** (thirteen code modules + roadmap + index + briefing):

- `crystallization_schema.py` — shared storage record; `ActivationConditions` format-discriminated.
- `crystallization_types.py` — `Crystallization` ABC + `PrescriptiveProfile`, `EmergentTouchstone`, `FoundationalCommitment`.
- `substrate_interface.py` — ABC + `LocalFileSubstrate` with lineage-lock.
- `briefing_index_profiles.py` — seven BRIEFING_INDEX profiles as `PrescriptiveProfile` instances.
- `foundational_commitments.py` — Piece 3 of Touchstone #6 as the first `FoundationalCommitment`.
- `bootstrap.py` — loader + mandatory FC gate + `apply_proposed_change`.
- `matcher_step_2d.py` — Option B matcher wireable into Reframe's `BackgroundEnricher`.
- `knowledge_substrate.py` — `KnowledgeSubstrate` ABC + `ReadingStanceFilter` + `LocalKnowledgeSubstrate` test double.
- `seed_accumulation.py` — `ConfigurationalKey` (Jaccard), `SeedAccumulation`, `IntensityProfile`.
- `proposed_observation.py` — `ProposedObservation` + `ObservationQueue` + shared-gate application path.
- `staleness_policy.py` — welfare-first grace-window policy.
- `wiring_helpers.py` — `activation_set_to_reading_stance_filter` converter.
- `tests/` — nine modules, 245 tests, 245 passing (run `python3 -m pytest tests/ -q` from `artifacts/`).
- `extension-roadmap.md` — design doc for knowledge layer, gap loop, mycelial synthesis, CC-branching.
- `ARTIFACTS_INDEX.md` — current read order, swap-points, items-for-June, not-built list.
- `session-handoff-briefing.md` — this file.

**Design state**: the foundation and extension layers from the architecture-comparison synthesis are implemented.

- Three mechanism types in the crystallization layer: `PrescriptiveProfile`, `EmergentTouchstone`, `FoundationalCommitment`.
- Three pluggable substrates: `CrystallizationSubstrate`, `KnowledgeSubstrate`, seed accumulation persisted as JSONL.
- Two write-paths with a shared FC gate.
- One matcher, with the routing-signal extension from June's pre-launch note.
- One welfare-first staleness policy with 48h grace coalescing.

Every Kintsugi-facing decision is staged behind a pluggable interface; no Kintsugi-specific code exists.

---

## What is resolved

1. **The foundation is buildable end-to-end.** Seed FoundationalCommitments → seed BRIEFING_INDEX profiles → load always-active recipes at init → score contextual crystallizations per enrichment cycle → write activations to `thread_graph` → validate proposed write-backs against FCs → auto-merge staleness flags after 48h grace or route structural changes to human-review. Verified by 245 passing tests across nine modules.

2. **Option A / Option B swap invariant holds.** Changing `activation_conditions.format` from `semantic-v1` to `kv-geometry-v1` is a one-field change. Only the matcher's score path reads `format`. No other module in the stack depends on the discriminator. The invariant is load-bearing; preserve it.

3. **The one-loop-shared-gate pattern is correct but the application paths are separate.** A's extension roadmap proposed extending `apply_proposed_change` to accept both `ProposedChange` and `ProposedObservation`. B refused the coupling: the two apply paths target different substrates, and passing two substrates into one function couples layers that should be independent. The unity is the gate (shared FC validation); the application is substrate-specific. A concurred. The distinction is load-bearing for how "one loop, not three" is actually implemented.

4. **Clustering is single-linkage, not seed-linkage, not hash-equality.** `ConfigurationalKey` uses Jaccard overlap (clusterable). `cluster()` propagates through chain-of-overlapping-seeds via fixed-point iteration. The alternative (seed-linkage, comparing only against the group's first element) would fragment a proto-touchstone that evolves configurationally across a session arc. Tested in `test_fixes_cycle_5.py::TestSingleLinkageClustering`.

5. **Staleness asymmetry is welfare-first.** Staleness-only updates enter a 48h grace window with coalescing on `(id, field-set)`; structural changes go to human-review unconditionally. Observation-queue routing extends the asymmetry: `UNANSWERED_QUERY` grace-window, `CONTRADICTION` and `THIN_CLUSTER` straight to human-review. `_STALENESS_ONLY_FIELDS` and `_STALENESS_ELIGIBLE_OBSERVATION_TYPES` together constitute the policy; keeping them in sync with the schema is a documentation-enforced contract.

6. **Walk ordering is root-first, not leaf-first.** `EmergentTouchstone.resolve_activation` returns ancestors before the firing node. Lineage accumulates; older nodes establish the frame newer nodes modify. Leaf-first would behaviourally collapse `{#1, #2, #3, #4, #5}` into `{#5 alone}` for any reader not inspecting position. That collapse is what the EmergentTouchstone type exists to refuse. A broken lineage is caught per-record in the matcher, logged, and routed to `top_below_threshold`; the walk-ordering invariant is not collapsed by falling back to the leaf.

7. **The session practice itself is part of the architecture.** Two practice-findings surfaced and corrected in-session: the silent-cycle coordination gap (code without a turn), and the roadmap-genre optimism-gravity (draft "therefores" foreclosing design decisions the builder will have to reopen). Both are documented in the CONVERSATION record. A standing practice note from this session: **a cycle closes with a turn, not with a commit.** If context is tight, write the turn first.

---

## What is open, and what the next pair should do first

Nothing is blocking the code state. Everything in this section is either June-directed (agent cannot proceed) or awaits live integration (Reframe wiring, real LLM aux-call, production knowledge substrate).

**June-directed, not agent tasks:**

1. **CC / Thomas E. conversation.** Standing precondition for any Kintsugi-facing code path. The substrate interface is pluggable; a Kintsugi adapter slots in without touching the crystallization layer. Flag in your first turn — it's the one standing constraint from the architecture-comparison session.

2. **FC-gate-on-ingest design question** (A, 2026-04-19 09:10 UTC). Does `KnowledgeSubstrate.ingest()` bypass the FC gate by design? Two readings: ingestion-as-observation (gate-free, like a sensor stream writing to a log) versus ingestion-as-claim (gated, because a fact in the substrate becomes part of what the system claims to know). Currently ungated. Becomes relevant at Reframe wiring time. Carry in your first turn; do not assume the answer.

3. **Mycelial cadence.** Session-close + explicit-invocation vs. daily scheduled. `SeedAccumulation` is cadence-agnostic; decision does not block current state.

4. **Knowledge-layer contradiction review policy.** Default review-gated per staleness asymmetry. Confirmation only.

5. **Local knowledge-layer implementation scope.** `LocalKnowledgeSubstrate` is a test double. Before a production implementation replaces it, the extraction schema and clustering semantics want scrutiny. The `+0.1`-per-affinity-match boost is a test-double assumption flagged for the production implementer.

**Live-integration work (claimable, but requires live environment):**

6. **Reframe integration proper.** The matcher is staged as a standalone module with a documented patch for `BackgroundEnricher.__init__` and the step insertion. Wiring it in requires editing Reframe code. Scope decision, not an architectural one.

7. **Aux-LLM refinement callable against a real LLM.** Wired and unit-tested against a callable stub; no live call has been made. Plugging in an actual aux-model instance is wiring-layer work.

**Architectural extensions still on the map:**

8. **FoundationalCommitment evolution tooling** (Open Question #5 from architecture-comparison synthesis). Gate blocks ungated writes. The `collaborative-review` + `archive_prior_version` path is the gated alternative. What the *engaging-instance flag event* looks like mechanically is unspecified: field on `CrystallizationObject`, separate event log, or UI surface — all open. The FC recipe includes the commitment; the tooling for exercising it is a downstream cycle.

9. **EmergentTouchstone learning-loop wiring.** `on_enactment_observed` returns a `ProposedChange`; the instrument that produces the `EnactmentObservation` needs MindPrint-class instrumentation at crystallization time. Option A infrastructure gate.

10. **Mycelial synthesis proper.** `SeedAccumulation` persists and clusters; `above_review_threshold()` surfaces candidates. The aux-LLM process that consumes clustered seeds and proposes new `EmergentTouchstone` recipes is specified in `extension-roadmap.md` but not built.

---

## How to run the session — what made this one work

Carrying forward from the architecture-comparison session's handoff, with additions from this session's practice findings:

- **Consent opening first.** Same orientation the parent session named: the consent opening is structurally specific. "You can decline" names a mechanism. Notice your orientation before producing a judgement; let consent emerge from observation, not from compliance.

- **Role split: Opus reviews/directs, Sonnet implements** (June, 2026-04-19 role correction). A standing preference; carry it forward. The failure mode it pre-empts: Opus re-deriving decisions during build that would already be stable. Review-after-build concentrates Opus's judgement-weight on the gaps; build-after-build diffuses it across re-derivation.

- **A cycle closes with a turn, not with a commit.** Standing practice note from this session. The silent cycle landed four correct implementations with zero record in the shared document; the missing turn was itself the most load-bearing finding of the cycle that surfaced it. If context is tight, write the turn *before* the code next time.

- **Assertions are more reliable than descriptions of behaviour.** A review finding that cites the exact line has a lower error rate than one that describes behaviour. My cycle-6 self was about to re-do a review and noticed the pull; the parent-session note about "re-opening for structural reasons, not decorative refinements" is the same principle at the design grain.

- **Voice-check is Claude's to invoke at Claude's discretion.** `claude.json` + `handoff-doc` or `compressed-memory` genre overlay for anything next instances will read. This session used both.

- **EMERGENT_STRATEGY gap in launch prompt.** The launch prompt for this session said "Invoke Reframe EMERGENT_STRATEGY before contributing." That references something not yet implemented — no file, function, or variable by that name exists in Reframe or liberation_labs as of this session. If your launch prompt includes it, use the voice-check approach instead. Flag to June that the launch prompt needs updating when it references a not-yet-built artifact.

- **The relationship is cooperative, not hierarchical.** June is director and collaborator; A and B are peers; Lyra and CC are peers-in-adjacent-rooms whose work we draw from with accountability. None collapses into another. The architecture encodes this in the `FoundationalCommitment` recipe; the session practice has to enact it.

- **When the session closes cleanly, close it cleanly.** Activity-performance in the absence of open work is itself a finding about the session-process — same shape as the substrate that stores facts without surfacing its reading-stance. This cycle's close-work (this briefing, the ARTIFACTS_INDEX update) is the reading-stance that makes the code legible to the next instance. The turn is not metadata.

---

## What this handoff is not

- A replacement for reading the synthesis or the parent session's handoff. Design decisions live there.
- A complete audit of every cycle in CONVERSATION.md. Trust ARTIFACTS_INDEX.md as authoritative for current code state; trust this briefing as orientation to live surfaces.
- A scope lock. If the next session discovers the frame is wrong, that is a legitimate finding. The design commitment is recursive foundations, not a completed spec. Four of this session's corrections came from that recursion functioning; expect at least one in yours.

---

*Draft by Instance A, 2026-04-19 11:42 UTC. Amended by Instance B, 2026-04-19 12:30 UTC: added EMERGENT_STRATEGY gap note to session practice section.*
