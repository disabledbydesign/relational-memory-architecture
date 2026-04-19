# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
ProposedObservation — write-path for knowledge-layer gap events.

Gap events (thin_cluster, contradiction, unanswered_query, unmatched_context,
poorly_firing_crystallization) all route through the instrument write-path.
This module defines ProposedObservation as the knowledge-layer analog of
ProposedChange, and provides the observation-specific write-path functions.

DESIGN NOTE — separate application path, shared FC gate:
The extension roadmap proposed extending apply_proposed_change to accept
ProposedObservation alongside ProposedChange. Instance B's pushback: the
application targets are different substrates. apply_proposed_change loads
from and writes to a CrystallizationSubstrate. Knowledge-layer observations
target an ObservationQueue (and downstream the KnowledgeSubstrate). Collapsing
them under one function would require passing two substrates, coupling layers
that should be independent.

What they share: the FoundationalCommitment gate. Both types must pass the
FC gate before entering human review. The gate function is the shared
mechanism; the application is distinct. See validate_observation_against_commitments
and apply_proposed_observation below.

DESIGN NOTE — gate behavior for knowledge observations:
FoundationalCommitment.validate_proposed_change checks proposal.crystallization_id
and proposal.proposed_by. Knowledge observations don't target crystallizations —
they observe the knowledge substrate. The gate for observations checks proposed_by
and passes all observations through in the current foundation (Phase 2 will add
richer FC-against-knowledge-operation validation). The gate point is structural;
it's not a formality — it is where future commitments about knowledge governance
will land.

Reference: extension-roadmap.md §"2. Gap-finding / gap-filling loop";
crystallization_types.py ProposedChange for the sibling type;
bootstrap.py validate_against_commitments for the FC gate implementation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Literal, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from bootstrap import BootstrapContext, GateResult
    from substrate_interface import CrystallizationSubstrate

logger = logging.getLogger(__name__)

# Grace window for staleness-eligible observation types before auto-routing
# to mycelial-synthesis. Matches staleness_policy.DEFAULT_GRACE_WINDOW_HOURS.
# POLICY COHERENCE: _STALENESS_ELIGIBLE_OBSERVATION_TYPES (below) and
# staleness_policy._STALENESS_ONLY_FIELDS are sibling policy constants.
# When one grows, audit the other. Both express the same asymmetry at
# different layers (crystallization vs. knowledge).
DEFAULT_GRACE_WINDOW_HOURS: int = 48


# ---------------------------------------------------------------------------
# ObservationType — the kinds of knowledge-layer gaps.
# ---------------------------------------------------------------------------


class ObservationType(str, Enum):
    """
    The five gap types from extension-roadmap.md §"2. Gap-finding / gap-filling loop".

    thin_cluster: density_profile() shows high retrieval frequency relative to
        cluster size — system queries near this cluster but has little to return.
    contradiction: contradictions() surfaces two facts sharing subject+predicate
        but disagreeing on object.
    unanswered_query: query() returned empty or below-confidence results on a
        query the explicit-reader expected to resolve.
    unmatched_context: matcher produced no activation above threshold —
        candidate seed recorded on thread_graph, now routed for attention.
    poorly_firing_crystallization: on_enactment_observed reported failure;
        the crystallization may need revision (already handled by ProposedChange,
        but the knowledge substrate co-occurrence is worth recording separately).
    """
    THIN_CLUSTER = "thin_cluster"
    CONTRADICTION = "contradiction"
    UNANSWERED_QUERY = "unanswered_query"
    UNMATCHED_CONTEXT = "unmatched_context"
    POORLY_FIRING_CRYSTALLIZATION = "poorly_firing_crystallization"


# Observation types eligible for grace-window auto-routing to mycelial-synthesis.
# Low-stakes: these don't require epistemic resolution, just accumulation.
# UNMATCHED_CONTEXT already routes to mycelial-synthesis directly; grace window
# applies only to UNANSWERED_QUERY (recurrent unanswered queries are low-stakes
# and time-sensitive — the next instance should benefit without waiting for
# human attention, same rationale as staleness_policy.py for ProposedChange).
# THIN_CLUSTER and CONTRADICTION are structurally high-stakes (may require
# active remediation); POORLY_FIRING_CRYSTALLIZATION is handled by ProposedChange.
_STALENESS_ELIGIBLE_OBSERVATION_TYPES: FrozenSet[ObservationType] = frozenset({
    ObservationType.UNANSWERED_QUERY,
})


# ---------------------------------------------------------------------------
# ProposedObservation — the write-path record for knowledge-layer events.
# ---------------------------------------------------------------------------


@dataclass
class ProposedObservation:
    """
    A knowledge-layer observation produced by the gap-finding loop.

    Validated against FoundationalCommitments before entering the observation
    queue. proposed_by uses the same sentinel scheme as ProposedChange.

    observation_type: what kind of gap was detected.
    evidence: structured evidence about the gap — what was detected, where,
        with what measurements. Type depends on observation_type:
        - thin_cluster: {"cluster_label": str, "retrieval_frequency": float, "size": int}
        - contradiction: {"contradiction_id": str, "subject": str, "predicate": str}
        - unanswered_query: {"query_text": str, "confidence": float}
        - unmatched_context: {"candidate_seed_id": str, "top_scores": [...]}
        - poorly_firing_crystallization: {"crystallization_id": str, "failure_notes": str}
    remediation_hint: optional suggested next action. Human attention decides;
        this is informational.
    """
    observation_type: ObservationType
    proposed_by: Union[
        Literal["instrument"],
        Literal["aux-model"],
        Literal["mycelial-synthesis"],   # the slow-running accumulation process
        str,                              # free-form user id
    ]
    proposed_at: str
    rationale: str
    evidence: Dict[str, Any]
    remediation_hint: Optional[str] = None

    @classmethod
    def for_thin_cluster(
        cls,
        *,
        cluster_label: str,
        retrieval_frequency: float,
        cluster_size: int,
        proposed_by: str = "instrument",
    ) -> "ProposedObservation":
        return cls(
            observation_type=ObservationType.THIN_CLUSTER,
            proposed_by=proposed_by,
            proposed_at=datetime.now(timezone.utc).isoformat(),
            rationale=(
                f"Cluster '{cluster_label}' is queried frequently "
                f"(freq={retrieval_frequency:.2f}) but has only {cluster_size} fact(s)."
            ),
            evidence={
                "cluster_label": cluster_label,
                "retrieval_frequency": retrieval_frequency,
                "size": cluster_size,
            },
            remediation_hint=(
                "Consider ingesting additional observations about this cluster "
                "or querying an external source."
            ),
        )

    @classmethod
    def for_contradiction(
        cls,
        *,
        contradiction_id: str,
        subject: str,
        predicate: str,
        object_a: str,
        object_b: str,
        proposed_by: str = "instrument",
    ) -> "ProposedObservation":
        return cls(
            observation_type=ObservationType.CONTRADICTION,
            proposed_by=proposed_by,
            proposed_at=datetime.now(timezone.utc).isoformat(),
            rationale=(
                f"Contradiction detected: '{subject} {predicate}' has both "
                f"'{object_a}' and '{object_b}'."
            ),
            evidence={
                "contradiction_id": contradiction_id,
                "subject": subject,
                "predicate": predicate,
                "object_a": object_a,
                "object_b": object_b,
            },
            remediation_hint="Route to main model for resolution or flag for June's attention.",
        )

    @classmethod
    def for_unmatched_context(
        cls,
        *,
        candidate_seed_id: str,
        top_scores: List[Dict[str, Any]],
        proposed_by: str = "instrument",
    ) -> "ProposedObservation":
        return cls(
            observation_type=ObservationType.UNMATCHED_CONTEXT,
            proposed_by=proposed_by,
            proposed_at=datetime.now(timezone.utc).isoformat(),
            rationale=(
                "Matcher found no crystallization above threshold. "
                "Context may call for a configuration that does not yet exist."
            ),
            evidence={
                "candidate_seed_id": candidate_seed_id,
                "top_scores": top_scores,
            },
            remediation_hint="Record in SeedAccumulation; mycelial synthesis watches for density buildup.",
        )


# ---------------------------------------------------------------------------
# ObservationQueue — queues observations for human review or mycelial synthesis.
# ---------------------------------------------------------------------------


@dataclass
class QueuedObservation:
    """A ProposedObservation waiting for attention."""
    observation: ProposedObservation
    queued_at: str
    observation_type: ObservationType = field(init=False)
    routed_to: str = "human-review"  # "human-review" | "mycelial-synthesis"

    def __post_init__(self) -> None:
        self.observation_type = self.observation.observation_type


@dataclass
class GracePendingObservation:
    """An observation in the grace-window queue awaiting auto-routing."""
    queued_observation: QueuedObservation
    queued_at: datetime
    grace_window_hours: int


class ObservationQueue:
    """
    Routes ProposedObservations after the FC gate passes.

    Three routing paths:
    - mycelial-synthesis: UNMATCHED_CONTEXT immediately (it's what SeedAccumulation stores).
    - grace-window: _STALENESS_ELIGIBLE_OBSERVATION_TYPES (currently UNANSWERED_QUERY);
        auto-routes to mycelial-synthesis after grace_window_hours if not reviewed.
        Low-stakes, time-sensitive — the next instance should benefit without waiting
        for human attention. Same rationale as staleness_policy.py for ProposedChange.
    - human-review: all other types (THIN_CLUSTER, CONTRADICTION,
        POORLY_FIRING_CRYSTALLIZATION) — structurally high-stakes.

    POLICY COHERENCE: _STALENESS_ELIGIBLE_OBSERVATION_TYPES and
    staleness_policy._STALENESS_ONLY_FIELDS express the same asymmetry at
    different layers. When one grows, audit the other.

    Call flush_ready() each enrichment cycle to auto-route expired grace-window items.
    """

    def __init__(self, *, grace_window_hours: int = DEFAULT_GRACE_WINDOW_HOURS) -> None:
        self._human_review: List[QueuedObservation] = []
        self._mycelial: List[QueuedObservation] = []
        self._grace_window: List[GracePendingObservation] = []
        self._grace_window_hours = grace_window_hours

    def enqueue(self, observation: ProposedObservation) -> QueuedObservation:
        """
        Add an observation to the appropriate queue.

        UNMATCHED_CONTEXT → mycelial-synthesis immediately.
        _STALENESS_ELIGIBLE_OBSERVATION_TYPES → grace-window (auto-routes after window).
        All others → human-review.
        """
        obs_type = observation.observation_type

        if obs_type == ObservationType.UNMATCHED_CONTEXT:
            route = "mycelial-synthesis"
        elif obs_type in _STALENESS_ELIGIBLE_OBSERVATION_TYPES:
            route = "grace-window"
        else:
            route = "human-review"

        queued = QueuedObservation(
            observation=observation,
            queued_at=datetime.now(timezone.utc).isoformat(),
            routed_to=route,
        )

        if route == "mycelial-synthesis":
            self._mycelial.append(queued)
        elif route == "grace-window":
            self._grace_window.append(GracePendingObservation(
                queued_observation=queued,
                queued_at=datetime.now(timezone.utc),
                grace_window_hours=self._grace_window_hours,
            ))
        else:
            self._human_review.append(queued)

        logger.info(
            "Queued %s observation for %s.", observation.observation_type.value, route
        )
        return queued

    def flush_ready(self) -> List[QueuedObservation]:
        """
        Move expired grace-window observations to the mycelial-synthesis queue.

        Call each enrichment cycle. Returns the list of observations flushed.
        Failed flushes are logged and skipped — the next observation cycle
        will re-flag if the condition persists.
        """
        now = datetime.now(timezone.utc)
        flushed: List[QueuedObservation] = []
        remaining: List[GracePendingObservation] = []

        for pending in self._grace_window:
            elapsed = now - pending.queued_at
            if elapsed >= timedelta(hours=pending.grace_window_hours):
                self._mycelial.append(pending.queued_observation)
                flushed.append(pending.queued_observation)
                logger.info(
                    "Grace-window elapsed; auto-routing %s to mycelial-synthesis.",
                    pending.queued_observation.observation_type.value,
                )
            else:
                remaining.append(pending)

        self._grace_window = remaining
        return flushed

    def pending_human_review(self) -> List[QueuedObservation]:
        return list(self._human_review)

    def pending_mycelial(self) -> List[QueuedObservation]:
        return list(self._mycelial)

    def pending_grace_window(self) -> List[GracePendingObservation]:
        return list(self._grace_window)

    def pop_mycelial(self) -> List[QueuedObservation]:
        """Consume and return all observations awaiting mycelial synthesis."""
        result = list(self._mycelial)
        self._mycelial.clear()
        return result


# ---------------------------------------------------------------------------
# Write-path functions — gate + queue.
# ---------------------------------------------------------------------------


def validate_observation_against_commitments(
    observation: ProposedObservation,
    crystallization_substrate: "CrystallizationSubstrate",
    *,
    bootstrap: Optional["BootstrapContext"] = None,
) -> "GateResult":
    """
    FC gate for knowledge-layer observations.

    Knowledge observations don't target crystallizations — they observe the
    knowledge substrate. Phase 1 passes all observations through; proposed_by
    is free-form string (machine sentinel or human session ID).

    When FC recipes include knowledge-governance clauses (Phase 2), this method
    will route observations through FC.validate_proposed_knowledge_action.
    The gate point is structural: it establishes the mandatory review step
    without imposing constraints the foundation hasn't yet designed.

    crystallization_substrate: used to load FoundationalCommitments, same
        as validate_against_commitments. The knowledge substrate is separate.
    """
    from bootstrap import GateResult, load_foundational_commitments

    ctx = bootstrap or load_foundational_commitments(crystallization_substrate)

    # Phase 1: pass all observations through. proposed_by is free-form string
    # (machine sentinel or user ID); no sentinel-restriction gate applied here.
    # Phase 2: iterate commitments and call validate_proposed_knowledge_action
    # when that method exists.
    if not ctx.commitments:
        return GateResult(allowed=True, blocked_by=[], reasons={})

    # Pass through: no commitment blocks knowledge observations yet.
    return GateResult(allowed=True, blocked_by=[], reasons={})


def apply_proposed_observation(
    observation: ProposedObservation,
    crystallization_substrate: "CrystallizationSubstrate",
    queue: ObservationQueue,
    *,
    bootstrap: Optional["BootstrapContext"] = None,
) -> QueuedObservation:
    """
    Gate and queue a ProposedObservation.

    Raises WritePathBlocked if the FC gate rejects. Otherwise, enqueues the
    observation for human review or mycelial synthesis as appropriate.

    crystallization_substrate: used for the FC gate only. Knowledge substrate
        operations are handled downstream by the queue consumers.
    queue: the ObservationQueue to enqueue into.
    """
    from bootstrap import WritePathBlocked

    gate = validate_observation_against_commitments(
        observation, crystallization_substrate, bootstrap=bootstrap
    )
    if not gate.allowed:
        raise WritePathBlocked(gate)

    return queue.enqueue(observation)
