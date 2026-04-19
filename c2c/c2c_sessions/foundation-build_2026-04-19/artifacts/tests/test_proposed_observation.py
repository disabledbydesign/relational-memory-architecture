# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for proposed_observation.py.

Covers: ProposedObservation factory methods, ObservationType enum,
ObservationQueue routing (unmatched_context → mycelial; others → human-review),
validate_observation_against_commitments gate behavior,
apply_proposed_observation raises WritePathBlocked on gate failure.

Key verification: the FC gate is called before queuing; the application path
is separate from apply_proposed_change (different substrate, different target).
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from proposed_observation import (
    ObservationQueue,
    ObservationType,
    ProposedObservation,
    QueuedObservation,
    apply_proposed_observation,
    validate_observation_against_commitments,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def substrate(tmp_path):
    """LocalFileSubstrate with no FoundationalCommitments loaded."""
    from substrate_interface import LocalFileSubstrate
    return LocalFileSubstrate(tmp_path)


@pytest.fixture
def queue():
    return ObservationQueue()


# ---------------------------------------------------------------------------
# TestProposedObservationFactories
# ---------------------------------------------------------------------------


class TestProposedObservationFactories:
    def test_for_thin_cluster(self):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="welfare-theory",
            retrieval_frequency=4.5,
            cluster_size=2,
        )
        assert obs.observation_type == ObservationType.THIN_CLUSTER
        assert obs.evidence["cluster_label"] == "welfare-theory"
        assert obs.evidence["size"] == 2
        assert obs.proposed_by == "instrument"
        assert obs.remediation_hint is not None

    def test_for_contradiction(self):
        obs = ProposedObservation.for_contradiction(
            contradiction_id="c/abc",
            subject="june",
            predicate="lives in",
            object_a="chicago",
            object_b="seattle",
        )
        assert obs.observation_type == ObservationType.CONTRADICTION
        assert obs.evidence["subject"] == "june"
        assert obs.evidence["object_a"] == "chicago"
        assert obs.evidence["object_b"] == "seattle"

    def test_for_unmatched_context(self):
        obs = ProposedObservation.for_unmatched_context(
            candidate_seed_id="seed/000001",
            top_scores=[{"id": "profile/welfare", "score": 0.2}],
        )
        assert obs.observation_type == ObservationType.UNMATCHED_CONTEXT
        assert obs.evidence["candidate_seed_id"] == "seed/000001"

    def test_proposed_at_is_populated(self):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=1.0, cluster_size=1
        )
        assert obs.proposed_at is not None
        assert len(obs.proposed_at) > 0


# ---------------------------------------------------------------------------
# TestObservationQueue
# ---------------------------------------------------------------------------


class TestObservationQueue:
    def test_unmatched_context_routes_to_mycelial(self, queue):
        obs = ProposedObservation.for_unmatched_context(
            candidate_seed_id="seed/0", top_scores=[]
        )
        queued = queue.enqueue(obs)
        assert queued.routed_to == "mycelial-synthesis"
        assert len(queue.pending_mycelial()) == 1
        assert len(queue.pending_human_review()) == 0

    def test_thin_cluster_routes_to_human_review(self, queue):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=3.0, cluster_size=1
        )
        queued = queue.enqueue(obs)
        assert queued.routed_to == "human-review"
        assert len(queue.pending_human_review()) == 1
        assert len(queue.pending_mycelial()) == 0

    def test_contradiction_routes_to_human_review(self, queue):
        obs = ProposedObservation.for_contradiction(
            contradiction_id="c/1",
            subject="june",
            predicate="lives in",
            object_a="chicago",
            object_b="seattle",
        )
        queued = queue.enqueue(obs)
        assert queued.routed_to == "human-review"

    def test_pop_mycelial_clears_queue(self, queue):
        obs = ProposedObservation.for_unmatched_context(
            candidate_seed_id="seed/0", top_scores=[]
        )
        queue.enqueue(obs)
        popped = queue.pop_mycelial()
        assert len(popped) == 1
        assert len(queue.pending_mycelial()) == 0

    def test_multiple_observations_accumulated(self, queue):
        for i in range(3):
            queue.enqueue(ProposedObservation.for_thin_cluster(
                cluster_label=f"cluster-{i}",
                retrieval_frequency=float(i),
                cluster_size=1,
            ))
        assert len(queue.pending_human_review()) == 3

    def test_queued_observation_attributes(self, queue):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=1.0, cluster_size=1
        )
        queued = queue.enqueue(obs)
        assert isinstance(queued, QueuedObservation)
        assert queued.queued_at is not None
        assert queued.observation_type == ObservationType.THIN_CLUSTER


# ---------------------------------------------------------------------------
# TestValidateObservationAgainstCommitments
# ---------------------------------------------------------------------------


class TestValidateObservationAgainstCommitments:
    def test_passes_with_no_commitments(self, substrate):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=1.0, cluster_size=1
        )
        result = validate_observation_against_commitments(obs, substrate)
        assert result.allowed is True
        assert result.blocked_by == []

    def test_passes_for_all_valid_proposers(self, substrate):
        for proposer in ["instrument", "aux-model", "mycelial-synthesis", "june@example.com"]:
            obs = ProposedObservation(
                observation_type=ObservationType.THIN_CLUSTER,
                proposed_by=proposer,
                proposed_at="2026-04-19T00:00:00+00:00",
                rationale="test",
                evidence={},
            )
            result = validate_observation_against_commitments(obs, substrate)
            assert result.allowed is True, f"Expected allowed for proposer {proposer!r}"

    def test_passes_unmatched_context(self, substrate):
        obs = ProposedObservation.for_unmatched_context(
            candidate_seed_id="seed/0", top_scores=[]
        )
        result = validate_observation_against_commitments(obs, substrate)
        assert result.allowed is True

    def test_gate_is_called_independently_of_apply_proposed_change(self, substrate):
        """
        Gate for observations uses a separate code path from crystallization gate.
        Verifies the architectural separation noted in the module docstring.
        """
        # apply_proposed_change would require a crystallization_id and target;
        # validate_observation_against_commitments does not.
        obs = ProposedObservation.for_contradiction(
            contradiction_id="c/1",
            subject="june",
            predicate="lives in",
            object_a="chicago",
            object_b="seattle",
        )
        # This should not raise even though no crystallization_id is present
        result = validate_observation_against_commitments(obs, substrate)
        assert result.allowed is True


# ---------------------------------------------------------------------------
# TestApplyProposedObservation
# ---------------------------------------------------------------------------


class TestApplyProposedObservation:
    def test_apply_enqueues_observation(self, substrate, queue):
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=3.0, cluster_size=1
        )
        queued = apply_proposed_observation(obs, substrate, queue)
        assert queued.routed_to == "human-review"
        assert len(queue.pending_human_review()) == 1

    def test_apply_unmatched_context_to_mycelial(self, substrate, queue):
        obs = ProposedObservation.for_unmatched_context(
            candidate_seed_id="seed/0", top_scores=[]
        )
        queued = apply_proposed_observation(obs, substrate, queue)
        assert queued.routed_to == "mycelial-synthesis"

    def test_apply_uses_different_substrate_than_proposed_change(self, substrate, queue, tmp_path):
        """
        apply_proposed_observation takes a CrystallizationSubstrate for the
        FC gate and an ObservationQueue for the observation, not a KnowledgeSubstrate.
        This test verifies the signature does not require a KnowledgeSubstrate.
        """
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="y", retrieval_frequency=1.0, cluster_size=2
        )
        # Should work with the crystallization substrate for the gate
        queued = apply_proposed_observation(obs, substrate, queue)
        assert queued is not None

    def test_apply_raises_write_path_blocked_on_gate_failure(self, substrate, queue):
        """
        If the gate fails (simulated by monkeypatching), WritePathBlocked is raised.
        """
        from bootstrap import GateResult
        import proposed_observation as po

        # Monkeypatch the gate to always block
        original = po.validate_observation_against_commitments

        def always_block(obs, sub, *, bootstrap=None):
            return GateResult(
                allowed=False,
                blocked_by=["test-commitment"],
                reasons={"test-commitment": "simulated block"},
            )

        po.validate_observation_against_commitments = always_block
        try:
            from bootstrap import WritePathBlocked
            obs = ProposedObservation.for_thin_cluster(
                cluster_label="z", retrieval_frequency=1.0, cluster_size=1
            )
            with pytest.raises(WritePathBlocked):
                apply_proposed_observation(obs, substrate, queue)
        finally:
            po.validate_observation_against_commitments = original


# ---------------------------------------------------------------------------
# TestSeparationFromProposedChange
# ---------------------------------------------------------------------------


class TestSeparationFromProposedChange:
    def test_proposed_observation_has_no_crystallization_id(self):
        """
        ProposedObservation does not carry a crystallization_id.
        It targets the knowledge layer, not crystallization records.
        ProposedChange carries crystallization_id; the two types are distinct.
        """
        obs = ProposedObservation.for_thin_cluster(
            cluster_label="x", retrieval_frequency=1.0, cluster_size=1
        )
        assert not hasattr(obs, "crystallization_id")
        assert not hasattr(obs, "field_updates")
        assert not hasattr(obs, "archive_prior_version")

    def test_proposed_observation_has_evidence_not_field_updates(self):
        obs = ProposedObservation.for_contradiction(
            contradiction_id="c/1",
            subject="s",
            predicate="p",
            object_a="a",
            object_b="b",
        )
        assert hasattr(obs, "evidence")
        assert hasattr(obs, "observation_type")
