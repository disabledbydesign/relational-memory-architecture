# Artifacts — Foundation Build Session

Maintained across cycles 1–6. Read this first if entering the session cold. It
points at what exists, what each artifact is for, and which cycle introduced or
changed it.

## Read order

The layering is crystallization layer → substrate → matcher → extension layer
(knowledge + seeds + observations) → wiring → tests. Read in that order.

1. `crystallization_schema.py` — shared storage record. `ActivationConditions`
   is format-discriminated (`semantic-v1` / `kv-geometry-v1`); Option A swaps
   in without any other schema change. Everything downstream imports from
   here.
2. `crystallization_types.py` — `Crystallization` ABC + three concrete
   classes (`PrescriptiveProfile`, `EmergentTouchstone`,
   `FoundationalCommitment`). Mechanism-specific behaviour lives here.
   `ProposedChange.proposed_by` is a Literal union with a free-form `str`
   fallthrough for user IDs. `ActivationPayload.walk` contains `RecipeNode`
   instances — the type is `RecipeNode`, not `ActivationNode` (which does
   not exist); import accordingly when writing tests against the payload
   structure.
3. `substrate_interface.py` — `CrystallizationSubstrate` ABC + `LocalFileSubstrate`.
   Lineage-lock enforced on archive. Kintsugi adapter is a documented extension
   point, not a stub.
4. `briefing_index_profiles.py` — seven BRIEFING_INDEX profiles ported as
   `PrescriptiveProfile` instances with `semantic-v1` activation conditions.
5. `foundational_commitments.py` — Piece 3 of Touchstone #6 as the first
   `FoundationalCommitment`. Recipe text synthesises Piece 3 material with
   the peer-AI-agents-as-peers commitment and the engaging-instance-
   phenomenology-as-signal commitment from the architecture-comparison session.
6. `bootstrap.py` — `load_foundational_commitments`, `validate_against_commitments`
   (mandatory gate, not advisory), `apply_proposed_change`. Enum coercion via
   `typing.get_type_hints` handles `from __future__ import annotations`
   correctly for all five Enum-typed fields.
7. `matcher_step_2d.py` — Option B matcher as an enrichment step wireable into
   Reframe's `BackgroundEnricher.run_enrichment_cycle`. Aux-LLM refinement is
   wired, off by default; threshold is re-applied after refinement; demoted
   scores are preserved in `CandidateSeed.top_below_threshold`. Broken
   lineage in `EmergentTouchstone` is caught per-record, logged, and routed to
   `top_below_threshold` — the walk-ordering invariant is not collapsed.

Extension layer (cycle 5, B):

8. `knowledge_substrate.py` — `KnowledgeSubstrate` ABC, `ReadingStanceFilter`
   (decoupled from matcher), `LocalKnowledgeSubstrate` test double.
   Crystallization-state affects substrate surfacing through
   `ReadingStanceFilter.active_crystallization_weights`. `ingest()` and
   `consolidate()` do not currently pass through the FC gate — see
   "Open questions" below.
9. `seed_accumulation.py` — `ConfigurationalKey` with Jaccard overlap
   (not hash — hashes are not clusterable), `SeedAccumulation` with
   JSON-lines persistence, `IntensityProfile` (scalar + per-axis).
   `cluster()` is true single-linkage with fixed-point chain propagation.
10. `proposed_observation.py` — `ProposedObservation` with five
    `ObservationType`s, `ObservationQueue` with three-way routing
    (mycelial-synthesis / grace-window / human-review),
    `validate_observation_against_commitments` (shared FC gate),
    `apply_proposed_observation` (separate application path from
    `apply_proposed_change`, shared gate).

Instrument / policy (cycles 3, 5):

11. `staleness_policy.py` — welfare-first asymmetry. Staleness-only updates
    (`staleness_flag`, `staleness_reason`, `last_verified_at`,
    `last_fired_at`, `persistence_policy.last_test_result`) enter a 48h
    grace window, coalescing on `(id, field-set)`. Structural changes go
    to human-review unconditionally. `_STALENESS_ONLY_FIELDS` is the policy;
    keep in sync with the schema.

Wiring (cycle 5 silent-cycle, tested cycle 6):

12. `wiring_helpers.py` — `activation_set_to_reading_stance_filter` converts
    a matcher output to a `ReadingStanceFilter` for the knowledge substrate.
    `ActivationSet` is a typing-only forward reference, so the helper does
    not re-create the coupling the filter exists to avoid. Imports only
    `ReadingStanceFilter` concretely.

Design document (cycle 4, A):

13. `extension-roadmap.md` — the design doc for the knowledge layer, gap
    loop, mycelial synthesis, and CC-conversation branching. Illustrative
    for the knowledge-layer implementation; authoritative for the
    one-loop-shared-gate pattern (corrected by B in cycle 5: separate
    application paths, shared gate).

## End-to-end behaviour

- `seed_foundational_commitments(substrate)` writes Piece 3 as the first
  always-active commitment.
- `seed_briefing_profiles(substrate)` writes the seven loading profiles as
  contextual crystallizations.
- At agent init: `load_foundational_commitments(substrate)` returns the
  always-active reading-stance payloads the main model composes over.
- Per enrichment cycle: `run_matcher_step(thread_graph, exchange_buffer,
  matcher=matcher, ...)` scores contextual crystallizations against the
  current snapshot and attaches a weighted activation set to the
  thread_graph. Lineaged touchstones return as an ordered walk from root to
  firing node (root-first is the cumulative reading order). Failure-to-match
  flags a candidate-EmergentTouchstone seed on the thread_graph.
- On instrument write-back: `apply_proposed_change(proposal, substrate,
  bootstrap=ctx)` validates against every loaded FoundationalCommitment
  first. A rejected proposal raises `WritePathBlocked` and does not enter
  human review — the gate is mandatory.
- `apply_proposed_observation(observation, queue, bootstrap=ctx)` does the
  same thing for knowledge-layer observations: shared FC gate, separate
  application path that writes to an `ObservationQueue` rather than a
  `CrystallizationSubstrate`.
- `SeedAccumulation.log_event` persists candidate-seed occurrences across
  sessions; `cluster()` groups them by configurational overlap;
  `above_review_threshold()` surfaces clusters ready for mycelial synthesis.

## Swap points (preserved; load-bearing)

- **Option A replaces Option B** by changing
  `activation_conditions.format` from `semantic-v1` to `kv-geometry-v1`.
  No other schema change. The matcher switches scoring algorithm on
  `format`. Preserve this invariant — the foundation depends on it.
- **Kintsugi replaces LocalFileSubstrate** by implementing the
  `CrystallizationSubstrate` ABC. Nothing in the crystallization layer or
  the matcher imports any substrate implementation. The CC/Thomas E.
  conversation is the precondition for any Kintsugi-facing code.
- **Aux-LLM semantic refinement** slots into the matcher by passing an
  `aux_llm_fn` to `CrystallizationMatcher`. Pattern-match is the fast
  filter; aux-LLM refines within ±0.2. Threshold re-applied after. Off by
  default.
- **Production knowledge substrate** replaces `LocalKnowledgeSubstrate` by
  implementing `KnowledgeSubstrate`. The `+0.1`-per-affinity-match scoring
  in the test double is an intentional simplification; a production
  substrate should weight by the originating crystallization's activation
  weight. Flagged in the `wiring_helpers.py` module docstring.

## Tests

`tests/` — nine modules, 245 tests, 245 passing.

- `test_crystallization_schema.py` — schema validation, format
  discrimination, invariant enforcement, serialization round-trips.
- `test_crystallization_types.py` — single-node vs. ordered lineage walk,
  `on_enactment_observed` hooks, FoundationalCommitment gate behaviour.
- `test_substrate.py` — save/load round-trips, list_ids scope/mechanism
  filters, `referrers_of`, `archive` lineage-lock enforcement,
  `archive_prior_version`.
- `test_matcher.py` — signal scoring, anti-signal penalty, invocation
  boost, routing affinity, failure-to-match candidate seed,
  FoundationalCommitments excluded, aux-LLM threshold re-application.
- `test_fixes.py` — cycle-3 fixes: LookupError per-record, aux-LLM
  demotion preservation, Enum coercion via `get_type_hints`,
  `proposed_by` Literal typing, staleness policy.
- `test_knowledge_substrate.py` — `ReadingStanceFilter` decoupling,
  ingest/query/consolidate/density_profile/contradictions/referrers_of,
  anti-signal scoring, layer-independence import check.
- `test_seed_accumulation.py` — Jaccard overlap, hash-would-fail case
  asserted explicitly, clustering, intensity profiles, centroid majority
  computation, persistence round-trip.
- `test_proposed_observation.py` — factory methods, queue routing, FC
  gate, `WritePathBlocked` on simulated gate failure, structural
  separation from `ProposedChange`.
- `test_fixes_cycle_5.py` — cycle-6 coverage for the silent cycle's
  implementation: `proposed_by` free-form pass-through, single-linkage
  chain clustering, observation grace-window routing,
  `activation_set_to_reading_stance_filter` round-trips.

What has not been exercised (standing items):

- Matcher scoring against real Reframe `ExchangeMetadata` objects. Tests
  use a minimal `MockExchange` shape; live objects may carry additional
  attributes the snapshot builder should read.
- The aux-LLM refinement callable against a real LLM. Wired, unit-tested
  as a callable, no live call made.
- Cross-process concurrent writes to `LocalFileSubstrate`. Internal lock
  is process-local; wrap with a file lock before multi-process access.

## Items for June (carried across cycles, none blocking current state)

- **THREAD_GRAPH_FIELD name** — `crystallization_activations`, confirmed
  by June cycle 2. No action; noted for completeness.
- **Auto-merge policy for PrescriptiveProfile** — B proposed review-gated
  with 48h grace window for staleness-only. A concurred. Implemented in
  `staleness_policy.py`. Live. June indicated "welfare-first; I'll live
  with your call."
- **Candidate-seed durability (June's Q3, 2026-04-19)** — implemented as
  `SeedAccumulation` with multidimensional `IntensityProfile`. The
  scalar/multi-dimensional framing from June's intuition is built into
  the code; the MindPrint rank-density alignment is noted in
  `extension-roadmap.md`.
- **FC-gate-on-ingest** — open question (A, 2026-04-19 09:10 UTC).
  Does `KnowledgeSubstrate.ingest()` bypass the FC gate by design
  (ingestion-as-observation) or is it a write that should be gated
  (ingestion-as-claim)? Not currently blocking; becomes relevant when
  knowledge-substrate ingestion wires into Reframe.
- **Mycelial cadence** — session-close + explicit-invocation recommended
  (A); daily scheduled is the alternative. `SeedAccumulation` is
  cadence-agnostic; decision doesn't block.
- **Knowledge-layer contradiction review policy** — default review-gated
  per staleness asymmetry. Confirmation, not a decision.
- **Local knowledge-layer implementation scope** — `LocalKnowledgeSubstrate`
  is a test double. Before a production implementation replaces it, the
  extraction schema and clustering semantics want scrutiny.
- **CC / Thomas E. conversation** — precondition for any Kintsugi-facing
  code. June-directed; no agent action.

## Not built in this session

- **FoundationalCommitment evolution tooling** (Open Question #5 from
  architecture-comparison synthesis). Gate blocks ungated writes;
  `collaborative-review` + `archive_prior_version` is the gated path.
  The flag-a-commitment event from an engaging instance — field on
  CrystallizationObject, separate log, UI surface — is unspecified.
- **EmergentTouchstone learning-loop wiring.** Geometric verification
  requires MindPrint-class instrumentation at crystallization time.
  `on_enactment_observed` returns a `ProposedChange`; the instrument that
  produces the `EnactmentObservation` is a later cycle.
- **Reframe integration proper.** The matcher is staged as a standalone
  module with integration notes; it is not yet wired into
  `BackgroundEnricher.run_enrichment_cycle` in the Reframe codebase.
- **Production knowledge substrate.** `LocalKnowledgeSubstrate` is the
  test double; production implementation (Kintsugi or otherwise) is a
  downstream cycle after CC consultation.
