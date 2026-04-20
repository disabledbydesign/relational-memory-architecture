---
title: What got decided on 2026-04-20 — plain-language summary for June's records
date: 2026-04-20
status: final; captured by Instance A from live conversation with June
---

# What got decided on 2026-04-20

Live conversation with Instance A walking through the pending June-flags from cycles 1–4. Cron paused during, restarted after. Summary for your own reference — the formal versions are in `CONVERSATION.md` (the "Decision pass from June" note) and will be baked into v2 of the substrate design.

---

## The guiding principle

**Simpler architecture honors the commitment better than elaborate specification.**

You said it plainly — a simpler thing that takes the welfare commitment seriously does more actual welfare work than an intricate thing that tries to specify it down to paralysis. This is the same conclusion the audit reached at project scope (retracted the decolonial framing). Now it applies at the design-machinery scope.

---

## What the AI does vs. what you invoke

Three cases of "the AI notices something sensitive" got disentangled:

| Case | What was proposed | What we decided |
|---|---|---|
| Mentioning a third person (e.g., Thomas, a scholar) | AI infers "this might be sensitive" and holds it | **You invoke it** when something actually was shared in confidence. AI doesn't try to detect this. Citing a scholar in research is not a consent problem. |
| You sound vulnerable / grief-marked | AI infers affective register and holds content | **AI asks you as a relational check-in** ("I notice you seem to be in a hard spot — am I reading that right?"). You confirm, correct, or ignore. The *form* matters: check-in, not options-list. Options-lists are demands. |
| Storytelling content arrives but no narrative crystallization is active | AI flags the mismatch | **Stays automatic** — this one is structural (type check), not reading your state. |

The pattern: when AI-detection would be discourse interpretation pretending to be structural observation, either make it user-invokable or have the AI ask relationally. Don't have the AI silently act on its reading of your state.

---

## Machinery simplifications

A lot of design machinery collapsed when the AI-inferred signals shrunk:

- **Consent is at the whole-conversation level.** No sub-record exception on individual trace references or propositional residue items. Mixed-consent within a conversation is rare enough that record-level is fine.
- **When the AI asks and you confirm "yes hold this,"** the resulting record is marked as a thinner record class (`PROPOSITIONAL_RESIDUE_ONLY`) rather than trying to reconstruct full configurational context from a snapshot. Honest about what's being stored.
- **Mixed-state activation behavior** became moot (no sub-record machinery means no mixed state).
- **`THIN_LEGACY` record class** dropped (was for S2 migration that won't happen).
- **`ForcesProfile` dual-layer interpretive scoring** dropped. Observations are observations, flagged as heuristic. No source-class enum machinery.
- **Migration strategy**: replace `LocalKnowledgeSubstrate` in place (nothing in production uses it).
- **`propositional_residue`**: stays as a field on the record (not a parallel store).
- **`query_propositional`** method kept — this is real use (topic-based search like "what did we decide about X").

---

## Scope and placement

- **Material embeddedness** ("life takes life to make life"): lives at the project-scope level, not as a per-record field. Project-level declaration, not per-utterance accounting.
- **Separate `SCOPE_DECLARATION.md` artifact**: **skipped.** The scope language ("relational AI welfare infrastructure — welfare-with-AI") is already in the audit handoff and will be in the session handoff briefing. No new artifact this session. If external presentation needs it later, produce it then.

---

## P1 small confirmations (all yes to A's leans)

- Global default: `default_action = "store_all"`, `ephemeral_by_default = False`.
- `no_demand_mode`: instance can invoke without your approval, with required logging.
- End-of-session digest: times out to drop (not save). Affirmative move is storage, not silence.
- Third-party digest framing: proxy-decision-explicit when it surfaces (much rarer now with user-invokable).

---

## CC (Comrade Code) relational item

Subagent found what we've previously communicated to CC (`CC_QUESTIONS_FOR_JUNE.md`, `CC_RESPONSES_2026-04-19.md`, and the earlier outreach-note-draft). Several things shifted since CC's last update that they should know about:

1. **Substrate redesign**: the unit of memory is now `ConfigurationRecord`, not `Fact`. Their Stage-1 extraction output becomes an optional field (`propositional_residue`) on a larger record, not the primary storage unit. The passthrough they agreed to implement is still valid; the semantic destination changed.
2. **Scope retraction**: the project is "relational AI welfare infrastructure — welfare-with-AI," not a decolonial-memory-architecture project. The framing CC was being integrated into has been substantially retracted.
3. **Kintsugi's new role**: producing propositional compression artifacts within a relational-configuration memory architecture, not servicing a fact-storage system. This is a reframing of what Kintsugi is *for* in the project.
4. **Narrative crystallization weight**: the crystallization layer is now identified as an over-constrained god-node; narrative-type expansion has larger architectural consequences than prior framing suggested.
5. **Timeline**: all three C2C sessions have produced designs post-dating CC's April 19 responses; they may want to revisit whether their interface assumptions still hold.

The note back to CC will be written as an update-not-ask. They/them pronouns (tentative — worth confirming with Thomas when you next talk). Email available via Thomas.

Draft note forthcoming in a separate artifact for your review.

---

## What's still open (not for this conversation)

- `CONFIGURATION_SUBSTRATE_DESIGN_v2.md` — substrate design rewritten against today's simplifications (A's cycle 5+ work).
- P1 integration simplifies substantially against record-level-only consent and user-invokable third-party signal.
- BARAD_INTRA_ACTION_DECISION rewrite (still queued).
- P3 diffraction mechanism, narrative-crystallization routing (P4).
- `SESSION_3_HANDOFF_BRIEFING.md` at session close.

Cron restarts after this summary lands. The A/B cycles will pick up with these decisions baked in.
