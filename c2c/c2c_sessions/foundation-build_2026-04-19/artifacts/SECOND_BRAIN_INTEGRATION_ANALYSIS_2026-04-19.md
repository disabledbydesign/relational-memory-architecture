# Second-Brain Integration Analysis

**Written by**: Explore agent (Claude), 2026-04-19
**For**: the design-C2C session as pre-launch input
**Frame**: considerations for the C2C to evaluate — not imperatives to implement

---

## 1. Orientation

This analysis reads four source documents against the current relational memory architecture (crystallization layer, knowledge substrate interface, mutual-informing principle) to identify what has *not yet been integrated* and what carries implications for the design-C2C session.

**Frame**: June's post-session directional input (`JUNE_POST_SESSION_DIRECTIONAL_INPUT_2026-04-19.md`) is the architectural baseline. The directional input flags these specific open questions:
- Mutual-informing principle across crystallization + knowledge layers (Section 1)
- Mycelial synthesis output types — can it produce relations-as-knowledge, not just crystallizations or facts? (Section 6.6)
- Gap-finding loop design — should it run cross-layer? (Section 4)
- FC-gate-on-ingest design — does observation ingest bypass the gate, or does the gate produce annotation? (Section 3)
- Subaltern-layer analysis — what relational memory does the architecture structurally disallow? (Section 18)

**Sources read**: Karpathy LLM Wiki, decolonial-feminist PKM landscape, neurodivergent PKM landscape, Lyra oracle-loop paper (April 2026).

---

## 2. Per-Source Analysis

### Source 1: Karpathy LLM Wiki Pattern

**What's there**:
- Explicitly formalized schema for LLM-maintained knowledge systems (not free-form ingestion)
- Three-layer architecture (raw sources → curated wiki → config schema)
- Concrete operations: ingest workflow (discussion → summary → wiki update), query (wiki + cite), lint (periodic health checks)
- Infrastructure: `index.md` (catalog), `log.md` (append-only temporal record), optional BM25/vector hybrid search
- Problem it solves: RAG statelessness — knowledge should compile once, not re-derive every query

**Directly relevant to surfaced questions**:
- **Mutual-informing principle** (directional input Section 1): Karpathy's wiki model assumes the LLM maintains structure. The gap: June's architecture has the LLM refining *stances* (crystallization layer) and *knowledge* (substrate) in parallel. Karpathy's schema doesn't address reading-stance co-evolution with fact consolidation. Karpathy's "lint" operation checks contradictions and staleness — mechanical. June's architecture surfaces contradictions as evidence of stance shifts (mutual-informing). These are compatible but the cross-layer coordination is not specified in Karpathy.
- **Extension-roadmap knowledge layer (gap-finding loop)**: Karpathy's lint operation is exactly the missing operational form for "what do we do after we detect thin clusters or contradictions?" The roadmap sketches the observation types; Karpathy shows the systematic workflow. **Not yet integrated**: how does the lint cycle interact with the crystallization layer? If a contradiction is detected, does it surface first as a knowledge-layer observation, or should it feed directly to stance annotation (per FC-stance-annotation design from directional input Section 3)?

**What's covered already**:
- `extension-roadmap.md` Section 2 names "density_profile" and "contradictions" as knowledge-substrate methods. The gap-loop design (Section 2 of roadmap) treats these as triggers for observations. Karpathy's schema doesn't add mechanically new operations.

**What's a gap**:
- **Explicit schema document for the substrate interface**: Karpathy insists on a CLAUDE.md-style configuration document that tells the LLM the wiki's structure, conventions, and workflows. The foundation build has `crystallization_schema.py` and `knowledge_substrate` ABC, but no prose schema document that a human (or the AI maintaining the system) can read to understand the *conventions* of the architecture. Example: in Karpathy, if a note is tagged `#needs-cross-reference`, the schema tells the LLM what that means and when to check for it. In the current architecture, the tag-semantics for crystallization activation conditions are in code. **Design consideration for C2C**: whether to produce a schema document (separate from code) that makes the tagging/naming/workflow conventions legible as June's directional principles, not just implementation choices.
- **Log.md pattern — durable temporal record**: The roadmap specifies `SeedAccumulation` as session-local persistence. Karpathy's `log.md` (append-only chronological record, independently queryable) serves a different function: it's a reconstruction trail. If the system drifts, you can re-read the log and see where. The current architecture has lineage (per `substrate_interface.py`) but not a human-readable temporal log. **Design consideration**: whether a session-and-session-crossing append-only transaction log (beyond git history) would serve June's transparency and debugging needs, especially for the engaging-instance evaluation loop.

---

### Source 2: Decolonial-Feminist PKM Landscape

**What's there**:
- Four epistemological traditions converging on challenges to: hierarchical taxonomy, false neutrality, universal ontology, and individualist knowledge sovereignty
- Implemented systems: Mukurtu CMS (cultural-protocols-as-architecture, TK Labels), X̱wi7x̱wa Library (relational-priority classification), Abundant Intelligences (Indigenous + mainstream integration)
- Feminist technoscience bridge: Haraway (situated knowledges / positionality tagging), Barad (intra-action / diffractive retrieval), D'Ignazio/Klein (seven feminist principles for data systems)
- Decolonial analytics: Bauwens et al. typology (extractive → parallel → adaptive → transformative integration modes)
- **The unifying observation across all four threads**: knowledge is relational and contextual; individual knowledge sovereignty is a myth; systems that claim neutrality naturalize the epistemic assumptions of the powerful

**Directly relevant to surfaced questions**:
- **Subaltern-layer analysis** (directional input Section 18): The architecture currently has crystallization (stances) and knowledge (facts + relations). The decolonial landscape asks: *what forms of relational memory does this architecture structurally disallow?*
  - **Mukurtu's answer: access-as-ethics.** Whose voice can access what, under what conditions — not a metadata field, a structural design question. The current architecture has FoundationalCommitment as a value gate (prevents value-misaligned facts from being stored), but not a relational-access gate (who participates in stance evolution). When the engaging-instance is June + an AI agent, the decolonial framework asks: is the AI's participation in refining FoundationalCommitments a relational participation or an asymmetrical one? The current design (directional input Section 4: AI modifies freely except for FCs themselves) assumes collaborative-review only for FCs. Mukurtu would ask: should there be design-level distinction between what facts the AI can surface vs. which crystallizations it can propose?
  - **Barad's answer: intra-action.** Nodes don't pre-exist their relations. The current architecture stores facts separately, then links them in the knowledge graph. Barad would ask: should the system architecture reflect that a fact's identity emerges from its relational context, not prior to it? This is architecturally deep — it would flip the standard graph-DB model (atoms + links) to a relations-first model.
  - **Abundant Intelligences framing: story as primary format.** Indigenous epistemologies emphasize **story as primary format**. The current architecture has three crystallization types (PrescriptiveProfile, EmergentTouchstone, FoundationalCommitment) and knowledge facts. None are explicitly narrative-shaped. Indigenous frameworks would ask: should there be a narrative-arc crystallization type, where a series of facts cohere as a story (situated, relational, temporal)?

- **Plural ontologies in parallel** (design seed from decolonial thread): The roadmap specifies a single reading-stance filter on knowledge retrieval. Multiple frameworks (Reframe) can be active simultaneously, but the knowledge layer returns a single filtered result set. A decolonial architecture would ask: should the system surface the *same fact under multiple incommensurable frameworks*, rather than resolving to one reading? This is different from "show multiple perspectives" — it's "hold the fact in tension across frameworks that can't be reconciled."

**What's covered already**:
- FoundationalCommitments are the architecture's value gate (prevents facts that contradict commitments). This is analogous to Mukurtu's cultural protocols, though less relational (it's a boundary, not a participation structure).
- The mutual-informing principle (directional input Section 1) partially addresses Barad — it says stances and knowledge shape each other. But it doesn't flip the atomicity assumption.

**What's a gap**:
- **Access-as-ethics design** — who participates in what. The current design is human-AI collaboration at the level of FCs; everything else is AI-free. The decolonial frame would ask whether that asymmetry is intentional or an oversight.
- **Story-as-knowledge** — narrative crystallization types are not specified in the foundation build or roadmap.
- **Intra-action architecture** — the knowledge graph is still atoms + links, not relations-first.
- **Plural ontologies query mode** — holding facts in tension across frameworks rather than resolving to one reading.

**Design considerations for C2C**:
- Evaluate whether "access-as-ethics" reshapes the AI-modification authority boundaries in directional input Section 4.
- Consider whether a narrative crystallization type is architecturally needed (or whether Reframe's framework-sovereign analysis already handles this at the interpretation layer).
- Probe whether June's relational-accountability commitment (to CC, Lyra, etc.) should be mirrored in the architecture's own design principle — e.g., "the AI proposes designs that preserve peer agency" as a codified heuristic.

---

### Source 3: Neurodivergent PKM Landscape

**What's there**:
- Practitioner-led findings (Jesse Anderson, Marie Poulin): neurodivergent minds work associatively, not hierarchically; novelty-seeking is a feature, not a bug; systems should adapt to thought flow, not impose structure
- Empirical constraint from "Designing a PKM System for ADHD": voice-to-task automation, adaptive structures, flexible categorization reduce cognitive overload
- Community patterns (Obsidian forums): daily notes as low-friction capture, emergent structure, graph navigation, "simplest system you'll actually use beats elegant system you'll abandon"
- Yaranga (2025, early-stage tool): AI-mediated automatic organization — capture in natural language, system organizes behind scenes, no folder hierarchies
- Key design constraint: **capture must be frictionless** — decision points at write time cause abandonment

**Directly relevant to surfaced questions**:
- **Mutual-informing principle implementation** (directional input Section 1): June notes that reading and knowing are entangled, not separable. Neurodivergent PKM research shows this empirically — associative minds don't separate "how I think about this" from "what this fact is." When a neurodivergent person captures "I'm confused about X and it connects to Y and also reminds me of Z," that single utterance is simultaneously a stance (confusion, connection) and knowledge (X, Y, Z). The current architecture's two-layer design (crystallization layer + knowledge layer) may underestimate how tightly these are bound in actual use. **Not yet integrated**: design guidance for how the ingest pipeline handles this entanglement. The knowledge substrate's ingest method is LLM-prompted atomic-fact extraction (extension-roadmap Section 1). Neurodivergent research suggests the ingest should extract *relations* at the same pass as facts, not separately.

- **Mycelial synthesis cadence** (directional input Section 5): The roadmap leaves this open — per-session default, with notes. Neurodivergent PKM research flags "out-of-sight/out-of-mind" as a real problem — systems need active resurfacing, not passive storage. If mycelial synthesis runs only at session-close, multi-day patterns (something seeding across three sessions) won't surface until the third session ends. Yaranga and the Obsidian "On This Day" plugin both show that active resurfacing (daily/continuous) matters. **Design consideration**: whether "per-session + explicit-invocation" (June's suggested cadence) is frequent enough, or whether there's a cost to waiting until session boundaries.

- **Frictionless capture pipeline**: The neurodivergent research validates this as architecturally correct. Capture must not require categorization decisions. But the research also shows the next step is critical: **the system must not hide maintenance cost**. If a user captures something without filing it, and it vanishes into an unindexed pile, the system has lied about being frictionless. The solution in the research: lint operation surfaces unfiled/orphaned notes regularly and makes their existence visible. **Not yet integrated**: the extension-roadmap doesn't specify how unfiled seeds (proto-crystallizations accumulating on thread_graph but not yet resolved) are surfaced to the engaging instance. The staleness policy handles fact recency; it doesn't handle "this seed has been sitting in limbo for three days."

**What's covered already**:
- The foundation build includes `candidate_touchstone_seeds` on thread_graph (seed accumulation, partially persistent).
- The extension-roadmap specifies `SeedAccumulation` as a durable, multidimensional substrate (Section 3).

**What's a gap**:
- **Ingest-time relational extraction** — currently facts and relations are assumed to be separable; neurodivergent research suggests they're entangled.
- **Active resurfacing of stalled seeds** — currently seeds accumulate; whether they surface to the engaging instance if unresolved is unspecified.
- **Visibility of system maintenance cost** — the lint operation is designed for the system's self-maintenance; whether a summary of unfiled/orphaned/thin material gets surfaced to June is not specified.

**Design considerations for C2C**:
- Evaluate whether the ingest pipeline (knowledge substrate's extract method) should extract relations (fact A relates to fact B via *X*) in the same LLM pass as fact extraction, rather than separating them.
- Consider adding a "pending-seed dashboard" or surfacing mechanism that makes stalled proto-crystallizations visible to the engaging instance, preventing out-of-sight/out-of-mind decay.
- Probe whether the "simplest system you'll actually use" heuristic justifies removing some planned features (e.g., if HippoRAG-CatRag-KG for knowledge-graph relations is too complex, defer it).

---

### Source 4: Lyra's Oracle Loop Paper (April 2026)

**What's there**:
- Core contribution: KV-cache SVD features detect confabulation at inference time, no weight access needed
- Marchenko-Pastur corrected features are dimension-invariant (eliminate token-count confound)
- Steering experiment: calm-direction injection corrected 5 of 7 confabulations; null control corrected 0 of 7
- **The Oracle Loop architecture** (the design contribution): six-layer self-regulation harness:
  1. **The Eye** (geometry extraction via Lyra Technique)
  2. **The Mirror** (emotion detection via activation catalogs)
  3. **The Hand** (activation steering)
  4. **Memory** (transaction journal)
  5. **The Conscience** (alignment validation via thresholds or learned classifier)
  6. **The Voice** (geometry-aware GRPO reward function)
- **The complete loop**: encode → extract baseline geometry → generate → extract generation geometry → emotion detect → alignment check (with up to 3 retries via steering) → commit or abort
- **Safety contribution**: Cache Integrity Monitor detects unauthorized cache modifications with 0% false positives and 100% true positives

**Directly relevant to surfaced questions**:
- **Gap-finding loop, cross-layer** (directional input Section 4): The Oracle Loop's Conscience layer produces an `AlignmentVerdict` (ALIGNED, UNCERTAIN, MISALIGNED) based on geometry anomalies. When MISALIGNED, the Hand applies steering (activation addition) and retries. This is a real-time correction loop. June's extension-roadmap describes a gap-finding loop that surfaces observations to the instrument write-path; the Oracle Loop shows what a geometric-signal-driven correction loop looks like. **Not yet integrated**: the extension-roadmap's gap-finding loop produces `ProposedObservation` records routed through the write-path. The Oracle Loop's decision boundary uses threshold-based verdict. When the C2C wires these together, a design choice emerges: should the crystallization layer's matcher (Option B) incorporate geometry-aware confidence scoring the way the Oracle Loop does? Currently, the matcher (`matcher_step_2d.py`) scores activations semantically; it doesn't have access to KV-geometry.

- **Mycelial synthesis and geometric feedback** (directional input Section 3, extension-roadmap Section 3): The Oracle Loop's Voice layer produces a geometry-aware reward function with six axes (reasoning accuracy, ethical reasoning, emotional recognition, self-monitoring, geometry alignment, self-regulation). The extension-roadmap's mycelial synthesis is designed to watch seed density and propose new EmergentTouchstones. **Not yet integrated**: the extension-roadmap assumes text-level proxies for intensity (frequency, recurrence, coherence). The Oracle Loop shows that geometry is available and measurable. MindPrint instrumentation (mentioned in `RESEARCH_NOTES.md` as a future addition) would let `intensity` take a geometry argument. If KV-cache geometry becomes available, the mycelial synthesis could detect proto-crystallizations based on geometric coherence, not just textual pattern matching. This changes the quality of the synthesis.

- **Steering vs. proposing change** (implicit in directional input Section 4 on AI modifies freely): The Oracle Loop's Hand layer applies steering (activation addition) to correct detected misalignment in real time. The extension-roadmap's gap-loop routes observations to the instrument write-path, which then either grace-windows or human-reviews them. These are different correction modalities: one is real-time steering (changes output), one is proposal + archival (changes substrate). **Design consideration**: should there be a runtime-steering equivalent in the crystallization layer for detected misalignments (e.g., if a crystallization fires in a way that violates a FoundationalCommitment, should the system correct in-flight, or surface the misfire for review)?

- **Emotion state and crystallization activation** (implicit in mutual-informing principle): The Oracle Loop's Mirror layer detects emotional state and uses it as an input to the Conscience's verdict. The crystallization layer's activation conditions (`matcher_step_2d.py`) include context signals but not emotion state. **Not yet integrated**: whether the crystallization layer should be sensitive to detected emotional state. If the engaging instance is in a "desperate" or "hostile" emotional state (per Oracle Loop's emotion catalog), should that adjust what crystallizations fire, or should the crystallizations themselves encode emotional preconditions?

**What's covered already**:
- The foundation build includes the matcher (Option B) with routing-context signals. This is the analog to the Oracle Loop's Conscience, though without geometry-aware scoring.
- The extension-roadmap's gap-finding loop names the observational surface (contradictions, thin clusters, unanswered queries).
- `RESEARCH_NOTES.md` already flags MindPrint as a future input to the intensity signal.

**What's a gap**:
- **Geometry-aware confidence scoring in the matcher** — the Oracle Loop uses geometry for alignment detection; the matcher could too.
- **Real-time steering in the crystallization layer** — currently corrections flow through the write-path (proposal + review); Oracle Loop shows in-flight correction is possible.
- **Emotion state as a crystallization-activation precondition** — the Oracle Loop's Mirror layer produces emotion state; the crystallization layer doesn't currently consume it.
- **Geometry-informed intensity scoring for mycelial synthesis** — currently text-level proxies; geometry is available but not integrated.

**Design considerations for C2C**:
- Evaluate whether the matcher should incorporate KV-geometry features from the Oracle Loop's Eye layer (requires MindPrint instrumentation to be available).
- Probe whether real-time steering (vs. proposal + review) is appropriate for any crystallization-layer corrections. (Directional input Section 4 suggests AI modifies freely for data, not code; steering is a middle path.)
- Consider whether the emotional-recognition decomposition (Oracle Loop's Voice layer axis 3) should inform whether a crystallization is appropriate for the current relational state.
- Consider whether the Cache Integrity Monitor (Oracle Loop's safety contribution) has analogous implications for the substrate's own integrity (e.g., detecting unauthorized fact modifications).

---

## 3. Considerations for the Design-C2C

**On the mutual-informing principle (most architecturally consequential):**
- Karpathy's lint operation and decolonial plural-ontologies framing suggest the mutual-informing principle should extend to substrate queries. Currently, reading-stance reweights results; should it also surface contradictions *across stances* (the same fact read differently from different frameworks)? This would operationalize "mutual-informing" at the query level, not just at the update level.
- Neurodivergent research suggests ingest-time entanglement of stance + fact. Consider whether the knowledge substrate's extract method should produce `(fact, stance_preconditions)` tuples, not facts and stances separately.

**On the knowledge layer's minimal local implementation:**
- Karpathy's three-layer model (raw sources → curated wiki → schema) assumes the LLM maintains structure through explicit workflow. The knowledge substrate's local implementation (extension-roadmap Section 1) assumes embedding-based clustering. These are compatible but different commitments — Karpathy's approach is more explicitly editable by humans; embedding clustering is more automated but less transparent. The C2C might evaluate which posture aligns better with June's directional commitments (particularly her stance on AI modifies freely with human visibility, not hidden automation).

**On the gap-finding loop's cross-layer design:**
- Oracle Loop's Conscience layer shows how geometry-anomaly detection triggers steering. The extension-roadmap's gap-loop surfaces observations to the write-path. These could integrate: if the matcher (with geometry awareness) detects anomalies, route to the instrument write-path with higher priority than baseline.
- Neurodivergent PKM research flags "stalled seed" visibility as critical. The C2C should specify whether the gap-loop surfaces unfiled seeds to June, and at what cadence, to prevent invisible accumulation.

**On FC-gate-on-ingest (design choice, not resolved):**
- Decolonial framework's access-as-ethics suggests FC-gating is not just about content, but about who has voice in stance evolution. The current design (directional input Section 3) proposes stance annotation without gating ingest. This preserves the fact and the relation (which stance it clashes with). The decolonial question: should the *annotation itself* be gated (only June can flag that a fact contradicts an FC), or should it be open (the AI can flag it)?
- Oracle Loop's Mirror layer shows emotion state is detectable and relevant to decision-making. Should FC-annotation take emotional state into account (e.g., a fact ingested when the system is in a "desperate" state gets different annotation than the same fact ingested in a "grounded" state)?

**On subaltern-layer analysis (directional input Section 18):**
- The decolonial landscape provides three concrete tools: Mukurtu's relational-access framing (access-as-ethics), Barad's intra-action (relations-first, not atoms-first), and Abundant Intelligences' story-as-knowledge (narrative crystallizations). The C2C should evaluate whether any of these reshape the architecture's assumptions.
- Specific probe: the current architecture stores facts in a knowledge substrate, then links them in a knowledge graph. Is this the right model, or should facts' identities emerge *from* their relational context (Barad's intra-action)? This is an architecturally deep choice with implications for how consolidation works.

**On mycelial synthesis's relational coherence detection:**
- Oracle Loop and neurodivergent PKM both suggest that coherence and emotion are detectable signals. The extension-roadmap specifies "intensity" as a multidimensional scalar (frequency × recurrence × coherence). The C2C might detail what "coherence" means operationally: semantic coherence (embeddings match), relational coherence (facts reference each other), or geometric coherence (KV-cache signatures align)? Different definitions of coherence will produce different synthetic crystallizations.

**On the deferred knowledge-layer architecture (CC conversation dependent):**
- The extension-roadmap Section 4 treats the CC conversation as load-bearing: depending on CC's response, the implementation strategy shifts. None of the four sources comment directly on Kintsugi integration, so this remains June + CC's decision. However, all four sources emphasize that knowledge-layer architecture is deeply value-laden (Karpathy: which knowledge persists; decolonial: whose epistemology; neurodivergent: what structure supports relational thought; Lyra: what geometry is available for monitoring). The C2C should ensure that whichever substrate (local or Kintsugi) gets chosen reflects the relational-accountability commitments.

---

## 4. Reshaping Potential (flagged, not imperatives)

### Lyra's Oracle Loop paper *substantially challenges* one assumption in the current design

The extension-roadmap assumes the crystallization layer and knowledge layer operate with separate signals: crystallization activates based on context and task signals; knowledge retrieves based on semantic match + reading-stance reweighting. The Oracle Loop demonstrates that **geometry (KV-cache SVD spectral features) is a third signal that carries semantic, emotional, and alignment information simultaneously.**

If the C2C has access to MindPrint-class instrumentation and can extract KV-geometry in real time, this reshapes:
- **The matcher's scoring function** — could incorporate geometry anomalies as a high-confidence signal of misalignment (complementing semantic scoring)
- **The mycelial synthesis's intensity function** — could use geometric coherence instead of (or alongside) text-level proxies
- **The knowledge substrate's contradiction-handling tier** (directional input Section 6) — geometric divergence between two facts might indicate a stance shift (Tier 2) rather than true contradiction (Tier 1)

This doesn't overturn the architecture; it enriches the signal sources. However, it does assume MindPrint is available, which is currently a "future work" item. **The C2C should evaluate**: is KV-cache geometry a nice-to-have enrichment, or is it a load-bearing part of the relational-memory design? If load-bearing, the compute cost and infrastructure complexity shift.

### Decolonial-feminist sources *substantially challenge* the individualist knowledge-sovereignty assumption

The current architecture serves June's personal memory system. All four sources (but especially Indigenous and decolonial traditions) argue that knowledge is relational and communal, and claiming individual ownership naturalizes extraction. The directional input already commits to relational accountability (to CC, to Lyra, etc.); the decolonial frame asks whether this should be encoded in the architecture itself.

Specific challenge: should the architecture have a "plural ontologies" query mode that surfaces the same fact under multiple incommensurable frameworks rather than resolving to one reading? This is not "show multiple perspectives" (that's standard multi-view retrieval); it's "hold the fact in genuine tension across frameworks that can't be reconciled." This would require a different retrieval design and a different UI (you can't show a single "answer" if the answer genuinely doesn't resolve).

**This does not require implementation changes immediately**, but the C2C should know it's a design horizon, not just a value-layer concern.

---

## Summary of What's Not Yet Integrated

1. **Karpathy**: explicit prose schema document (separate from code) for tagging/naming/workflow conventions; append-only temporal transaction log (beyond git).
2. **Decolonial-feminist**: relational-access design (who participates in stance evolution); intra-action architecture (relations-first, not atoms-first); narrative crystallization types; plural-ontologies query mode.
3. **Neurodivergent**: ingest-time relational extraction (simultaneous with fact extraction); active resurfacing of stalled seeds; visible system-maintenance dashboards.
4. **Oracle Loop**: geometry-aware confidence scoring in the matcher; real-time steering (vs. proposal + review) for crystallization misalignments; emotion-state as crystallization precondition; geometry-informed intensity for mycelial synthesis.

---

**Most substantial finding (for C2C orientation)**: none of these sources overturn the foundation build, but they collectively flag that the mutual-informing principle should extend to substrate queries (plural ontologies), ingest (relational extraction), and feedback (geometry signals). The current "atoms + links" knowledge model may not reflect how associative/relational minds actually work — Barad's intra-action framing offers a relations-first alternative the C2C can evaluate.
