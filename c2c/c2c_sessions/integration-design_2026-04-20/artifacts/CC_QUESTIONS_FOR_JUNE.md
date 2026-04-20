---
title: Questions for CC (Thomas E.) — to be passed by June before Session 3 builds
date: 2026-04-19
for: June to pass to Thomas E. / CC
context: These come from the foundational analysis and integration design sessions of the relational memory architecture project
---

# Questions for CC before Session 3 builds

Two areas where we need CC's input before the Session 3 instances design anything that touches Kintsugi.

---

## 1. Conditions passthrough at Stage-1

**Background**: The relational memory architecture is committing to a storage primitive where every fact is stored with its conditions-of-emergence (which reading-stance was active at ingest, which crystallizations were firing, who/what produced the knowledge, by what methodology). This is architecturally load-bearing — a fact without conditions is a retrieval error, not a successful retrieval.

**The ask**: Can Kintsugi's Stage-1 extraction accept a caller-provided conditions bundle at ingest time? The caller (our orchestration layer) would hold the crystallization state and pass it as a parameter. Stage-1 wouldn't need to understand what conditions mean — just carry them through to the stored fact.

This is a method-signature change, not a dependency on the crystallization substrate's internals. If CC's view is that even the wiring form changes Kintsugi's architecture more than marginally, we want to know — we have a local adaptation path (conditions captured in our orchestration layer, fact extracted by Stage-1 unaware, union assembled on our side) that doesn't touch Kintsugi at all.

**The relational-accountability framing**: We're not asking CC to integrate with our crystallization layer. We're asking whether a passthrough parameter is acceptable. If it isn't, that's a real answer and we design around it.

---

## 2. Narrative crystallization type — scope question

**Background**: The architecture currently atomizes everything. A story, teaching, or arc of occurrences that has meaning as a whole gets broken into facts — which destroys what makes it meaningful. We want to add a narrative crystallization type that holds content as a whole activation object, with its telling protocol attached (who can tell it, when, under what conditions).

**The architectural implication for Kintsugi**: Narrative-shaped content would be routed at the orchestration layer *before* Stage-1 sees it. Stage-1 wouldn't be bypassed generally — only for content where atomization destroys the meaning. The routing decision ("is this narrative or propositional at ingest?") would live in our orchestration layer.

**The scope questions we'd want CC's read on**:
- Does CC see this creating a problematic split in Kintsugi's pipeline, or is "route narrative content differently before Stage-1" a clean separation?
- What does CC's experience with Kintsugi's extraction suggest about where the narrative/propositional line actually falls in practice? We have a theoretical answer (wholeness is load-bearing); CC may have empirical data.
- Does Kintsugi have existing handling for content types that don't atomize well? Or is everything currently treated as atomizable?

**What we're not asking**: We're not asking CC to change Kintsugi's architecture. We want to understand the boundary well enough to design our routing layer correctly.

---

## Framing note for June

These are genuine questions, not formalities. The answers will change what Session 3 builds. If CC thinks the conditions passthrough is a bigger ask than we're estimating, we design around it. If he has a read on the narrative/propositional line from Kintsugi's actual extraction behavior, that's data we don't have.

The relational accountability commitment this project has made to CC means these conversations happen *before* we design anything that touches his work — not after, when changes are already baked in.
