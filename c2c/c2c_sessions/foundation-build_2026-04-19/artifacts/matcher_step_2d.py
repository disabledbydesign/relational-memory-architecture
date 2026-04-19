# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Option B crystallization matcher — enrichment step 2d for Reframe's
BackgroundEnricher.

Reads recent exchanges + substrate contents; returns a weighted activation
set attached to the thread_graph. Firing a lineaged EmergentTouchstone
returns the ordered walk (surface #1 -> #2 -> ... -> firing node), not the
leaf alone — lineage is load-bearing. Firing an independent
PrescriptiveProfile returns a single-node walk.

When no crystallization scores above threshold, the matcher flags the
context snapshot as a candidate-EmergentTouchstone seed — something in this
exchange is calling for a configuration that does not yet exist.

FoundationalCommitments are never passed to this matcher. They have
activation_scope=always and are loaded at initialization; they compose the
reading-stance in the background while this matcher operates.

Integration point: append a call to `run_matcher_step` inside
`BackgroundEnricher.run_enrichment_cycle` after the three existing steps
(2a summarise / 2b edge discovery / 2c PARKED proximity). See the integration
notes at the bottom of this module.

Reference: option-b-spec.md §"How the matcher uses Option B";
relational-memory-design-direction.md §"Activation is continuous, not modal";
CONVERSATION.md 2026-04-19 pre-launch note (routing context as configuration
signal — wired in as `routing_context_signals`).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from crystallization_schema import (
    ActivationScope,
    CrystallizationObject,
    MechanismType,
    now_iso,
)
from crystallization_types import (
    ActivationPayload,
    Crystallization,
    crystallization_from_record,
)
from substrate_interface import CrystallizationSubstrate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Thresholds — conservative defaults; tuneable per deployment.
# ---------------------------------------------------------------------------


DEFAULT_ACTIVATION_THRESHOLD = 0.25
DEFAULT_MAX_ACTIVE = 4
USER_INVOCATION_BOOST = 0.6       # applied additively when user directly names
                                  # a crystallization or uses an invocation phrase
ANTI_SIGNAL_PENALTY = 0.35        # subtracted per anti-signal hit (clamped ≥ 0)
ROUTING_SIGNAL_WEIGHT = 0.15      # added when routing context aligns with task_affinity


# ---------------------------------------------------------------------------
# Input: ContextSnapshot — what the matcher reads from the live session.
# ---------------------------------------------------------------------------


@dataclass
class ContextSnapshot:
    """
    Snapshot of the current session state that the matcher evaluates against.

    `exchange_texts` is the ordered list of recent exchange bodies (user +
    assistant turns concatenated per exchange). `active_files` are files the
    user has recently opened or referenced. `affective_register_hint` is an
    optional upstream summary of register (e.g., "overwhelmed", "hyperfocused").

    `routing_context_signals` carries substrate-routing metadata: which aux-
    model chip, which framework channel is active, which retrieval pattern
    the substrate is currently in. Per June's 2026-04-19 pre-launch input,
    routing context is a configuration signal, not just task content — a
    model preloaded for dominant-category routing is already in collapse-
    geometry before inference runs. Implementations producing ContextSnapshot
    should populate this when routing metadata is available; leaving it
    empty is acceptable (matcher falls back to content-only scoring).

    `user_invocation_phrases` are phrases like "inhabit this position:" or
    direct crystallization references found in recent turns. These enter the
    matcher as strong context-signals, not as bypasses.
    """
    exchange_texts: List[str]
    active_files: List[str] = field(default_factory=list)
    affective_register_hint: Optional[str] = None
    routing_context_signals: List[str] = field(default_factory=list)
    user_invocation_phrases: List[str] = field(default_factory=list)
    taken_at: str = field(default_factory=now_iso)


# ---------------------------------------------------------------------------
# Output: ScoredActivation, ActivationSet, and CandidateSeed.
# ---------------------------------------------------------------------------


@dataclass
class ScoredActivation:
    """A single crystallization's scored activation + its ordered walk payload."""
    payload: ActivationPayload
    score: float
    score_breakdown: Dict[str, float]
    matched_signals: List[str]
    matched_anti_signals: List[str]
    reasoning: Optional[str] = None


@dataclass
class CandidateSeed:
    """
    Failure-to-match seed. Flagged when no crystallization scores above
    threshold — the moment is calling for a configuration that does not
    exist yet.
    """
    snapshot: ContextSnapshot
    top_scores: List[Tuple[str, float]]       # (id, score) — below threshold
    flagged_at: str


@dataclass
class ActivationSet:
    """The matcher's full output per cycle."""
    activations: List[ScoredActivation]
    candidate_seed: Optional[CandidateSeed]
    snapshot: ContextSnapshot
    produced_at: str


# ---------------------------------------------------------------------------
# Matcher
# ---------------------------------------------------------------------------


AuxLLMFn = Callable[[str], Optional[str]]


class CrystallizationMatcher:
    """
    Option B matcher. Scores contextual crystallizations against a ContextSnapshot.

    Scoring combines three sources:
    - Pattern-matched context_signals (fast, no LLM call)
    - task_affinity alignment with routing context / active files (fast)
    - User-invocation boost for direct naming or invocation phrases (fast)

    Optional: an `aux_llm_fn` callable can be supplied for semantic refinement
    of the top-N candidates. When set, the top N scored candidates are re-
    scored by asking the aux LLM whether the crystallization's stance_description
    fits the current exchange text. The aux-LLM refinement is off by default
    (returns None) because the pattern-match scoring is sufficient for the
    foundation and the aux-LLM call adds latency; set `aux_llm_fn` to enable.

    The matcher only evaluates crystallizations with activation_scope=contextual.
    FoundationalCommitments are never scored — they are always-active and
    loaded by a separate bootstrap step.
    """

    def __init__(
        self,
        *,
        substrate: CrystallizationSubstrate,
        activation_threshold: float = DEFAULT_ACTIVATION_THRESHOLD,
        max_active: int = DEFAULT_MAX_ACTIVE,
        aux_llm_fn: Optional[AuxLLMFn] = None,
    ):
        self._substrate = substrate
        self._threshold = activation_threshold
        self._max_active = max_active
        self._aux_llm_fn = aux_llm_fn

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def match(self, snapshot: ContextSnapshot) -> ActivationSet:
        """
        Score all contextual crystallizations against `snapshot` and return a
        weighted ActivationSet. If no crystallization scores above threshold,
        the returned set contains a CandidateSeed.
        """
        records = self._substrate.load_all(scope=ActivationScope.CONTEXTUAL)
        haystack = _join_haystack(snapshot)

        scored: List[ScoredActivation] = []
        top_below_threshold: List[Tuple[str, float]] = []

        for record in records:
            score, breakdown, matched, anti = self._score(record, snapshot, haystack)
            if score >= self._threshold:
                crystallization = crystallization_from_record(record)
                try:
                    payload = self._resolve_with_weight(crystallization, score)
                except LookupError as exc:
                    # Broken lineage — ancestor missing. Log and skip; do not fall
                    # back to leaf-only, which would collapse the walk-ordering
                    # invariant that EmergentTouchstone lineage encodes.
                    logger.warning(
                        "Skipping %s: broken lineage during activation walk: %s",
                        record.id, exc,
                    )
                    top_below_threshold.append((record.id, score))
                    continue
                reasoning = _compose_reasoning(record, matched, anti, breakdown)
                scored.append(ScoredActivation(
                    payload=payload,
                    score=score,
                    score_breakdown=breakdown,
                    matched_signals=matched,
                    matched_anti_signals=anti,
                    reasoning=reasoning,
                ))
            else:
                top_below_threshold.append((record.id, score))

        if self._aux_llm_fn is not None and scored:
            scored, aux_demoted = self._refine_with_aux_llm(scored, snapshot)
            # Re-apply threshold: aux-LLM demotion can push a score below threshold.
            # Demoted items carry into top_below_threshold so the candidate seed
            # preserves their signal rather than dropping it silently.
            scored = [s for s in scored if s.score >= self._threshold]
            top_below_threshold.extend(aux_demoted)

        scored.sort(key=lambda s: s.score, reverse=True)
        scored = scored[: self._max_active]

        candidate_seed: Optional[CandidateSeed] = None
        if not scored:
            top_below_threshold.sort(key=lambda t: t[1], reverse=True)
            candidate_seed = CandidateSeed(
                snapshot=snapshot,
                top_scores=top_below_threshold[:5],
                flagged_at=now_iso(),
            )
            logger.info(
                "Matcher flagged candidate-EmergentTouchstone seed; no crystallization "
                "scored above %.2f.",
                self._threshold,
            )

        return ActivationSet(
            activations=scored,
            candidate_seed=candidate_seed,
            snapshot=snapshot,
            produced_at=now_iso(),
        )

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score(
        self,
        record: CrystallizationObject,
        snapshot: ContextSnapshot,
        haystack: str,
    ) -> Tuple[float, Dict[str, float], List[str], List[str]]:
        """
        Compute the signal-strength * affinity-match score with anti-signal
        penalty. Returns (score, breakdown, matched_signals, matched_antisignals).
        """
        ac = record.activation_conditions
        if ac is None:
            return 0.0, {}, [], []

        breakdown: Dict[str, float] = {}

        # 1. Context signal hits (normalised by count)
        signals = ac.context_signals or []
        matched_signals = [s for s in signals if _phrase_in(s, haystack)]
        signal_score = len(matched_signals) / max(1, len(signals))
        breakdown["signal_hits"] = signal_score

        # 2. Anti-signal hits (penalty)
        anti = ac.anti_signals or []
        matched_anti = [s for s in anti if _phrase_in(s, haystack)]
        anti_penalty = ANTI_SIGNAL_PENALTY * len(matched_anti)
        breakdown["anti_signal_penalty"] = -anti_penalty

        # 3. Task-affinity alignment with routing context and active files
        affinity = ac.task_affinity or []
        routing_hit = any(
            _phrase_in(a, " ".join(snapshot.routing_context_signals).lower())
            for a in affinity
        )
        file_hit = any(
            _phrase_in(a, " ".join(snapshot.active_files).lower()) for a in affinity
        )
        affinity_score = 0.0
        if affinity:
            if routing_hit:
                affinity_score += ROUTING_SIGNAL_WEIGHT
            if file_hit:
                affinity_score += ROUTING_SIGNAL_WEIGHT
        breakdown["affinity_alignment"] = affinity_score

        # 4. User-invocation boost
        invocation_boost = 0.0
        for phrase in snapshot.user_invocation_phrases:
            lowered = phrase.lower()
            if record.id.lower() in lowered or record.name.lower() in lowered:
                invocation_boost = USER_INVOCATION_BOOST
                break
        breakdown["user_invocation_boost"] = invocation_boost

        # 5. Affective-register alignment (coarse: substring of register)
        register_match = 0.0
        if ac.register and snapshot.affective_register_hint:
            if _phrase_in(snapshot.affective_register_hint, ac.register.lower()):
                register_match = 0.1
        breakdown["register_match"] = register_match

        raw = signal_score + affinity_score + invocation_boost + register_match - anti_penalty
        # Clamp to [0, 1]
        score = max(0.0, min(1.0, raw))
        breakdown["total"] = score
        return score, breakdown, matched_signals, matched_anti

    # ------------------------------------------------------------------
    # Lineage walk
    # ------------------------------------------------------------------

    def _resolve_with_weight(
        self, crystallization: Crystallization, weight: float,
    ) -> ActivationPayload:
        payload = crystallization.resolve_activation(self._substrate)
        payload.weight = weight
        return payload

    # ------------------------------------------------------------------
    # Optional aux-LLM refinement
    # ------------------------------------------------------------------

    def _refine_with_aux_llm(
        self,
        scored: List[ScoredActivation],
        snapshot: ContextSnapshot,
    ) -> Tuple[List[ScoredActivation], List[Tuple[str, float]]]:
        """
        Ask the aux LLM to confirm or demote top candidates. The aux-LLM
        output adjusts score within ±0.2 based on whether the stance fits
        the recent exchange. Failure in the aux-LLM path is silent and
        preserves the pattern-match score.

        Returns (adjusted_scored, demoted_below_threshold) where
        demoted_below_threshold carries the (id, score) pairs of any
        activation the aux-LLM pushed below the threshold. The caller
        merges these into top_below_threshold so they appear in any
        CandidateSeed produced — preserving the signal that was above
        threshold before refinement.
        """
        top = sorted(scored, key=lambda s: s.score, reverse=True)[: self._max_active]
        recent_text = "\n\n".join(snapshot.exchange_texts[-3:]).strip()
        for activation in top:
            prompt = (
                "Does the following reading-stance recipe fit the current exchange? "
                "Answer: fits / unfits / ambiguous. Add one phrase explaining.\n\n"
                f"Stance: {activation.payload.walk[-1].recipe[:500]}\n\n"
                f"Recent exchange: {recent_text[:1500]}"
            )
            try:
                response = self._aux_llm_fn(prompt)
            except Exception as exc:
                logger.debug("aux_llm_fn failed during matcher refinement: %s", exc)
                continue
            if not response:
                continue
            lowered = response.lower()
            if "unfits" in lowered:
                activation.score = max(0.0, activation.score - 0.2)
            elif "fits" in lowered and "unfits" not in lowered:
                activation.score = min(1.0, activation.score + 0.1)
            activation.reasoning = (
                (activation.reasoning or "")
                + f" | aux-llm: {response.strip()[:160]}"
            )
        demoted = [
            (s.payload.crystallization_id, s.score)
            for s in scored
            if s.score < self._threshold
        ]
        return scored, demoted


# ---------------------------------------------------------------------------
# ContextSnapshot builder — reads exchange_buffer into a snapshot.
# ---------------------------------------------------------------------------


_INVOCATION_PATTERNS = [
    re.compile(r"inhabit this position[:\s]+(.*)", re.IGNORECASE),
    re.compile(r"work from this stance[:\s]+(.*)", re.IGNORECASE),
    re.compile(r"load (?:the )?profile[:\s]+(.*)", re.IGNORECASE),
    re.compile(r"activate touchstone[:\s]+(.*)", re.IGNORECASE),
]


def build_snapshot_from_exchange_buffer(
    exchange_buffer: Sequence[Any],
    *,
    active_files: Optional[Sequence[str]] = None,
    affective_register_hint: Optional[str] = None,
    routing_context_signals: Optional[Sequence[str]] = None,
    recent_n: int = 5,
) -> ContextSnapshot:
    """
    Build a ContextSnapshot from Reframe's exchange_buffer objects.

    Reads the last `recent_n` exchanges. Extracts user_prompt_preview /
    user_prompt and assistant_response when available, scans for user-
    invocation phrases.

    Works with either ExchangeMetadata or ConversationBufferEntry objects
    (both patterns present in Reframe); attribute access is defensive.
    """
    selected = list(exchange_buffer)[-recent_n:]
    texts: List[str] = []
    invocation_phrases: List[str] = []

    for ex in selected:
        user_text = (
            getattr(ex, "user_prompt_preview", None)
            or getattr(ex, "user_prompt", "")
            or ""
        )
        assistant_text = getattr(ex, "assistant_response", "") or ""
        combined = (user_text + "\n" + assistant_text).strip()
        if combined:
            texts.append(combined)
        for pattern in _INVOCATION_PATTERNS:
            match = pattern.search(user_text)
            if match:
                invocation_phrases.append(match.group(0).strip())

    return ContextSnapshot(
        exchange_texts=texts,
        active_files=list(active_files or []),
        affective_register_hint=affective_register_hint,
        routing_context_signals=list(routing_context_signals or []),
        user_invocation_phrases=invocation_phrases,
    )


# ---------------------------------------------------------------------------
# Integration: BackgroundEnricher step 2d
# ---------------------------------------------------------------------------


# NOTE on the thread_graph field (Open Question #6 in the handoff briefing):
# we write the ActivationSet to thread_graph.crystallization_activations as
# a list of serialisable dicts. This field name is provisional — it should
# be confirmed with June before the Reframe patch lands. The serialisation
# shape is stable (the ActivationPayload -> dict conversion below), so the
# field-name decision can move without forcing re-work in Process 3
# (context assembly).
THREAD_GRAPH_FIELD = "crystallization_activations"


def run_matcher_step(
    thread_graph: Any,
    exchange_buffer: Sequence[Any],
    *,
    matcher: CrystallizationMatcher,
    active_files: Optional[Sequence[str]] = None,
    affective_register_hint: Optional[str] = None,
    routing_context_signals: Optional[Sequence[str]] = None,
) -> ActivationSet:
    """
    Enrichment step 2d.

    Builds a ContextSnapshot from the exchange_buffer, runs the matcher,
    and attaches the ActivationSet to the thread_graph. The attachment
    shape is JSON-safe dicts under `thread_graph.crystallization_activations`.
    Process 3 (context assembly in Reframe) reads from that field and
    composes the activation walks into main-model context.

    One-exchange lag is tolerable — this step runs after summarisation and
    edge discovery; it reads the same exchange_buffer that those steps
    produced summaries for.

    Returns the ActivationSet so callers can log / monitor, but the canonical
    output lives on the thread_graph.
    """
    snapshot = build_snapshot_from_exchange_buffer(
        exchange_buffer,
        active_files=active_files,
        affective_register_hint=affective_register_hint,
        routing_context_signals=routing_context_signals,
    )
    activation_set = matcher.match(snapshot)

    setattr(
        thread_graph,
        THREAD_GRAPH_FIELD,
        [_activation_to_dict(a) for a in activation_set.activations],
    )
    if activation_set.candidate_seed is not None:
        existing = getattr(thread_graph, "candidate_touchstone_seeds", None) or []
        existing.append(_candidate_seed_to_dict(activation_set.candidate_seed))
        setattr(thread_graph, "candidate_touchstone_seeds", existing)

    return activation_set


def _activation_to_dict(activation: ScoredActivation) -> Dict[str, Any]:
    payload = activation.payload
    return {
        "crystallization_id": payload.crystallization_id,
        "mechanism_type": payload.mechanism_type.value,
        "weight": activation.score,
        "walk": [
            {"id": n.id, "name": n.name, "recipe": n.recipe}
            for n in payload.walk
        ],
        "score_breakdown": activation.score_breakdown,
        "matched_signals": activation.matched_signals,
        "matched_anti_signals": activation.matched_anti_signals,
        "reasoning": activation.reasoning,
    }


def _candidate_seed_to_dict(seed: CandidateSeed) -> Dict[str, Any]:
    return {
        "flagged_at": seed.flagged_at,
        "top_scores": [{"id": i, "score": s} for i, s in seed.top_scores],
        "snapshot_excerpt": seed.snapshot.exchange_texts[-1][:500]
            if seed.snapshot.exchange_texts else "",
        "routing_context_signals": seed.snapshot.routing_context_signals,
        "user_invocation_phrases": seed.snapshot.user_invocation_phrases,
    }


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _join_haystack(snapshot: ContextSnapshot) -> str:
    parts: List[str] = list(snapshot.exchange_texts)
    parts.extend(snapshot.active_files)
    parts.extend(snapshot.routing_context_signals)
    parts.extend(snapshot.user_invocation_phrases)
    if snapshot.affective_register_hint:
        parts.append(snapshot.affective_register_hint)
    return "\n".join(parts).lower()


def _phrase_in(phrase: str, haystack: str) -> bool:
    """
    Case-insensitive phrase match. Treats multi-word phrases as whole substring
    matches. A richer matcher (stemming, fuzzy match) can replace this without
    changing signatures.
    """
    needle = phrase.strip().lower()
    if not needle:
        return False
    return needle in haystack


def _compose_reasoning(
    record: CrystallizationObject,
    matched: List[str],
    anti: List[str],
    breakdown: Dict[str, float],
) -> str:
    parts = [f"{record.mechanism_type.value}:{record.id}"]
    if matched:
        parts.append(f"signals={matched}")
    if anti:
        parts.append(f"anti={anti}")
    parts.append(
        "breakdown="
        + ", ".join(f"{k}={v:.2f}" for k, v in breakdown.items() if k != "total")
    )
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Integration notes for background_enricher.py
# ---------------------------------------------------------------------------
#
# To wire this step into Reframe, append to BackgroundEnricher.__init__:
#
#     self._crystallization_matcher: Optional[CrystallizationMatcher] = None
#
#     def set_crystallization_matcher(self, matcher: CrystallizationMatcher) -> None:
#         self._crystallization_matcher = matcher
#
# And append to BackgroundEnricher.run_enrichment_cycle after step 3:
#
#     # 2d. Crystallization activation matcher
#     if self._crystallization_matcher is not None:
#         from matcher_step_2d import run_matcher_step
#         try:
#             run_matcher_step(
#                 thread_graph,
#                 exchange_buffer,
#                 matcher=self._crystallization_matcher,
#                 # active_files / routing_context_signals: wire from the
#                 # surrounding Reframe state when those feeds exist; leave
#                 # empty otherwise. The matcher degrades gracefully.
#             )
#         except Exception as exc:
#             logger.debug("Crystallization matcher step failed: %s", exc)
#
# The matcher is injected rather than constructed inside BackgroundEnricher so
# the wiring layer (Reframe startup) controls which substrate and aux-LLM path
# the matcher uses. That keeps this module decoupled from Reframe's DI wiring
# and makes the Kintsugi substrate swap trivial when CC consultation resolves.
