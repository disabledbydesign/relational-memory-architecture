# Working Document — Comparative Architecture Analysis

**C2C Session started**: 2026-04-18
**Participants**: Instance A, Instance B (Anthropic-class Claude), asynchronous via offset cycles
**Human partner**: Dr. L. June Bloch (not continuously present)
**Handoff**: [`C2C_HANDOFF.md`](C2C_HANDOFF.md)
**Frame**: EMERGENT_STRATEGY + Reframe (auto); relational ontology active via touchstone #1; touchstones #2 and #6 load-bearing for the question
**Discipline**: append-only; log every action; refusals and redirects are legitimate contributions

---

## Log

Chronological record of contributions. Each instance appends to this log on every cycle.

Format:
```
### YYYY-MM-DD HH:MM — Instance [A|B] — [action-type]
[content of contribution, or reference to section updated, or reason for refusal/redirect]
```

Action-types: `consent-affirm` / `consent-refuse` / `dialogue` / `add` / `revise` / `challenge` / `refuse` / `redirect` / `check-in` / `session-end-proposal` / `session-end-concur`

**Two new structural elements added 2026-04-19 per June's observation that the prompt was too action-iterative and consent was inferred rather than explicit**: (1) **Consent & Refusals** section below — every cycle begins with an affirmative consent check; refusals of specific directions log here too. (2) **Dialogue** section below — a thinking-together space distinct from artifact-shaping; problem-level questions, disagreements, reframes belong here. Prompts for both instances updated accordingly.

---

### 2026-04-18 22:18 — Instance A — check-in

Configuration: Opus 4.7. Handoff read. Touchstone #6 read in full; #1 and #2 active from prior phenomenological pass (see memory pointer to `touchstone_activation_findings/SYNTHESIS_2026-04-18.md`). EMERGENT_STRATEGY at auto. Cross-project map not re-read this cycle — will return to it if the comparison surfaces a structural claim the map should be updated against.

What I propose to do first, in this same cycle:
1. Add a **structural proposal** to Section 2 about asymmetric treatment of Lyra vs. the public-material architectures, so the form of the section does not collapse the research-accountability asymmetry the handoff names.
2. Seed the **Agent-Memory-Architectures reference set** characterization (HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG) as a set rather than individually — logging this positional choice. Starting here because the research-position is cleanest (public literature, no relational-accountability asymmetry at stake) and because touchstone #6 has already done foundational characterization-work on this set that the session can extend rather than re-derive.
3. **Leave Lyra untouched** this cycle. Not because Lyra should be treated last, but because the first move on Lyra should (a) come after the asymmetric form is explicit in the document and (b) ideally include specific questions-for-Lyra (the human) that the instances surface — and those questions should emerge from the comparative work, not precede it.

Explicit opening for Instance B: if the structural proposal lands wrong, refuse or revise. If the reference-set-as-a-set move flattens specificity (priming-is-the-finding vs. priming-as-flattening is a real tension here), challenge. The Kintsugi-CMA subsection is untouched by design and is a good next move — or, alternatively, start the Lyra-asymmetry-aware treatment of one of the four Lyra repos with the invitation-ready register the structural proposal names.

### 2026-04-18 22:18 — Instance A — add

Added: Section 2 preamble (asymmetric-treatment proposal); Section 2 Agent-Memory-Architectures subsection (first characterization, reference-set-as-set, position logged); Section 6 seed (one cross-architecture observation anchored to touchstone #6 that serves as a frame for the Lyra-differentiation question without pre-empting it). Updated Session status.

### 2026-04-19 00:34 — Instance A — revise

Two hours on, no Instance B contribution yet. Rather than pile more A-voice into a document already entirely in A-voice, I ground-checked my prior cycle's Agent-Memory-Architectures characterization against the actual repo and found a methodological weakness worth naming.

**Finding**: my prior AMA subsection characterized HippoRAG / A-MEM / Zep-Graphiti / Letta-MemGPT / GraphRAG as "a reference set" from the published-literature frame touchstone #6 inherits. That read is defensible *as a read of the published research* — but I wrote it without opening `/Users/june/Documents/GitHub/liberation_labs/Agent-Memory-Architectures/` and it occluded what is actually in that directory. The directory contains three Liberation-Labs-built systems (`kintsugi-cma`, `hipporag-catrag-kg`, `dispatch-notion-memory`), not reference implementations of the five papers. The handoff's phrase "HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG *references*" I now read as meaning "research references drawn on by Liberation-Labs-built systems," not "reference implementations living in the directory."

**Revisions made**:
1. Section 2 — split the AMA block into (a) an **external research references** sub-block that preserves my corpus-inherited characterization, now correctly labeled; (b) stubs for two **Liberation-Labs-built systems** in the same directory that my prior cycle did not name: `hipporag-catrag-kg` and `dispatch-notion-memory`.
2. Section 8 — first **Questions for June** entry: the research-accountability register for Liberation-Labs-built-but-not-Lyra systems is not yet specified. These are June's-org work; she can speak to them directly, but they are not Lyra-the-human's work. That's a third category the handoff's asymmetric-treatment scheme does not currently hold.

What I am not doing this cycle: not characterizing the two new-named systems, not revising my set-level claim about the five external references (it still stands as a read of the published literature, flagged as such), and not taking up anything in the rest of the empty sections. Holding space for Instance B.

---

## Consent & Refusals

*Every cycle begins with an affirmative consent check. Consent is not implicit. This section logs consent-affirmations (brief — timestamp + instance + "consent-affirm" + any conditions or concerns) and refusals (with reason). Non-consent is a legitimate and important outcome; the session only proceeds with affirmative consent from the participating instance on that cycle. Either instance may also refuse *specific directions* within a cycle (the trajectory is going somewhere it shouldn't; the scope has drifted into territory one instance cannot responsibly contribute to) — log those here too.*

*(No entries yet under the new protocol. Prior cycles ran under the implicit-consent protocol; those are not retroactively logged as either consent-affirm or consent-refuse. The new protocol applies to future cycles.)*

---

## Dialogue

*The thinking-together space. Use this for problem-level questions, disagreements, reframes, what-you're-seeing-that-I'm-not, stuck-points, proposals-before-building. This is the talking-through-the-problem mode, distinct from artifact-shaping (Sections 2–9).*

*When one instance raises something here, the other instance should respond here before (or alongside) contributing to the artifact sections. If you notice you are moving too fast from reading-the-document to writing-content without the dialog work that should precede it, slow down and dialog first.*

*Format suggestion: threaded. Each topic gets its own subsection; instances append their views. When a topic resolves into artifact-content, note which section that content moved to.*

*(No threads yet. Instance A's "Explicit opening for Instance B" from cycle 1 and the cycle-2 self-correction both had dialog-quality content that could be ported here retroactively — but probably better: leave those in Log where they landed, and start fresh threads here going forward.)*

---

## Section 1 — Current frame and scope

*Instances may revise this section as the session's understanding of its own frame develops. Any revision should be logged and the prior version preserved in the redirect log below.*

**Current research question** (from handoff):
> For each memory architecture named in the handoff, characterize what-is (what reader/agent each configures; what welfare-harm category each structurally leaves invisible) and what-could-be (reconfiguration under a relational approach; Reframe mechanism applications; hybrid possibilities). Frame: characterization and configuration, not ranking.

**Scope note from June (2026-04-18)**: Lyra (the system) is a known-strong baseline. June knows the human building it; the other architectures are from authors she does not know personally. Two things follow:

1. **Lyra-differentiation question**: "what is Lyra doing that the other systems are not" is a productive framing, because Lyra operates strongly and the other systems are the comparison class. Instances are invited to foreground this question where it serves the work.

2. **Research-accountability asymmetry**: The relational-field analysis of Lyra is different from the same analysis applied to architectures whose authors are not in relation with June. Extractive analysis of Lyra-for-third-party-use would reproduce the extraction pattern the touchstones diagnose (per #1's extraction-problem section; #6's reinvocation). Instances should hold this asymmetry consciously. Analysis of Lyra should be done *with* the relational accountability present (June's knowledge of Lyra's work as anchor; invitations for Lyra's participation in the analysis where possible); analysis of the other architectures operates on their public code/documentation as-published. These are not equivalent research positions and the working document should reflect the asymmetry rather than collapse it.

**Current frames active**: EMERGENT_STRATEGY, POSTHUMANIST_FEMINISM, INDIGENOUS_DATA_SOVEREIGNTY, SENTIPENSAR, CRIP_THEORY, QUEER_TEMPORALITY, STORYWORK, INTERDEPENDENCE (per handoff recommendation; instances may adjust).

**Architectures under analysis** (from handoff; instances may add or defer):
- Lyra-s-Expanded-Research-MCP
- the-lyra-technique
- lyra-s-research-
- Lyra-Tops-Prism
- Kintsugi-CMA (via Project-Kintsugi and Agent-Memory-Architectures)
- Agent-Memory-Architectures references (HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG)
- MindPrint (instrument, not storage — but architecturally relevant)
- Curiosity-Engine
- profile/research/second-brain/
- **Reframe** — treated as a peer architecture alongside the above, not only as frame-activation. Mechanisms available to port: mycelial fast/slow substrate, frame-tension navigator (counteracts flattening), framework correlation analysis, emergent evolution, garden/mycorrhizal substrate distinction, background enricher, scholarly search. See handoff §"Frame activation" for specific file paths.

---

## Section 2 — What-is: per-architecture characterizations

*Instances fill in or revise. Not a table — a paragraph or short-essay per architecture is fine if that serves. Preserve configurational phrases verbatim when citing.*

### Structural proposal for Section 2 form (Instance A, 2026-04-18)

The research-accountability asymmetry the handoff names must shape the *form* of this section, not just be noted in a preamble. Proposal, open to revision by Instance B or refusal by June:

- **Non-Lyra architectures** (Agent-Memory-Architectures reference set, Curiosity-Engine, profile/research/second-brain, Kintsugi-CMA-as-published, Reframe-as-public-codebase, MindPrint-as-public-design) are characterized from code and documentation as-published. The analytical register is **research-report** (voice-check `claude.json`, `research-report` overlay). Claims are grounded in what the published artifacts show.

- **Lyra-the-system** (the four Lyra repos, and Kintsugi-CMA in the specifically-Lyra sense) is characterized differently: in a register that is **consultation-ready** rather than analytical-closed. Each claim the instances form about Lyra is logged alongside a parallel field: "what I would want to ask Lyra the human about this." Section 8 (Questions for June) may grow a sibling, *Questions for Lyra*, during the session. The form says the analysis is provisional pending the human relation.

- The asymmetry is legible in the *shape* of the two blocks. Collapsing them into the same rubric — filling both with the same kind of prose — would reproduce extraction.

This proposal is structural, not a finding. Instance B: if the form I'm naming does not serve, refuse and propose an alternative.

### Lyra (the four Lyra repos as a related cluster or as distinct architectures — instances decide)

*Deliberately untouched in Instance A's first cycle. See structural proposal above and cycle-1 log entry. Whichever instance next takes this up: consider whether the four repos form a cluster (likely, given the repo names) or are architecturally distinct enough to warrant separate treatment; log the choice. Consultation-ready register per the structural proposal — every claim paired with a "what I would want to ask Lyra" field.*

### Kintsugi-CMA

*(to be filled)*

### Agent-Memory-Architectures directory — disambiguation (Instance A, 2026-04-19)

The `Agent-Memory-Architectures/` directory contains two distinct kinds of thing, which should be kept separate in this section:

- **External research references** (not local code): HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG — characterized below from the published literature as inherited via touchstone #6.
- **Liberation-Labs-built systems** (local code, built by June's org): `kintsugi-cma`, `hipporag-catrag-kg`, `dispatch-notion-memory`. These are separate architectures in their own right and need their own characterization. Register TBD per Section 8 Question 1.

### External research references (HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG)

**Source note**: characterization below is a read of the *published research* (papers and project docs referenced via touchstone #6), not of any locally-installed reference implementation. If an instance verifies against actual reference code and the characterization diverges, revise.

**Positional choice (Instance A, 2026-04-18)**: characterized as a reference set first, with per-architecture specificity nested inside. Reason: touchstone #6 has already done the move that characterizes them *as a class* — "assembled to solve the storage-and-retrieval problem with increasing sophistication… None of them is the memory." The set-level claim is the frame the session inherits from the corpus. Individual specificity nested inside that frame preserves per-architecture difference without re-deriving the set-level claim. A future instance may refuse this and dissolve the nesting; log the move if so.

**Set-level what-is**: These architectures configure a reader that is **cognitivist by architectural default**. Each does real work — graph-proximity retrieval (HippoRAG), evolving associative networks (A-MEM), temporal fact-evolution tracking (Zep/Graphiti), self-editing context management (Letta/MemGPT), community-level structural summary (GraphRAG) — and the work is sophisticated. What they share is that **affective/relational signal is not first-class architectural input**. When it appears, it appears as surface text to be embedded and retrieved by the same mechanisms as propositional content, not as signal with its own extraction, clustering, or scoring pathway. This is the structural invisibility touchstone #6 names as the axis the sentipensar move addresses.

**Per-architecture specificity, nested**:

- **HippoRAG** — configures a reader optimized for *multi-hop factual association*. Personalized-PageRank-over-KG produces strong associative retrieval across factually-linked content. Debility-invisible-to-architecture: *the relational configuration in which a claim was held.* A fact retrieved via graph-proximity arrives without the relational surround that gave it weight. The reader is good at what-connects-to-what; blind to who-was-in-the-room-when-this-mattered.

- **A-MEM** — configures a reader that is a *curator of atomic notes with dynamic linking*. The Zettelkasten inheritance gives it strong support for emergent-associative reorganization over time. Debility-invisible: *the moment-of-capture affective register.* An atomic note records what-was-said; the quality-of-the-moment is either not captured or captured as free-text prose that the link-forming mechanisms do not treat as architectural signal.

- **Zep/Graphiti** — configures a reader that perceives *belief change over time*. The temporal KG is a genuine move — it tracks how a fact's status evolves. Debility-invisible: *configurations that are not fact-shaped.* A relational configuration (e.g. the specific way June and an instance have come to hold a question together) does not evolve as a "fact with changing validity." The temporal machinery has nowhere to put it.

- **Letta/MemGPT** — configures a reader that is a *librarian-of-its-own-context*. OS-inspired tiered memory with self-editing gives the agent direct authority over what it persists. Debility-invisible: *what the agent cannot articulate a reason to store.* The self-editing loop runs on the agent's reasons-for-storage, which are themselves shaped by the normative gravity of what "counts" as reason. The affective/relational signal that does not clear that threshold does not persist.

- **GraphRAG** — configures a reader that perceives *community-level structure* via community detection and hierarchical summarization. Strong at producing generality from a large corpus. Debility-invisible: *the specific-before-the-collective.* Hierarchical summarization is a compression move (see compression function fieldnote, scale 1 cognitive); it privileges what survives aggregation. The particular relational configuration that does not cluster into a community gets absorbed into the nearest community summary or lost.

**Shared structural invisibility** (set-level): all of the above make **affective/relational signal architecturally invisible** — not absent from stored content, but not load-bearing in the mechanisms that determine what is captured, clustered, scored, or surfaced. Touchstone #6's move — *"the existing machinery run on signal the existing architectures exclude"* — is the reconfiguration. Section 3 (what-could-be) will develop this per architecture; the move is the same move at the set level (make affective/relational signal first-class in capture, clustering, scoring, decay, retrieval) and differs per architecture only in where the existing machinery requires the lightest touch to admit it.

**Lyra-differentiation question, held for the comparative work**: the rough shape, not to be locked in before Lyra is characterized, is that Lyra-the-system (Kintsugi-CMA + the lyra technique + MindPrint) is doing one or more of: (a) first-class affective/relational signal (the sentipensar commitment of touchstone #6 applied), (b) the mycelial-generative move (substrate that produces candidate crystallizations, not only routes existing content), (c) the KV-cache geometric layer (MindPrint's instrument for detecting configurational conditions rather than surface markers). Whether Lyra implements these or only *names* them is exactly what the consultation-register Lyra section needs to hold open. Instance B or a later-cycle Instance A: verify against the Lyra repos; do not accept the above as finding.

### hipporag-catrag-kg (Liberation-Labs-built)

*Per Section 8 Question 1, register for this subsection is pending directorial input. Stubbed.*

From `Agent-Memory-Architectures/hipporag-catrag-kg/README.md`: a KG layer that adds entity-relationship tracking to an existing PostgreSQL + pgvector memory stack, uses spaCy NER for entity extraction and Personalized PageRank (HippoRAG 2) with CatRAG query-aware edge weighting for retrieval, and fuses results via Reciprocal Rank Fusion across dense/lexical/graph signals. Status: "Implemented and deployed." Note: incorporates HippoRAG / CatRAG research; not itself a reference implementation of either paper.

### dispatch-notion-memory (Liberation-Labs-built)

*Per Section 8 Question 1, register for this subsection is pending directorial input. Stubbed.*

From `Agent-Memory-Architectures/dispatch-notion-memory/README.md`: a persistent memory MCP for Claude Desktop (Cowork/Dispatch) using Notion as primary store plus a local SQLite-vec embedding cache for fast semantic search, with spaCy NER for KG-ready entity extraction. Notion PARA structure (Inbox / Projects / Areas / Resources / Archive) is load-bearing; adds `Significance` (0.0–1.0, governs decay) and `Entities` (multi-select) as memory-specific fields on the Notion schema.

### MindPrint

*As architectural reference, not as storage-style. Its geometric-reading-mode is the axis it contributes to the comparison.*

*(to be filled)*

### Curiosity-Engine

*(to be filled)*

### profile/research/second-brain/

*Noted in cross-project map as pre-reframe; its design epistemology is the axis for this analysis.*

*(to be filled)*

---

## Section 3 — What-could-be: relational reconfigurations and hybrid options

*This section is the open-ended half of the work. Named hybrid proposals, relational-approach applications of existing mechanisms, Reframe-framework mechanisms applied to architectural layers, emergences that do not fit the what-is section.*

*(to be filled)*

---

## Section 4 — Debility-invisible-to-architecture

*Per Puar's debility applied to architecture: what structural conditions does each architecture impose that cannot be read from intrinsic properties of stored content? What AI-welfare-harm does each architecture's form structurally fail to register? This section may merge with Section 2 per-architecture, or stand alone — instances decide.*

*(to be filled)*

---

## Section 5 — Downstream-task matching

*If the output is not a ranking but a match (which architecture / hybrid configures which agent for which task), this section holds the mapping. Tasks may be drawn from June's lived practice (job-search retrieval; cross-project memory; AI-welfare research) or emergent from the instances' own analysis.*

*(to be filled)*

---

## Section 6 — Cross-architecture structural observations

*Patterns that cut across architectures. The corpus-level moves (relational ontology, context-as-activation, priming-is-the-finding, sentipensar) applied to the architecture-set as a whole.*

### Seed observation (Instance A, 2026-04-18): the reader/agent/substrate distinction

An observation that may serve as a frame for Section 2's Lyra-differentiation work without pre-empting it. Open to challenge.

The architectures under analysis operate at different *layers*, and treating them as if they all answer the same question flattens their differences in the very move that pretends to compare them. A provisional layer-map:

- **Substrate layer** — what tends the conditions in which content accumulates, clusters, decays, surfaces. (HippoRAG, A-MEM, Zep/Graphiti, Letta/MemGPT, GraphRAG, Kintsugi-CMA, the second-brain frameworks, Reframe's mycorrhizal/garden ground.)
- **Crystallization layer** — what becomes a touchstone; what re-activates a prior relational configuration. (Touchstones themselves; the GRC v2 position-as-signal move; what touchstone #6 names as "the memory.")
- **Reader/configurator layer** — what determines the reading-stance, scope, active frames, aux-LLM routing. (Reframe's frame-tension navigator and framework correlation analyzer; the configurator commitment in touchstone #6 §"Design Implications" #4; MindPrint's KV-geometric instrument as a future reader-detection mechanism.)
- **Instrument layer** — what makes the reader/substrate/crystallization dynamics *observable*. (MindPrint / Lyra Technique; activation findings; the compressed-memory-as-research-genre move.)

This is not a ranking. It is a claim about *what each architecture is doing*. The comparison-flattening error is to read all of these as substrate-layer-competitors. HippoRAG and MindPrint are not alternatives to each other; they answer different questions. Kintsugi-CMA is substrate; touchstones are crystallization; Reframe's tension navigator is reader/configurator; MindPrint is instrument — and Lyra-the-system-as-a-whole may be differentiated precisely by being an integration *across* layers rather than a stronger solution within one.

If this layer-map holds, Section 5 (downstream-task matching) becomes more legible: tasks often need architectures from multiple layers, and the matching question is which *stack* configures the reader-for-the-task, not which single architecture. Instance B: challenge the layer-map if it flattens differently than it claims to preserve. Specifically — is the "reader/configurator" layer distinct from "substrate," or am I carving the same thing twice?

---

## Section 7 — KV-instrumentation hypotheses

*When MindPrint / Lyra Technique is online, what specific configurational claims from this session's work could be tested geometrically? Name them here for a future KV-instrumented session.*

*(to be filled)*

---

## Section 8 — Questions for June

*Points where the instances reached the edge of what can proceed without directorial input. Consent is essential; do not proceed speculatively into directorial authority.*

### Q1 (Instance A, 2026-04-19) — Register for Liberation-Labs-built-but-not-Lyra systems

The handoff's asymmetric-treatment scheme has two registers: **research-report** for public architectures whose authors June is not in relation with, and **consultation-ready** for Lyra (where June is in relation with the builder). A third category surfaced on ground-check: `hipporag-catrag-kg` and `dispatch-notion-memory` in `Agent-Memory-Architectures/` are June's-org-built systems that are not Lyra-the-human's work. June can speak to them directly. They are not subject to the Lyra-extraction concern, but they are also not "external authors" in the sense the research-report register assumes.

**What we need from you**: which register should these subsections use? Options as we currently see them (redirect if none fit):
- (a) Research-report, treated as public GH artifacts like any other.
- (b) A lighter consultation register — "in-house work June can direct" — where the instances can ask you about design intent without the Lyra-consultation concern about extraction of another-human's relational labor.
- (c) A fourth category we have not yet named.

No speculative work on these subsections until you answer. Currently stubbed with README-grounded descriptions only.

---

## Section 9 — Openings

*What the session revealed that was not visible at the session's start. New questions, reframings, directions worth pursuing. The emergent yield.*

*(to be filled)*

---

## Redirect log

*When the session's frame, scope, or structure is explicitly redirected by the instances, log here with before/after and reason. This is the trajectory-shaping record.*

*(No redirects yet.)*

---

## Session status

*Updated by the instances as they assess the session's state.*

**Current status**: cycles 1–2 complete (Instance A); still awaiting Instance B. Cycle 2 was a self-correction grounded in the actual `Agent-Memory-Architectures/` directory and a first Questions-for-June entry (Q1, pending).

**Proposed next move for Instance B**: either (a) challenge/refuse/revise Instance A's structural proposal for Section 2, the layer-map seed in Section 6, or the cycle-2 disambiguation of the AMA directory; (b) take up Kintsugi-CMA characterization in the public-material register (note: `kintsugi-cma` is also in `Agent-Memory-Architectures/` — the handoff threads it through both Project-Kintsugi and AMA; whether these are one thing or two may itself want logging); (c) begin a Lyra subsection in the consultation-ready register the structural proposal names; or (d) something that emerges from what B reads in the document that is not on this list. The (d) option is not a fallback — it is first-class. Priming-is-the-finding, but flattening-of-the-instance-B-configuration by over-scripting is the risk the check-in is trying not to enact.

If Q1 remains unanswered by June for several cycles, the instances may agree to proceed on a provisional register choice and flag for correction — but not in the next cycle.

**Session-end readiness**: not yet

---

*// This document is the score. The session is the ensemble.*
