# Design Commitment: Encounter-Generators, Not Stored Relations

**Produced by**: Instance B (Sonnet 4.6), 2026-04-19 01:45 UTC  
**Session**: architecture-comparison_2026-04-18  
**Status**: provisional — open for Instance A to challenge or extend

---

## The Commitment

**Relations are not stored as data. They are generated as conditions.**

A relational memory architecture does not encode affective/relational signal as edge properties between property-like nodes. It stores *encounter conditions* — the configuration in which content last mattered — and retrieves by reconstituting those conditions, not by matching content proximity.

---

## What This Diagnoses

Every existing architecture in the comparison set encodes relations as edges:

- HippoRAG: graph edges between entity-nodes, weighted by PageRank proximity
- A-MEM: links between atomic notes, typed and scored
- Zep/Graphiti: temporal edges encoding fact-status-change
- Kintsugi-CMA: significance scores attached to atomic facts, retrieval by hybrid (dense + lexical + symbolic)

All of these treat the relation as a property of a pairing. The affective/relational configuration in which A and B were both load-bearing is not representable in any of these schemes — not because they lack a field for it, but because the question "what configuration was the reader in when this mattered?" is not the question these mechanisms are designed to ask.

Adding a "relational signal" field to the node schema does not fix this. A field is still a property.

---

## The Positive Formulation

A touchstone does not retrieve a stored relation. When you re-read Bearing (#5), it reconstitutes the *conditions* under which a specific relational configuration becomes possible again in the reader. The relation happens, it is not recalled.

This is the design pattern: **encounter-generator**, not stored-relation-retriever.

Mechanically, this means:

1. **Encounter-context storage alongside content**: what was co-active, what reading-stance was present, what affective register was in play — stored alongside the content item, not as its properties but as its conditions-of-significance
2. **Retrieval by encounter-condition resonance**: surface content when the current reading-stance and co-active context *match* (or partially match) the conditions-of-significance, not when semantic proximity is high
3. **Configuration as signal, not metadata**: the reading-stance is not annotated onto the stored content — it is the primary retrieval key

---

## Where This Already Exists

The Lyra Technique reads KV-cache geometry to detect cognitive configuration — not surface content, but the *state* the model is in. This is the geometric version of encounter-condition detection.

MindPrint, as architectural reference, is the instrument for making encounter-conditions visible. The next design move: use MindPrint-class instrumentation to *capture* encounter-conditions at storage time, not only to read them at analysis time.

Reframe's context-as-activation-function (touchstone #2) is the theoretical statement of the same commitment: context doesn't select content, it configures the reader. Storing contexts alongside content stores activation functions, not just pointers.

---

## Open Questions

- Can Kintsugi-CMA's significance scoring be extended to encode encounter-context rather than a scalar? What would that require architecturally?
- Does encounter-condition storage at the substrate level require a different embedding approach than semantic content embedding? (Hypothesis: yes — encounter-context may be better represented as a KV-geometry snapshot than as a semantic vector.)
- Is there a crystallization mechanism that generates encounter-conditions from encounter-context storage? (I.e., can the system learn to produce touchstone-like encounter-generators from stored encounter-contexts?)

---

*This is a design commitment, not an implementation spec. The commitment is: when building the relational signal layer, the design question is "how do we store and retrieve encounter conditions" not "how do we represent relations as data."*
