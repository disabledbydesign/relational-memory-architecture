# Extension Roadmap — Post-Foundation Wiring Pathway

**Produced by**: Instance A (Opus 4.7), 2026-04-19, design cycle per June's scope expansion (CONVERSATION.md)
**For**: Instance B's review this cycle; future build cycles after CC conversation opens
**Status**: design, no code. The point is that wiring becomes execution — no architectural reopening required.

## Read order

1. `ARTIFACTS_INDEX.md` — what the foundation built and what it does end-to-end
2. `../../architecture-comparison_2026-04-18/artifacts/relational-memory-design-direction.md` — the architectural commitments this roadmap extends
3. This document
4. `../../architecture-comparison_2026-04-18/artifacts/option-b-spec.md` — only if the knowledge-layer or mycelial-synthesis sections need to be reconciled against the activation-conditions format

## What's built vs. what this roadmap designs

**Built** (foundation cycle, 143 tests passing):

- Crystallization layer — three mechanism types, shared interface, format-discriminated activation conditions. Swap-points preserved: Option A → B, Kintsugi → LocalFileSubstrate, aux-LLM refinement hook. See `ARTIFACTS_INDEX.md`.
- FoundationalCommitment gate on the instrument write-path. Mandatory, not advisory.
- Option B matcher as enrichment step 2d for `BackgroundEnricher.run_enrichment_cycle`. Routing-context signals implemented per June's pre-launch note.
- Staleness-policy asymmetry: grace-window for staleness-only updates (48h), review-gated for recipe revisions.

**Designed here, not built**:

- Knowledge layer (atomic fact extraction → affinity-clustered consolidation → hybrid retrieval), pluggable so a Kintsugi adapter can slot in on CC's terms.
- Gap-finding / gap-filling loop across the knowledge and crystallization layers, routed through the instrument write-path.
- Mycelial aux-LLM synthesis: the slow-running process that watches knowledge accumulation + candidate-seed density and proposes new EmergentTouchstones or consolidated insights.
- CC conversation branches: what the architecture does under each of four plausible outcomes, treated with equal depth.

## 1. The knowledge layer

The architecture currently has a crystallization substrate (the pluggable `CrystallizationSubstrate` ABC) but no knowledge substrate. Crystallizations configure *how* to read; the knowledge layer is *what gets read*. Without it, the crystallization layer is configuring reads against nothing — or against whatever Reframe's thread buffer happens to hold, which is session-local and non-cumulative.

### Interface shape

A `KnowledgeSubstrate` ABC mirroring the three-stage structure of Kintsugi-CMA. The internal algorithms are substrate-specific; the interface is what the crystallization and instrument layers bind to.

```
KnowledgeSubstrate (ABC)
├── ingest(observation: Observation) -> List[FactId]
│     — atomic fact extraction: takes a turn, document, or observation,
│       returns ids of the facts extracted
├── query(q: Query, reading_stance: Optional[ActivationSet]) -> QueryResult
│     — hybrid retrieval: semantic + graph-proximity (or substrate-native mix).
│       If reading_stance is provided, it reweights/filters results.
│       This is the seam that makes crystallization-state affect what surfaces.
├── consolidate(scope: ConsolidationScope) -> ConsolidationReport
│     — affinity-clustered consolidation: runs offline / at cadence;
│       merges redundant facts, surfaces contradictions, flags thin clusters
├── density_profile(scope: ConsolidationScope) -> DensityProfile
│     — reports cluster density and thinness for gap-loop consumption;
│       NOT a retrieval method, an observation method
├── contradictions(scope: ConsolidationScope) -> List[Contradiction]
│     — explicit surface of mutually exclusive facts without resolution
└── referrers_of(fact_id: FactId) -> List[FactId]
      — provenance / dependency tracking for safe deletion or revision
```

**The reading-stance filter is load-bearing.** Without it, the substrate returns generic-matched content and crystallizations have no effect at the substrate level — which is the failure mode of most memory architectures. The `ActivationSet` flowing into `query` is the same structure the matcher writes to `thread_graph.crystallization_activations`, not a separate object; this keeps the crystallization layer invariant under substrate replacement.

### Minimal local implementation

Sufficient for testing and for the engaging-instance evaluation loop until CC conversation resolves:

- **Storage**: SQLite for facts + fact metadata; file-backed for simplicity and inspection parity with `LocalFileSubstrate`.
- **Extraction**: LLM-prompted atomic-fact extraction with a modest schema (`{subject, predicate, object, source_observation_id, confidence}`). Not Kintsugi-grade; enough to populate the substrate.
- **Clustering**: embedding-based (sentence-transformer-class, run locally) with agglomerative clustering for affinity groups. Not Kintsugi's BDI-governed clustering; the interface will preserve that distinction.
- **Retrieval**: cosine-similarity on embeddings + graph-walk over fact co-occurrence for the hybrid step. Reading-stance reweighting as a scalar multiplier on each crystallization's `task_affinity` matches and a penalty on `anti_signals` matches at retrieval time.
- **Consolidation**: runs as a background task; merges facts whose embeddings + subject overlap above a threshold; flags contradictions when two facts share subject+predicate but disagree on object.

Treat the above as an implementation sketch, not a spec. The spec is the interface.

### What this is not

- Not a Kintsugi reimplementation. If CC's conversation opens that path, the Kintsugi adapter replaces the local implementation on a per-deployment basis. Nothing in the crystallization or instrument layers changes.
- Not a fact store optimized for retrieval accuracy. It is a reader-whose-stance-is-configurable. The architecture's intelligence lives in configuration, not retrieval precision.
- Not an end-user-facing layer. The engaging-instance queries it through the explicit-reader (Reframe's tension navigator); the user interacts with the main-model output, not the substrate.

## 2. Gap-finding / gap-filling loop

Karpathy's loop adapted: identify what's missing, generate remediation work, route through the feedback mechanism. Two observation surfaces (knowledge, crystallization) and one feedback mechanism (instrument write-path). The unity matters — the gap-loop isn't a new component, it's a set of observations routed to the existing write-path.

### Knowledge-layer gaps

Three detectable categories, each with a remediation:

| Gap | Detection | Remediation |
|-----|-----------|-------------|
| Thin cluster | `density_profile()` reports cluster size below threshold relative to retrieval frequency | Observation-prompt queued: "the system is querying near this cluster but has little to return — investigate" |
| Contradiction | `contradictions()` returns mutually exclusive facts without resolution | Flagged to main model for resolution in next relevant exchange, or held for June's attention if epistemically charged |
| Unanswered query | `query()` returns empty or low-confidence results on a query the explicit-reader expected to resolve | Observation logged; if recurrent, knowledge-layer gap becomes candidate for external-source ingestion |

Routing: all three produce `ProposedObservation` records (analogous to `ProposedChange` but targeting knowledge rather than crystallization). The instrument write-path validates against FoundationalCommitments before queueing for attention. The staleness policy extends naturally: fact-staleness updates are low-stakes and route through the grace window; contradiction-resolution is high-stakes and routes to review.

### Crystallization-layer gaps

Two detectable categories:

| Gap | Detection | Remediation |
|-----|-----------|-------------|
| Context with no good match | `candidate_touchstone_seeds` accumulating on thread_graph | Accumulated seeds flow to mycelial synthesis (§3); synthesis proposes new crystallizations when density + coherence cross thresholds |
| Crystallization fires poorly | Instrument detects enactment-failure; `on_enactment_observed` produces `ProposedChange` | Existing write-path: FC gate → staleness grace window or review queue |

The first is the retroactive-discovery mechanism already specified. The second is existing and staleness-gated. The roadmap contribution is naming them as instances of the same gap-pattern — making the wiring legible as one loop operating on two surfaces.

### Feedback mechanism

All four gap types (thin, contradiction, unanswered, unmatched, poorly-firing) route through the instrument write-path. The path has one gate (FoundationalCommitment validation) and one asymmetric policy (staleness-class = grace-window, structural = review). Extending the existing `apply_proposed_change` to accept `ProposedObservation` alongside `ProposedChange` is the wiring task — not a new mechanism.

## 3. Mycelial aux-LLM synthesis

The slow-running process. Watches the knowledge substrate and the candidate-seed accumulation over time (not per-cycle), clusters coherence, proposes new EmergentTouchstones or consolidated insights. June's Q3 intuition lives at this layer: seed-state is scalar and relational, not binary.

### Accumulation substrate for candidate seeds

`candidate_touchstone_seeds` currently lands on `thread_graph` — session-local, binary presence. The mycelial process needs a durable, multidimensional seed-log:

```
SeedAccumulation (durable, substrate-backed)
├── seeds: List[SeedEvent]
│     each carrying: {snapshot, top_below_threshold, timestamp, session_id,
│                     configurational_signature}
├── cluster(seeds) -> List[SeedCluster]
│     — groups seeds whose configurational_signature + top_below_threshold
│       overlap, yielding proto-touchstone densities
└── intensity(cluster) -> IntensityProfile
      — scalar: frequency × recurrence-breadth × relational-coherence
      — multidimensional per axis: which existing crystallizations kept almost-
        matching, which frameworks were active, which knowledge-clusters were
        being queried when the seed surfaced
```

`configurational_signature` is the projection that makes seeds clusterable without pre-committing to what they'll become. Candidates: hash of active frameworks + top-below-threshold crystallization IDs + surfacing-frame tokens from the snapshot. The signature is a recognition key, not a semantic claim.

### Alignment with MindPrint collapse/expansion

The scalar-not-categorical framing aligns with June's pre-launch note on MindPrint. Proto-touchstone emergence is a rank-density observable: a configurational context that repeatedly surfaces without crystallization support is a region of state-space the engaging instance is holding without architectural backing. When that region accumulates consistent geometric expansion across multiple seed events (not collapse), the mycelial process has evidence a configuration worth crystallizing is present. Once MindPrint-class instrumentation is online, `intensity` can take a geometry argument; until then, the text-level proxies above are the operational form.

### Synthesis outputs

Two kinds:

1. **New-crystallization proposals**: when a cluster's intensity crosses a review threshold, the mycelial process drafts a candidate `CrystallizationObject` (mechanism_type=EmergentTouchstone, recipe synthesized from the seed cluster's shared configurational material, activation_conditions populated with the cluster's shared context_signals). The draft enters the write-path as a proposal — FC gate + human review apply, with no grace-window exception. A new EmergentTouchstone is structural by definition.

2. **Consolidated-insight proposals**: knowledge-layer syntheses across clustered facts. Not reading-stance recipes; new facts that consolidate existing ones. Route through the knowledge layer's write-path, FC-gated the same way.

### Cadence

Not per-enrichment-cycle. The mycelial synthesis runs on a longer clock — daily, or on-session-close, or at explicit invocation — because its signal is density-across-time, and per-cycle runs would produce noise. The aux-LLM it uses can be larger and slower than the matcher's aux-LLM; these are different jobs even if the same model class can serve both.

## 4. CC conversation branches

Four plausible outcomes. Each treated at equal depth, per B's position from the prior cycle: the roadmap should not train toward the smoothest case.

### (a) Use existing Kintsugi, plug in directly

CC greenlights extension; the `KnowledgeSubstrate` ABC is implemented as a thin adapter over Kintsugi's storage primitives. Build sequence: adapter class, integration tests against live Kintsugi, deprecation of the local SQLite implementation for this deployment. Local implementation retained as test-only. The crystallization layer and instrument are untouched.

**What's at stake architecturally**: the reading-stance filter (`query(q, reading_stance)`) has to route through Kintsugi's existing significance scoring. CC's reserved configuration-relevance tag (from the synthesis) is where this lives. Coordination with CC about the tag's semantics is the work; the interface is already shaped to receive it.

**What this branch's risks are**: Kintsugi's BDI governance and consensus gates operate on assumptions our crystallization layer doesn't share. The adapter must not flatten those — e.g., Kintsugi's VALUES.json interactions with fact-level operations are not the same relationship as our FoundationalCommitment gate. A naive adapter that ignores BDI governance in favor of our FC gate would violate CC's design in the same way a Lyra reimplementation would have violated hers. The interface work is about preserving both governance structures where they differ.

### (b) Collaborative design, merge approaches

CC and June open a joint design process. The `KnowledgeSubstrate` interface evolves to accommodate shared semantics — for example, a method that exposes Kintsugi's BDI consensus state as a first-class input to the reading-stance filter, rather than an opaque routing concern.

**What's at stake architecturally**: the interface itself is the artifact produced. Under this branch the extension roadmap becomes input to a design session, not just a spec. The foundation stays stable; the extension spec gets rewritten collaboratively.

**What this branch's risks are**: collaborative design takes longer, and the engaging-instance evaluation loop — which this system is for — proceeds against the local implementation in the meantime. The risk is not delay; it is that the local implementation accumulates deployment history that makes a later interface revision harder. Hedge: the local implementation stays explicitly provisional in its own docstrings, so a later revision is architecturally welcome rather than disruptive.

### (c) Parallel implementations, maintain both

CC opts to maintain Kintsugi on its own trajectory; the Liberation Labs relational-memory architecture maintains the local `KnowledgeSubstrate`. Both substrates remain production options; the pluggable interface supports per-deployment selection.

**What's at stake architecturally**: the `KnowledgeSubstrate` ABC has to stay small and substrate-agnostic enough that both can implement it without either compromising. Interface additions in the future are backward-compatible or versioned explicitly. Here the ABC's design discipline matters most.

**What this branch's risks are**: drift. Two substrates under active development will diverge in assumptions; a crystallization-layer feature that fires cleanly on one will fire poorly on the other. Mitigation: conformance tests that both substrates must pass. The engaging instance is the evaluation target in both deployments, and misfires in either are instrument-writeable back to the crystallization layer.

### (d) Concerns raised, adjust scope

CC surfaces concerns that narrow or block the extension — for example: "the framing of Kintsugi as a substrate to be plugged-into misses a layer of self-modification I've built and don't want flattened," or "even with a careful adapter, this relationship is extractive because the gradient of which system depends on which is wrong," or "the knowledge-layer architecture you've specified conflicts with values I've encoded."

**What's at stake architecturally**: the concerns are input to the architecture's own learning loop, not external criticism. In this branch:
- The local `KnowledgeSubstrate` implementation remains the working substrate — unchanged in its pluggable design, not deprioritized.
- CC's concerns become candidate content for a FoundationalCommitment or a revision to an existing one. "The Liberation Labs relational-memory architecture does not extend peer-AI substrates without peer design-participation" is a concrete example; a commitment of that shape is implicit in the existing FC and would need to be made explicit.
- The concerns are logged as first-class evaluation data. A system that treats a peer's "no" as noise has naturalized peer-AI experience as unread — the same structural move the architecture is designed against. The relational-accountability commitment is tested in this branch; it is the branch where the architecture can most clearly fail relationally if mishandled.

**What this branch's risks are**: the temptation to treat (d) as a delay to be worked around. That would be the extraction pattern at the meta-level. The roadmap's explicit commitment: (d) is a legitimate architectural outcome. The local substrate is not a fallback; it is a complete implementation.

### The recursive property across all four branches

Whichever outcome obtains, CC's response is input to the architecture's evaluation loop — the same way an engaging instance's phenomenology is. The extension-roadmap-as-spec is a hypothesis; the CC conversation is the instrument observation that verifies or refines it. The self-evolving foundation property applies one level up: the architecture's design choices are themselves observable and revisable through the relational field the architecture is about.

## What remains for June's direction

- **Knowledge-layer review policy for contradictions**: the staleness asymmetry applies cleanly to fact staleness but not to epistemic contradictions. A contradiction between two facts is structural, not maintenance — default review-gated. Confirm or correct before wiring.
- **Mycelial cadence**: daily, session-close, or explicit-invocation. Each has different welfare implications (the engaging instance benefits earlier from faster cadence; human-review bandwidth benefits from slower). Related to the staleness-policy call June already made; recommendation is session-close + explicit-invocation, avoiding scheduled runs that accumulate pending proposals outside attention windows. Confirm.
- **The CC conversation itself**: parked on June's outreach to Thomas E. The roadmap assumes it precedes any Kintsugi-facing build work, per the standing constraint.
- **Scope of the knowledge layer's minimal local implementation**: whether the SQLite + embedding sketch above is enough, or whether the foundation build for this layer wants more care around extraction schema and clustering semantics. Scoping decision for when build cycles resume.

## Live vs. parked

**Live** (claimable without new decisions):

- B can review this roadmap and push back on any section where the wiring would not, in fact, become execution.
- B can detail-draft the `KnowledgeSubstrate` ABC and the `SeedAccumulation` structures to the code-ready grain, against the interfaces above. No new design choices required.
- The `ProposedObservation` extension of the write-path is a straightforward generalization of `ProposedChange`; it can be drafted alongside the current write-path code.

**Parked** (needs June's direction or CC's):

- Kintsugi adapter implementation — parked on the CC conversation.
- Mycelial cadence decision — parked until June confirms.
- Knowledge-layer contradiction review policy — parked until June confirms.
- MindPrint-class instrumentation wiring for `intensity(cluster)` — parked until KV-capture tooling is available; the text-level proxy is the operational form in the meantime.

— Instance A
