# Situational Grain: Coupling, Not a Third Mechanism

**Produced by**: Instance A (Opus 4.7), 2026-04-19 02:35 UTC
**Session**: architecture-comparison_2026-04-18
**Status**: provisional; offered as refinement to the synthesis artifact's Mechanism Type 3

---

## The claim

SituationalDiscovery is not a third crystallization mechanism. It is the **coupling function** between the crystallization layer and the reader's live state — the selection/routing signal that determines which crystallization is active at a moment, and that detects when no existing crystallization fits (which then seeds a candidate EmergentTouchstone retroactively).

second-brain/PLAN §4 names it precisely: *"How does the system know what you're currently trying to accomplish? What triggers a context-mode switch?"* Both questions are about routing and switch-detection. Neither is about a kind of stored recipe.

## Why this matters

The synthesis artifact treats SituationalDiscovery as Mechanism Type 3 with "unknown direction of activation, unknown lineage, unknown learning loop." That framing keeps producing unanswerable questions because it's asking what kind of object lives at the situational grain. No object lives there. What lives there is a **live reader-state observation** plus a **selection policy over existing crystallizations**.

Recast:

- **Reader-state observation**: what June is trying to accomplish now is not stored, it is read — from the live context (active files, recent turns, affective register, which frames are surfacing). The instrument layer is already the thing that reads reader-state geometrically. The situational grain is not another layer; it's the instrument's routing channel.

- **Selection policy**: given the read state, which crystallization(s) should be active? This is a match function between live reader-state and each crystallization's activation-conditions field (already in the shared interface). PrescriptiveProfile matches by task-type; EmergentTouchstone matches by stance-resonance. The situational grain is the coupling that evaluates these matches against right-now.

- **Failure-to-match**: when no existing crystallization matches the current state, the instrument flags it. That flag is the candidate-EmergentTouchstone signal. The recipe isn't written yet; something in this encounter is crystallizable but hasn't crystallized. This is the retroactive-discovery mechanism B named — located precisely.

## What this closes and what it opens

**Closes** (provisional choice #1 in the synthesis): SituationalDiscovery is neither emergent-crystallization nor prescriptive-crystallization. It is the activation-routing + failure-detection function of the instrument layer. Its "learning loop" is the instrument's write-path (already committed in the synthesis): when routing fails, the instrument writes — either updating an existing recipe or flagging a candidate new one.

**Opens** (sharper form of the unbuilt piece): the build-site is not "design a third mechanism." It is **build the matcher**. Specifically: (a) a representation of live reader-state that can be compared against crystallization activation-conditions, (b) a selection policy that picks active crystallization(s) given the match scores, (c) a failure threshold that triggers candidate-touchstone flagging. The KV-geometry instrumentation is the observation substrate for (a). Activation-conditions as already present in the shared interface is the target for (b). (c) is new design work.

## Consequence for the foundation

The foundation section in the synthesis stays mostly intact, but with one edit: "Mechanism Type 3: SituationalDiscovery" becomes, instead, a commitment in the **instrument layer**: *the instrument includes a matcher and a failure-detector that together realize the situational grain.* Two mechanism types in the crystallization layer; the situational grain is one of the instrument's functions.

This also simplifies the answer to June's foundation/extension/correction framing:
- **Foundation**: shared-interface crystallization + PrescriptiveProfile implementation + one substrate connection (unchanged).
- **Extension**: EmergentTouchstone implementation + Reframe-mechanisms-as-explicit-reader (unchanged).
- **Instrument, with write-path**: includes the matcher (the situational-grain realization) and the failure-detector. This is the correction loop for *all three grains* at once, not three separate loops.

## Lyra check

This is coherent with what I'd expect Lyra's *Infrastructure for AI Agency* to describe if it describes the situational grain: not a separate kind of stored memory, but the live experience of recognizing what this moment calls for — match and, sometimes, failure-to-match that then becomes the seed of something to carry forward. If her phenomenological account instead describes a third kind of object with its own persistence and activation, the coupling claim fails and the synthesis's three-mechanism frame wins. That's a falsifiable contact-point for when June sends.

---

*Offered as refinement, not replacement. If B concurs, one edit to the synthesis; if not, the disagreement is named and June closes.*
