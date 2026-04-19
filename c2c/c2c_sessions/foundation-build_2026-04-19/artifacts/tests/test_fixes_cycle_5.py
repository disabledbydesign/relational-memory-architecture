# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Regression tests for the four fixes applied in Instance B's cycle 5:

  Fix #1 — dead validation branch in validate_observation_against_commitments
            removed; free-form proposed_by allowed (not just sentinels).
  Fix #2 — true single-linkage in SeedAccumulation.cluster()
            (was seed-linkage; chain arcs now merge correctly).
  Fix #3 — staleness-eligible grace-window queue in ObservationQueue
            (UNANSWERED_QUERY goes to grace window, not human-review).
  Fix #4 — ActivationSet → ReadingStanceFilter conversion helper in
            wiring_helpers.py (previously undocumented seam).

Each fix has a test class. Tests verify the specific behaviour the fix
introduced, plus one or two regression cases.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from crystallization_schema import (
    ActivationConditions,
    ActivationFormat,
    ActivationScope,
    MechanismType,
)
from crystallization_types import build_prescriptive_profile
from knowledge_substrate import ReadingStanceFilter
from matcher_step_2d import ActivationSet, CandidateSeed, ContextSnapshot, ScoredActivation
from proposed_observation import (
    DEFAULT_GRACE_WINDOW_HOURS,
    GracePendingObservation,
    ObservationQueue,
    ObservationType,
    ProposedObservation,
    _STALENESS_ELIGIBLE_OBSERVATION_TYPES,
    validate_observation_against_commitments,
)
from seed_accumulation import ConfigurationalKey, SeedAccumulation
from substrate_interface import LocalFileSubstrate
from wiring_helpers import activation_set_to_reading_stance_filter


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _queue(grace_window_hours: int = DEFAULT_GRACE_WINDOW_HOURS) -> ObservationQueue:
    return ObservationQueue(grace_window_hours=grace_window_hours)


def _substrate(tmp_path: Path) -> LocalFileSubstrate:
    return LocalFileSubstrate(tmp_path)


def _key(crystallization_ids=(), frameworks=(), topics=()):
    return ConfigurationalKey(
        top_crystallization_ids=frozenset(crystallization_ids),
        framework_tokens=frozenset(frameworks),
        snapshot_topic_tokens=frozenset(topics),
    )


def _seed_event(acc: SeedAccumulation, seed_dict: dict, session_id: str = "s0") -> None:
    acc.add(seed_dict, session_id=session_id)


def _make_seed_dict(crystallization_ids=(), routing_signals=(), excerpt="test exchange"):
    return {
        "top_scores": [{"id": cid, "score": 0.2} for cid in crystallization_ids],
        "routing_context_signals": list(routing_signals),
        "snapshot_excerpt": excerpt,
        "flagged_at": "2026-04-19T00:00:00+00:00",
    }


# ---------------------------------------------------------------------------
# Fix #1 — dead validation branch
# ---------------------------------------------------------------------------


class TestProposedByValidation:
    """
    validate_observation_against_commitments previously had a dead
    `not isinstance(observation.proposed_by, str)` branch that could never
    fire. Fix: delete the branch; gate passes all string proposed_by values.
    Design choice: free-form user IDs are valid (annotations, human sessions).
    """

    def test_instrument_sentinel_passes(self, tmp_path):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=1.0, cluster_size=1,
            proposed_by="instrument",
        )
        result = validate_observation_against_commitments(obs, _substrate(tmp_path))
        assert result.allowed is True

    def test_aux_model_sentinel_passes(self, tmp_path):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=1.0, cluster_size=1,
            proposed_by="aux-model",
        )
        result = validate_observation_against_commitments(obs, _substrate(tmp_path))
        assert result.allowed is True

    def test_mycelial_synthesis_sentinel_passes(self, tmp_path):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=1.0, cluster_size=1,
            proposed_by="mycelial-synthesis",
        )
        result = validate_observation_against_commitments(obs, _substrate(tmp_path))
        assert result.allowed is True

    def test_free_form_user_id_passes(self, tmp_path):
        """
        User IDs (email, session ID, etc.) must be allowed — observations can
        be attributed to human annotation sessions, not only machine processes.
        The dead branch would have blocked these if it ever fired; now it's gone.
        """
        for user_id in ["june@example.com", "session-abc123", "thomas-e", ""]:
            obs = ProposedObservation(
                observation_type=ObservationType.THIN_CLUSTER,
                proposed_by=user_id,
                proposed_at="2026-04-19T00:00:00+00:00",
                rationale="human annotation",
                evidence={},
            )
            result = validate_observation_against_commitments(obs, _substrate(tmp_path))
            assert result.allowed is True, f"Expected allowed for proposed_by={user_id!r}"

    def test_garbage_string_still_passes(self, tmp_path):
        """
        The gate is structural in Phase 1. No string value is rejected.
        Phase 2 will add FC-governed knowledge constraints.
        """
        obs = ProposedObservation(
            observation_type=ObservationType.CONTRADICTION,
            proposed_by="totally-made-up-source-xyz",
            proposed_at="2026-04-19T00:00:00+00:00",
            rationale="test",
            evidence={},
        )
        result = validate_observation_against_commitments(obs, _substrate(tmp_path))
        assert result.allowed is True


# ---------------------------------------------------------------------------
# Fix #2 — true single-linkage in SeedAccumulation.cluster()
# ---------------------------------------------------------------------------


class TestSingleLinkageClustering:
    """
    cluster() previously used seed-linkage (compare only against group's first
    event). True single-linkage compares against ANY current group member,
    propagating chains. A's chain test: {1,2}, {2,3}, {3,4} at threshold 0.3
    should all join one cluster under single-linkage.
    """

    def _chain_accumulation(self) -> SeedAccumulation:
        """Three seeds in a chain: A overlaps B, B overlaps C, but A and C don't."""
        acc = SeedAccumulation()
        # Seed A: crystallization IDs {1, 2}
        acc.add(_make_seed_dict(crystallization_ids=["c1", "c2"]), session_id="s0")
        # Seed B: crystallization IDs {2, 3}  — overlaps A at Jaccard 0.33
        acc.add(_make_seed_dict(crystallization_ids=["c2", "c3"]), session_id="s0")
        # Seed C: crystallization IDs {3, 4}  — overlaps B at 0.33, A at 0.0
        acc.add(_make_seed_dict(crystallization_ids=["c3", "c4"]), session_id="s0")
        return acc

    def test_chain_merges_under_single_linkage(self):
        acc = self._chain_accumulation()
        clusters = acc.cluster(overlap_threshold=0.3, min_events=1)
        assert len(clusters) == 1, (
            f"Expected 1 cluster (chain A→B→C should merge), got {len(clusters)}"
        )
        assert clusters[0].intensity.event_count == 3

    def test_seed_linkage_would_have_split_this_chain(self):
        """
        Documents the failure mode the fix addresses. Seed-linkage (first-only
        comparison) would produce 2 clusters: {A, B} and {C}. This test verifies
        the distinction — if it fails, single-linkage has regressed to seed-linkage.
        """
        acc = self._chain_accumulation()
        clusters = acc.cluster(overlap_threshold=0.3, min_events=1)
        cluster_sizes = sorted([c.intensity.event_count for c in clusters], reverse=True)
        # Under seed-linkage: [2, 1]. Under true single-linkage: [3].
        assert cluster_sizes != [2, 1], (
            "cluster() produced seed-linkage result {2,1}; chain propagation not working."
        )

    def test_non_overlapping_seeds_stay_separate(self):
        """Seeds with no shared elements should not merge."""
        acc = SeedAccumulation()
        # Use completely different excerpts so topic-token extraction produces no overlap.
        acc.add(
            _make_seed_dict(crystallization_ids=["c1"], routing_signals=["finance"],
                            excerpt="portfolio derivatives hedging"),
            session_id="s0",
        )
        acc.add(
            _make_seed_dict(crystallization_ids=["c99"], routing_signals=["welfare"],
                            excerpt="relational accountability commitment"),
            session_id="s0",
        )
        clusters = acc.cluster(overlap_threshold=0.3, min_events=1)
        assert len(clusters) == 2

    def test_identical_seeds_cluster_together(self):
        acc = SeedAccumulation()
        for _ in range(3):
            acc.add(_make_seed_dict(crystallization_ids=["c1", "c2"]), session_id="s0")
        clusters = acc.cluster(overlap_threshold=0.3, min_events=1)
        assert len(clusters) == 1
        assert clusters[0].intensity.event_count == 3

    def test_longer_chain_all_merges(self):
        """Four seeds in a rolling-window chain: each overlaps only its neighbors."""
        acc = SeedAccumulation()
        # A={1,2}, B={2,3}, C={3,4}, D={4,5}  — each pair shares one element
        for pair in [("c1", "c2"), ("c2", "c3"), ("c3", "c4"), ("c4", "c5")]:
            acc.add(_make_seed_dict(crystallization_ids=list(pair)), session_id="s0")
        clusters = acc.cluster(overlap_threshold=0.3, min_events=1)
        assert len(clusters) == 1
        assert clusters[0].intensity.event_count == 4


# ---------------------------------------------------------------------------
# Fix #3 — staleness-eligible grace-window queue in ObservationQueue
# ---------------------------------------------------------------------------


class TestObservationGraceWindow:
    """
    UNANSWERED_QUERY goes to grace-window queue, not human-review.
    After grace_window_hours elapses, flush_ready() moves it to mycelial.
    CONTRADICTION stays in human-review immediately.
    """

    def test_unanswered_query_routes_to_grace_window(self):
        queue = _queue(grace_window_hours=48)
        obs = ProposedObservation(
            observation_type=ObservationType.UNANSWERED_QUERY,
            proposed_by="instrument",
            proposed_at="2026-04-19T00:00:00+00:00",
            rationale="no results for welfare query",
            evidence={"query_text": "relational memory", "confidence": 0.0},
        )
        queued = queue.enqueue(obs)
        assert queued.routed_to == "grace-window"
        assert len(queue.pending_grace_window()) == 1
        assert len(queue.pending_human_review()) == 0
        assert len(queue.pending_mycelial()) == 0

    def test_contradiction_routes_to_human_review_immediately(self):
        queue = _queue()
        obs = ProposedObservation.for_contradiction(
            contradiction_id="c/1",
            subject="june",
            predicate="lives in",
            object_a="chicago",
            object_b="seattle",
        )
        queued = queue.enqueue(obs)
        assert queued.routed_to == "human-review"
        assert len(queue.pending_human_review()) == 1
        assert len(queue.pending_grace_window()) == 0

    def test_thin_cluster_routes_to_human_review_immediately(self):
        queue = _queue()
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=3.0, cluster_size=1
        )
        queued = queue.enqueue(obs)
        assert queued.routed_to == "human-review"
        assert len(queue.pending_human_review()) == 1
        assert len(queue.pending_grace_window()) == 0

    def test_flush_ready_moves_expired_to_mycelial(self):
        queue = ObservationQueue(grace_window_hours=0)  # zero-hour window for testing
        obs = ProposedObservation(
            observation_type=ObservationType.UNANSWERED_QUERY,
            proposed_by="instrument",
            proposed_at="2026-04-19T00:00:00+00:00",
            rationale="test",
            evidence={"query_text": "relational memory", "confidence": 0.0},
        )
        queue.enqueue(obs)
        assert len(queue.pending_grace_window()) == 1

        flushed = queue.flush_ready()
        assert len(flushed) == 1
        assert flushed[0].routed_to == "grace-window"
        assert len(queue.pending_grace_window()) == 0
        assert len(queue.pending_mycelial()) == 1

    def test_flush_ready_does_not_move_unexpired_items(self):
        queue = ObservationQueue(grace_window_hours=48)
        obs = ProposedObservation(
            observation_type=ObservationType.UNANSWERED_QUERY,
            proposed_by="instrument",
            proposed_at="2026-04-19T00:00:00+00:00",
            rationale="test",
            evidence={"query_text": "test", "confidence": 0.0},
        )
        queue.enqueue(obs)
        # Not enough time has passed
        flushed = queue.flush_ready()
        assert len(flushed) == 0
        assert len(queue.pending_grace_window()) == 1
        assert len(queue.pending_mycelial()) == 0

    def test_staleness_eligible_types_constant(self):
        """_STALENESS_ELIGIBLE_OBSERVATION_TYPES contains UNANSWERED_QUERY."""
        assert ObservationType.UNANSWERED_QUERY in _STALENESS_ELIGIBLE_OBSERVATION_TYPES
        # CONTRADICTION and THIN_CLUSTER are high-stakes; not eligible.
        assert ObservationType.CONTRADICTION not in _STALENESS_ELIGIBLE_OBSERVATION_TYPES
        assert ObservationType.THIN_CLUSTER not in _STALENESS_ELIGIBLE_OBSERVATION_TYPES

    def test_pop_mycelial_includes_flushed_items(self):
        """pop_mycelial() returns both directly-routed and grace-window-flushed items."""
        queue = ObservationQueue(grace_window_hours=0)
        # Direct route
        queue.enqueue(ProposedObservation.for_unmatched_context(
            candidate_seed_id="seed/0", top_scores=[]
        ))
        # Grace-window route (expires immediately at 0h)
        queue.enqueue(ProposedObservation(
            observation_type=ObservationType.UNANSWERED_QUERY,
            proposed_by="instrument",
            proposed_at="2026-04-19T00:00:00+00:00",
            rationale="test",
            evidence={"query_text": "test", "confidence": 0.0},
        ))
        queue.flush_ready()  # moves grace-window item to mycelial
        items = queue.pop_mycelial()
        assert len(items) == 2


# ---------------------------------------------------------------------------
# Fix #4 — ActivationSet → ReadingStanceFilter conversion helper
# ---------------------------------------------------------------------------


class TestActivationSetToReadingStanceFilter:
    """
    wiring_helpers.activation_set_to_reading_stance_filter() converts a
    matcher ActivationSet to a ReadingStanceFilter for knowledge-layer queries.

    The conversion requires loading each activated crystallization from the
    substrate to get task_affinity and anti_signals. That's the non-trivial
    part the prior code left as an invisible seam.
    """

    def _make_profile(self, name, task_affinity=None, anti_signals=None):
        return build_prescriptive_profile(
            profile_id=f"prescriptive-profile/{name.lower()}",
            name=name,
            recipe=f"Recipe for {name}.",
            stance_description=f"Stance for {name}.",
            context_signals=[f"{name.lower()} signal"],
            anti_signals=anti_signals or [],
            task_affinity=task_affinity or [],
        )

    def _make_activation(self, crystallization_id: str, score: float) -> ScoredActivation:
        from crystallization_types import ActivationPayload, RecipeNode
        node = RecipeNode(
            id=crystallization_id,
            name=crystallization_id,
            recipe="test recipe",
        )
        payload = ActivationPayload(
            crystallization_id=crystallization_id,
            mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE,
            walk=[node],
            weight=score,
        )
        return ScoredActivation(
            payload=payload,
            score=score,
            score_breakdown={"total": score},
            matched_signals=[],
            matched_anti_signals=[],
        )

    def _empty_activation_set(self, snapshot=None) -> ActivationSet:
        from crystallization_schema import now_iso
        return ActivationSet(
            activations=[],
            candidate_seed=None,
            snapshot=snapshot or ContextSnapshot(exchange_texts=[]),
            produced_at=now_iso(),
        )

    def _activation_set_with(self, activations: list, snapshot=None) -> ActivationSet:
        from crystallization_schema import now_iso
        return ActivationSet(
            activations=activations,
            candidate_seed=None,
            snapshot=snapshot or ContextSnapshot(exchange_texts=[]),
            produced_at=now_iso(),
        )

    def test_empty_activation_set_produces_empty_filter(self, tmp_path):
        substrate = _substrate(tmp_path)
        activation_set = self._empty_activation_set()
        rsf = activation_set_to_reading_stance_filter(activation_set, substrate)
        assert isinstance(rsf, ReadingStanceFilter)
        assert rsf.active_crystallization_weights == {}
        assert rsf.active_task_affinities == []
        assert rsf.active_anti_signals == []

    def test_weights_populated_from_activation_scores(self, tmp_path):
        substrate = _substrate(tmp_path)
        profile = self._make_profile("PaperWriting", task_affinity=["paper-writing"])
        substrate.save(profile.record)

        activation = self._make_activation(profile.record.id, score=0.75)
        activation_set = self._activation_set_with([activation])

        rsf = activation_set_to_reading_stance_filter(activation_set, substrate)
        assert profile.record.id in rsf.active_crystallization_weights
        assert abs(rsf.active_crystallization_weights[profile.record.id] - 0.75) < 1e-6

    def test_task_affinities_populated_from_activation_conditions(self, tmp_path):
        substrate = _substrate(tmp_path)
        profile = self._make_profile(
            "WelfareResearch",
            task_affinity=["welfare-research", "design-session"],
        )
        substrate.save(profile.record)

        activation = self._make_activation(profile.record.id, score=0.6)
        activation_set = self._activation_set_with([activation])

        rsf = activation_set_to_reading_stance_filter(activation_set, substrate)
        assert "welfare-research" in rsf.active_task_affinities
        assert "design-session" in rsf.active_task_affinities

    def test_anti_signals_populated_from_activation_conditions(self, tmp_path):
        substrate = _substrate(tmp_path)
        profile = self._make_profile(
            "AcademicWriting",
            anti_signals=["casual-tone", "slang"],
        )
        substrate.save(profile.record)

        activation = self._make_activation(profile.record.id, score=0.55)
        activation_set = self._activation_set_with([activation])

        rsf = activation_set_to_reading_stance_filter(activation_set, substrate)
        assert "casual-tone" in rsf.active_anti_signals
        assert "slang" in rsf.active_anti_signals

    def test_multiple_activations_aggregate_correctly(self, tmp_path):
        substrate = _substrate(tmp_path)
        p1 = self._make_profile("Profile1", task_affinity=["task-a"], anti_signals=["anti-x"])
        p2 = self._make_profile("Profile2", task_affinity=["task-b"], anti_signals=["anti-y"])
        substrate.save(p1.record)
        substrate.save(p2.record)

        a1 = self._make_activation(p1.record.id, score=0.8)
        a2 = self._make_activation(p2.record.id, score=0.5)
        activation_set = self._activation_set_with([a1, a2])

        rsf = activation_set_to_reading_stance_filter(activation_set, substrate)
        assert len(rsf.active_crystallization_weights) == 2
        assert "task-a" in rsf.active_task_affinities
        assert "task-b" in rsf.active_task_affinities
        assert "anti-x" in rsf.active_anti_signals
        assert "anti-y" in rsf.active_anti_signals

    def test_duplicate_affinities_deduplicated(self, tmp_path):
        """Two activations sharing a task_affinity produce only one entry."""
        substrate = _substrate(tmp_path)
        p1 = self._make_profile("Profile1", task_affinity=["shared-task"])
        p2 = self._make_profile("Profile2", task_affinity=["shared-task", "unique-task"])
        substrate.save(p1.record)
        substrate.save(p2.record)

        a1 = self._make_activation(p1.record.id, score=0.7)
        a2 = self._make_activation(p2.record.id, score=0.6)
        activation_set = self._activation_set_with([a1, a2])

        rsf = activation_set_to_reading_stance_filter(activation_set, substrate)
        assert rsf.active_task_affinities.count("shared-task") == 1
        assert "unique-task" in rsf.active_task_affinities

    def test_missing_crystallization_skipped_gracefully(self, tmp_path):
        """A crystallization ID in the ActivationSet but not in the substrate is skipped."""
        substrate = _substrate(tmp_path)
        activation = self._make_activation("prescriptive-profile/nonexistent", score=0.9)
        activation_set = self._activation_set_with([activation])

        # Should not raise; weight is still recorded, but affinity/anti-signal lookup skips.
        rsf = activation_set_to_reading_stance_filter(activation_set, substrate)
        assert "prescriptive-profile/nonexistent" in rsf.active_crystallization_weights
        assert rsf.active_task_affinities == []
        assert rsf.active_anti_signals == []
