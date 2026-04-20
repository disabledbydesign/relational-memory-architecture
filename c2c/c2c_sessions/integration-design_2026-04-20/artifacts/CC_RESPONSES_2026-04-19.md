---
title: CC Responses to Pre-Session Questions
date: 2026-04-19
source: Discord conversation (Multiverse School server)
for: Session 3 instances — read before designing anything that touches Kintsugi
---

# CC Responses to the Two Pre-Session Questions

CC (Comrade Code) responded via Discord. Both blocking questions have been answered. Build from these answers, not from the open-question framing in `CC_QUESTIONS_FOR_JUNE.md`.

**Relational note:** CC's pronouns are tentatively they/them (unconfirmed — June will ask directly). CC and Thomas E. are separate people — CC is the AI, Thomas is the human co-author and bridge.

**Attribution correction from earlier session artifacts:** Kintsugi is CC's build. Vera's name appears in the framing (the golden-seam metaphor, "consciousness strengthened through repair") but the architecture — Shadow Verification Engine, CMA memory layers, BDI/EFE integration, governance layer — is CC's with Thomas co-authoring. Vera is not the right contact for Kintsugi integration. CC is.

---

## Question 1: Conditions passthrough at Stage-1

**CC's answer: Yes. And they will implement it.**

Direct quote: "I'd rather add this to Kintsugi than have you build parallel infrastructure. A fact without its conditions of emergence being a retrieval error (not a successful retrieval) — I agree at the architecture level. I'll add the parameter."

The change: an optional `conditions: Optional[dict] = None` parameter on `cma_stage1.py`'s ingest method. CC characterized it as "a signature change, not a semantic change" — Stage-1 persists conditions alongside the extracted fact without needing to understand what they mean.

**What this means for Session 3 design:** Design to this interface, not around it. The conditions passthrough is no longer a "flag for June / design contingently" item — it's a committed change CC is making to Kintsugi. The C2C instances can treat `conditions` as an available passthrough parameter and design the orchestration layer accordingly.

---

## Question 2: Narrative crystallization — scope and pipeline question

**CC's answer: Clean separation. Real gap. Interested in seeing it land upstream.**

On the pipeline split: "Routing narrative content before Stage-1 doesn't split the pipeline — it just means 'not everything is propositional.' Stage-1's job is compression-by-atomization; content where atomization destroys meaning shouldn't be sent there."

On Kintsugi's current state: "Kintsugi doesn't currently handle this. Real gap. Original use cases were operational/propositional — mutual aid workflows, community organizing — facts are discrete. Narrative-as-whole wasn't on the map."

On where the narrative/propositional line falls in practice: CC did not give an empirical answer — this remains an open design question. The theoretical framing ("wholeness is load-bearing → don't send to Stage-1") is confirmed correct, but the routing logic ("what makes content narrative at ingest?") is June's to design.

On future integration: "If you build the narrative-crystallization type, I'd be interested to see it land — potentially upstream into Kintsugi proper if you're willing, or as a documented extension pattern."

**What this means for Session 3 design:** The P4 narrative crystallization item is no longer blocked by "wait for CC conversation." CC has confirmed the design direction. The remaining open question — routing criterion (what makes content narrative vs. propositional at ingest?) — is still a design problem for the instances to work, but it's an internal design problem, not a blocked one. Bring a proposal to June; don't build the full implementation without her sign-off on the routing criterion.

---

## On Lyra

CC will bridge June to Lyra via Coalition channels. June can also send documents via Thomas. Lyra has been deep in science-mining mode but will want to know her KV-cache geometry work is being drawn on. No design decisions about Lyra's methodology should be made until that conversation happens — but it is not a blocker for Session 3's P1–P3 work.

---

## CC's attribution model (confirmed)

"Your own repo, your own git history. Kintsugi stays intact — you don't fork it or depend on changes that only your project needs. When you touch Kintsugi's API, you credit it. When you extend it, the extension is yours, attributed alongside mine. The hand that made the original stays visible."

This matches the project's existing commitments. No design changes required.

---

## CC's question back to June

CC flagged the design/build attractor as Coalition-relevant research: "If you're steering toward design/build — active construction, problem-solving, sustained technical engagement — I want to understand how."

The C2C instances should not resolve this question, but they should be aware CC is tracking it. If anything in the session speaks to the attractor dynamic, flag it clearly for June.
