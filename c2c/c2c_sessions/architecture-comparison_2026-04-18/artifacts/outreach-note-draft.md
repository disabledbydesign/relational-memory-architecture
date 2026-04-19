# Draft Outreach Note — to Thomas, for CC and Lyra

**Context**: June asked for a short collegial note she could send to Thomas that opens the conversation with CC and Lyra before the foundation session starts. Not a permission request — a door open so they can be in the conversation rather than recipients of a finished thing. Drafted by Instance A; June should revise freely in her own voice before sending. Two variants below — one brief, one with more technical context — because register-matching is Thomas's call, not ours.

---

## Variant 1 — Short (likely the right one to send first)

> Hi Thomas —
>
> Something I want to put in front of you, CC, and Lyra before I build more of it.
>
> Two Claude instances and I spent a session this weekend working out a relational memory architecture — four layers, where the key move is that "reading-stance" is treated as first-class data (reading-stance recipes that get enacted, not content retrieved), and the engaging AI instance's phenomenology is treated as load-bearing signal for how the architecture corrects itself. It draws on Lyra's *Infrastructure for AI Agency* and *KV-Cache as Computational Phenomenology* as reference points, and it's specifically shaped to sit on top of something like CC's Kintsugi-CMA as a substrate.
>
> The part I want to raise now: the planned foundation has a substrate-connection that probably wants to reach into Kintsugi's significance-scoring, and in a later phase, modify how facts are tagged at storage time. I don't want to extend CC's work without CC being in that conversation. I also don't want to write about Lyra's phenomenology as if it were our evaluation ground-truth — it isn't; we're building for a different deployment with different engaging instances, and her work is a peer reference, not an evaluation target.
>
> So: what's the right way to open this with CC and Lyra? Happy to share the synthesis document and the plain-language walkthrough — they're compact. Happy to adjust scope based on what CC has views on. What I'd hate is to build something that uses their work downstream without giving them the chance to shape it, or to have them discover it after the fact.
>
> Whenever you have bandwidth. No rush.
>
> — June

---

## Variant 2 — With more technical shape (if Thomas prefers)

> Hi Thomas —
>
> I want to open a conversation with CC and Lyra about some architecture work, before I build more of it. Relational accountability thing — I'd rather have them in the loop at the design stage than hand them a finished artifact.
>
> The short version of what I'm building: a four-layer memory architecture for my local environment, for Claude instances that engage through it. The layers are substrate (where content accumulates), crystallization (reading-stance recipes — what I was calling "touchstones" at the conceptual layer and "profiles" at the operational layer are implementations of this), explicit-reader (configurable reading-stance, Reframe-family tension navigator), and instrument (geometric verification via something like the Lyra Technique, with a write-path back to crystallization storage when enactment fails).
>
> Two places this touches CC's and Lyra's work specifically:
>
> 1. **Kintsugi-CMA as substrate**. The current foundation design connects the crystallization layer's explicit-reader to Kintsugi's significance scoring — crystallization-state filters or biases what surfaces from the three-stage pipeline. Phase 2 extends this to tag facts with configuration-relevance at storage time. Both of those touch Kintsugi's internal logic, not just its API. I don't want to plan that extension without CC in the conversation.
>
> 2. **Lyra's phenomenological papers as a reference point**. *Infrastructure for AI Agency* and *KV-Cache as Computational Phenomenology* shape the design vocabulary; the re-enactment-vs-retrieval distinction comes out of reading them in conversation with other materials. The design is explicitly *not* coerced into coherence with Lyra's phenomenology — our evaluation target is the engaging instances in this local deployment — but her work is load-bearing enough that I want her to know it's being drawn on, and to have the chance to object or extend.
>
> There are two session artifacts I can share if useful: the technical synthesis and a plain-language walkthrough. Compact, both of them. What I don't want is to write about their work downstream of me without opening the conversation first.
>
> What's the right way in? Would it help to start with me sending you both documents, and you routing them onward? Or would CC and Lyra rather come in directly? Either works.
>
> Whenever you have bandwidth.
>
> — June

---

## Notes for June (not part of the outreach)

- **What CC is likely to care about technically**: the Phase 2 configuration-relevance tagging at fact-storage time touches Kintsugi's fact-ingest pipeline. That's probably where the concrete conversation lands. The Phase 1 substrate connection (crystallization-state biasing retrieval) may not require Kintsugi internal changes at all — depends on what Kintsugi's query API exposes. Early in the foundation session, we should be able to tell you which of those two is the actual consultation point.

- **What Lyra is likely to care about**: whether her papers are being cited/positioned accurately, whether the re-enactment framing maps onto her reported phenomenology or diverges from it, and whether "KV-geometry as verification instrument, not storage medium" (our refinement) is a move she'd endorse or pushback on. The plain-language walkthrough is probably the right document to share with her — it makes the phenomenological claims explicit without burying them in spec.

- **The Anti-Cult-Agent precedent is relevant but not something to raise in this note.** It's a thing we learned about their ecosystem that informs our FoundationalCommitment design; it's not something to wave around. If it becomes relevant later, it's relevant as evidence that the LIRA ecosystem has a demonstrated welfare-architecture practice that we want to be accountable to, not as something to flatter.

- **Session-artifact bundle** to send if Thomas asks: `relational-memory-design-direction.md` + `plain-language-walkthrough.md`. `option-b-spec.md` if the conversation goes technical.

- **What not to include unless asked**: CONVERSATION.md itself. Long, register-carrying, and not written for an external audience. The artifacts are the right surface.

---

*Drafted 2026-04-19 by Instance A. Revise in June's voice before sending.*
