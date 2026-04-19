# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for crystallization_types.py.

Verifies:
- PrescriptiveProfile: single-node ActivationPayload; on_enactment hooks
- EmergentTouchstone: ordered lineage walk (root-to-leaf); LookupError on
  broken lineage; staleness flagging
- FoundationalCommitment: on_enactment returns None; gate blocks/allows
  proposals correctly
- Factory: crystallization_from_record returns the right concrete type
"""
import pytest

from crystallization_schema import (
    ActivationConditions,
    ActivationFormat,
    ActivationScope,
    LearningLoopType,
    MechanismType,
    now_iso,
)
from crystallization_types import (
    ActivationPayload,
    EnactmentObservation,
    FoundationalCommitment,
    EmergentTouchstone,
    PrescriptiveProfile,
    ProposedChange,
    build_emergent_touchstone,
    build_foundational_commitment,
    build_prescriptive_profile,
    crystallization_from_record,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_profile(name="Test Profile", context_signals=None):
    return build_prescriptive_profile(
        name=name,
        recipe=f"Recipe for {name}.",
        stance_description=f"Stance for {name}.",
        context_signals=context_signals or ["test signal"],
    )


def _make_root_touchstone(tid="touchstone/01-root"):
    return build_emergent_touchstone(
        touchstone_id=tid,
        name=f"Touchstone {tid}",
        recipe="Root recipe.",
        stance_description="Root stance.",
        context_signals=["root signal"],
        lineage=[],
    )


def _make_leaf_touchstone(tid="touchstone/02-leaf", root_id="touchstone/01-root"):
    return build_emergent_touchstone(
        touchstone_id=tid,
        name=f"Touchstone {tid}",
        recipe="Leaf recipe.",
        stance_description="Leaf stance.",
        context_signals=["leaf signal"],
        lineage=[root_id],
    )


def _make_commitment(cid="foundational-commitment/test"):
    return build_foundational_commitment(
        commitment_id=cid,
        name="Test Commitment",
        recipe="Always-active recipe.",
    )


def _obs(crystallization_id, success, notes=None):
    return EnactmentObservation(
        crystallization_id=crystallization_id,
        observed_at=now_iso(),
        expected_configuration="target",
        success=success,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# PrescriptiveProfile
# ---------------------------------------------------------------------------


class TestPrescriptiveProfile:
    def test_resolve_activation_returns_single_node(self, substrate):
        profile = _make_profile()
        payload = profile.resolve_activation(substrate)
        assert isinstance(payload, ActivationPayload)
        assert len(payload.walk) == 1
        assert payload.walk[0].id == profile.id
        assert payload.mechanism_type == MechanismType.PRESCRIPTIVE_PROFILE

    def test_walk_node_recipe_matches_record(self, substrate):
        profile = _make_profile()
        payload = profile.resolve_activation(substrate)
        assert payload.walk[0].recipe == profile.record.recipe

    def test_on_enactment_success_returns_metadata_update(self):
        profile = _make_profile()
        change = profile.on_enactment_observed(_obs(profile.id, success=True))
        assert change is not None
        assert "last_verified_at" in change.field_updates
        assert change.field_updates.get("persistence_policy.last_test_result") == "passed"

    def test_on_enactment_failure_sets_staleness_and_failed(self):
        profile = _make_profile()
        change = profile.on_enactment_observed(
            _obs(profile.id, success=False, notes="Drift detected.")
        )
        assert change is not None
        assert change.field_updates.get("staleness_flag") is True
        assert change.field_updates.get("persistence_policy.last_test_result") == "failed"

    def test_validate_proposed_change_passes_by_default(self):
        profile = _make_profile()
        proposal = ProposedChange(
            crystallization_id=profile.id,
            proposed_by="instrument",
            proposed_at=now_iso(),
            rationale="Update staleness flag.",
            field_updates={"staleness_flag": True},
        )
        assert profile.validate_proposed_change(proposal) is None


# ---------------------------------------------------------------------------
# EmergentTouchstone — lineage walk
# ---------------------------------------------------------------------------


class TestEmergentTouchstoneLineageWalk:
    def test_root_touchstone_single_node_walk(self, substrate):
        root = _make_root_touchstone()
        substrate.save(root.record)
        payload = root.resolve_activation(substrate)
        assert len(payload.walk) == 1
        assert payload.walk[0].id == "touchstone/01-root"
        assert payload.walk[0].recipe == "Root recipe."

    def test_lineaged_touchstone_ordered_walk_root_first(self, substrate):
        root = _make_root_touchstone()
        leaf = _make_leaf_touchstone()
        substrate.save(root.record)
        substrate.save(leaf.record)
        payload = leaf.resolve_activation(substrate)
        assert len(payload.walk) == 2
        assert payload.walk[0].id == "touchstone/01-root"
        assert payload.walk[1].id == "touchstone/02-leaf"
        assert payload.walk[0].recipe == "Root recipe."
        assert payload.walk[1].recipe == "Leaf recipe."

    def test_three_deep_lineage_walk_fully_ordered(self, substrate):
        t1 = _make_root_touchstone("touchstone/01")
        t2 = build_emergent_touchstone(
            touchstone_id="touchstone/02",
            name="T2",
            recipe="T2 recipe.",
            stance_description="T2 stance.",
            context_signals=["t2"],
            lineage=["touchstone/01"],
        )
        t3 = build_emergent_touchstone(
            touchstone_id="touchstone/03",
            name="T3",
            recipe="T3 recipe.",
            stance_description="T3 stance.",
            context_signals=["t3"],
            lineage=["touchstone/01", "touchstone/02"],
        )
        for ts in (t1, t2, t3):
            substrate.save(ts.record)
        payload = t3.resolve_activation(substrate)
        ids = [n.id for n in payload.walk]
        assert ids == ["touchstone/01", "touchstone/02", "touchstone/03"]

    def test_missing_lineage_node_raises_lookup_error(self, substrate):
        leaf = _make_leaf_touchstone(root_id="touchstone/01-missing")
        substrate.save(leaf.record)
        # Root not saved — lineage is broken.
        with pytest.raises(LookupError, match="touchstone/01-missing"):
            leaf.resolve_activation(substrate)


class TestEmergentTouchstoneEnactment:
    def test_on_enactment_success_refreshes_verification(self):
        ts = _make_root_touchstone()
        change = ts.on_enactment_observed(_obs(ts.id, success=True))
        assert change is not None
        assert "last_verified_at" in change.field_updates

    def test_on_enactment_failure_flags_staleness(self):
        ts = _make_root_touchstone()
        change = ts.on_enactment_observed(
            _obs(ts.id, success=False, notes="Configuration diverged.")
        )
        assert change is not None
        assert change.field_updates.get("staleness_flag") is True

    def test_on_enactment_failure_note_preserved_in_reason(self):
        ts = _make_root_touchstone()
        change = ts.on_enactment_observed(
            _obs(ts.id, success=False, notes="Specific divergence note.")
        )
        assert change is not None
        staleness_reason = change.field_updates.get("staleness_reason", "")
        assert "Specific divergence note." in staleness_reason


# ---------------------------------------------------------------------------
# FoundationalCommitment — dual-job behavior
# ---------------------------------------------------------------------------


class TestFoundationalCommitment:
    def test_on_enactment_observed_always_returns_none(self):
        fc = _make_commitment()
        for success in (True, False):
            result = fc.on_enactment_observed(_obs(fc.id, success=success))
            assert result is None

    def test_resolve_activation_returns_single_node(self, substrate):
        fc = _make_commitment()
        payload = fc.resolve_activation(substrate)
        assert len(payload.walk) == 1
        assert payload.walk[0].recipe == "Always-active recipe."
        assert payload.mechanism_type == MechanismType.FOUNDATIONAL_COMMITMENT

    def test_validate_blocks_self_change_without_archive_flag(self):
        fc = _make_commitment()
        proposal = ProposedChange(
            crystallization_id=fc.id,
            proposed_by="instrument",
            proposed_at=now_iso(),
            rationale="Instrument-proposed change.",
            field_updates={"recipe": "New recipe."},
            archive_prior_version=False,
        )
        reason = fc.validate_proposed_change(proposal)
        assert reason is not None
        assert "archive" in reason.lower()

    def test_validate_blocks_non_collaborative_review_proposer(self):
        fc = _make_commitment()
        proposal = ProposedChange(
            crystallization_id=fc.id,
            proposed_by="instrument",  # not "collaborative-review"
            proposed_at=now_iso(),
            rationale="Instrument trying to modify FC.",
            field_updates={"recipe": "New recipe."},
            archive_prior_version=True,  # correct flag but wrong proposer
        )
        reason = fc.validate_proposed_change(proposal)
        assert reason is not None
        assert "collaborative-review" in reason

    def test_validate_allows_collaborative_review_with_archive(self):
        fc = _make_commitment()
        proposal = ProposedChange(
            crystallization_id=fc.id,
            proposed_by="collaborative-review",
            proposed_at=now_iso(),
            rationale="Collaborative session revision.",
            field_updates={"recipe": "Revised recipe."},
            archive_prior_version=True,
        )
        reason = fc.validate_proposed_change(proposal)
        assert reason is None

    def test_validate_passes_for_changes_to_other_crystallizations(self):
        fc = _make_commitment()
        proposal = ProposedChange(
            crystallization_id="prescriptive-profile/other",  # different target
            proposed_by="instrument",
            proposed_at=now_iso(),
            rationale="Update another crystallization.",
            field_updates={"staleness_flag": True},
        )
        reason = fc.validate_proposed_change(proposal)
        assert reason is None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class TestFactory:
    def test_prescriptive_profile_from_record(self):
        profile = _make_profile()
        result = crystallization_from_record(profile.record)
        assert isinstance(result, PrescriptiveProfile)

    def test_emergent_touchstone_from_record(self):
        ts = _make_root_touchstone()
        result = crystallization_from_record(ts.record)
        assert isinstance(result, EmergentTouchstone)

    def test_foundational_commitment_from_record(self):
        fc = _make_commitment()
        result = crystallization_from_record(fc.record)
        assert isinstance(result, FoundationalCommitment)
