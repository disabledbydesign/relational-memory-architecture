# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for substrate_interface.py (LocalFileSubstrate).

Verifies:
- save/load/exists round-trips
- list_ids scope and mechanism-type filters
- referrers_of: downstream touchstones returned; empty when not referenced
- archive: removes from active; raises SubstrateError on missing;
  raises LineageLockViolation when lineage_lock referrers exist;
  succeeds when no referrers
- archive_prior_version: first write saves without prior; second write
  archives prior and records id in prior_versions; rejects non-FC
"""
import pytest

from crystallization_schema import ActivationScope, MechanismType
from crystallization_types import (
    build_emergent_touchstone,
    build_foundational_commitment,
    build_prescriptive_profile,
)
from substrate_interface import LineageLockViolation, LocalFileSubstrate, SubstrateError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _profile(name, pid=None, signals=None):
    return build_prescriptive_profile(
        profile_id=pid or f"prescriptive-profile/{name.lower().replace(' ', '-')}",
        name=name,
        recipe=f"Recipe for {name}.",
        stance_description=f"Stance for {name}.",
        context_signals=signals or ["signal"],
    )


def _touchstone(tid, lineage=None):
    return build_emergent_touchstone(
        touchstone_id=tid,
        name=f"Touchstone {tid}",
        recipe=f"Recipe for {tid}.",
        stance_description="Stance.",
        context_signals=["ts signal"],
        lineage=lineage or [],
    )


def _commitment(cid="foundational-commitment/test", version=1, prior_versions=None):
    return build_foundational_commitment(
        commitment_id=cid,
        name="Test Commitment",
        recipe="Always-active recipe.",
        version=version,
        prior_versions=prior_versions,
    )


# ---------------------------------------------------------------------------
# Save / load / exists
# ---------------------------------------------------------------------------


class TestSaveLoad:
    def test_save_and_load_roundtrip(self, substrate):
        profile = _profile("Alpha")
        substrate.save(profile.record)
        loaded = substrate.load(profile.id)
        assert loaded is not None
        assert loaded.id == profile.id
        assert loaded.recipe == profile.record.recipe

    def test_load_returns_none_for_missing(self, substrate):
        assert substrate.load("prescriptive-profile/does-not-exist") is None

    def test_exists_true_after_save(self, substrate):
        profile = _profile("Beta")
        substrate.save(profile.record)
        assert substrate.exists(profile.id) is True

    def test_exists_false_before_save(self, substrate):
        assert substrate.exists("prescriptive-profile/never-saved") is False

    def test_overwrite_updates_record(self, substrate):
        import time
        from crystallization_schema import now_iso

        profile = _profile("Gamma", pid="prescriptive-profile/gamma")
        substrate.save(profile.record)

        # Build a second profile at the same id with different recipe
        updated = build_prescriptive_profile(
            profile_id="prescriptive-profile/gamma",
            name="Gamma",
            recipe="Updated recipe.",
            stance_description="Stance.",
            context_signals=["signal"],
        )
        substrate.save(updated.record)

        loaded = substrate.load("prescriptive-profile/gamma")
        assert loaded is not None
        assert loaded.recipe == "Updated recipe."

    def test_save_validates_record(self, substrate):
        from crystallization_schema import (
            ActivationConditions,
            ActivationFormat,
            ActivationScope,
            CrystallizationObject,
            LearningLoopType,
            MechanismType,
            PersistencePolicy,
            now_iso,
        )
        now = now_iso()
        bad = CrystallizationObject(
            id="prescriptive-profile/bad",
            mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE,
            name="Bad",
            activation_scope=ActivationScope.ALWAYS,   # wrong for prescriptive profile
            recipe="Recipe.",
            activation_conditions=ActivationConditions(
                format=ActivationFormat.SEMANTIC_V1,
                stance_description="stance",
            ),
            validates_proposed_changes=False,
            lineage=None,
            learning_loop_type=LearningLoopType.HYPOTHESIS_TEST_ANNOTATE,
            persistence_policy=PersistencePolicy(
                mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE
            ),
            created_at=now,
            updated_at=now,
        )
        with pytest.raises(ValueError):
            substrate.save(bad)


# ---------------------------------------------------------------------------
# list_ids filters
# ---------------------------------------------------------------------------


class TestListIds:
    def test_list_all_ids(self, substrate):
        p1 = _profile("P1")
        p2 = _profile("P2")
        fc = _commitment()
        substrate.save(p1.record)
        substrate.save(p2.record)
        substrate.save(fc.record)
        ids = substrate.list_ids()
        assert p1.id in ids
        assert p2.id in ids
        assert fc.id in ids

    def test_list_contextual_scope(self, substrate):
        profile = _profile("Contextual")
        fc = _commitment()
        substrate.save(profile.record)
        substrate.save(fc.record)
        ids = substrate.list_ids(scope=ActivationScope.CONTEXTUAL)
        assert profile.id in ids
        assert fc.id not in ids

    def test_list_always_scope(self, substrate):
        profile = _profile("Contextual")
        fc = _commitment()
        substrate.save(profile.record)
        substrate.save(fc.record)
        ids = substrate.list_ids(scope=ActivationScope.ALWAYS)
        assert fc.id in ids
        assert profile.id not in ids

    def test_list_by_mechanism_type_emergent_touchstone(self, substrate):
        profile = _profile("Profile")
        ts = _touchstone("touchstone/filter-test")
        substrate.save(profile.record)
        substrate.save(ts.record)
        ids = substrate.list_ids(mechanism_type=MechanismType.EMERGENT_TOUCHSTONE)
        assert ts.id in ids
        assert profile.id not in ids

    def test_list_by_mechanism_type_prescriptive_profile(self, substrate):
        profile = _profile("Profile Only")
        ts = _touchstone("touchstone/ts-only")
        substrate.save(profile.record)
        substrate.save(ts.record)
        ids = substrate.list_ids(mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE)
        assert profile.id in ids
        assert ts.id not in ids

    def test_empty_substrate_returns_empty(self, substrate):
        assert substrate.list_ids() == []


# ---------------------------------------------------------------------------
# referrers_of
# ---------------------------------------------------------------------------


class TestReferrersOf:
    def test_referrers_of_returns_lineage_descendants(self, substrate):
        root = _touchstone("touchstone/root")
        leaf = _touchstone("touchstone/leaf", lineage=["touchstone/root"])
        substrate.save(root.record)
        substrate.save(leaf.record)
        referrers = substrate.referrers_of("touchstone/root")
        assert "touchstone/leaf" in referrers

    def test_referrers_of_unreferenced_returns_empty(self, substrate):
        profile = _profile("Isolated")
        substrate.save(profile.record)
        assert substrate.referrers_of(profile.id) == []

    def test_referrers_of_missing_id_returns_empty(self, substrate):
        assert substrate.referrers_of("touchstone/nonexistent") == []

    def test_referrers_of_with_multi_level_lineage(self, substrate):
        t1 = _touchstone("touchstone/01")
        t2 = _touchstone("touchstone/02", lineage=["touchstone/01"])
        t3 = _touchstone("touchstone/03", lineage=["touchstone/01", "touchstone/02"])
        substrate.save(t1.record)
        substrate.save(t2.record)
        substrate.save(t3.record)
        referrers = substrate.referrers_of("touchstone/01")
        assert "touchstone/02" in referrers
        assert "touchstone/03" in referrers


# ---------------------------------------------------------------------------
# archive
# ---------------------------------------------------------------------------


class TestArchive:
    def test_archive_removes_from_active(self, substrate):
        ts = _touchstone("touchstone/to-archive")
        substrate.save(ts.record)
        substrate.archive("touchstone/to-archive")
        assert substrate.exists("touchstone/to-archive") is False
        assert substrate.load("touchstone/to-archive") is None

    def test_archive_raises_on_missing(self, substrate):
        with pytest.raises(SubstrateError):
            substrate.archive("touchstone/does-not-exist")

    def test_archive_raises_lineage_lock_when_referenced(self, substrate):
        root = _touchstone("touchstone/locked-root")
        leaf = _touchstone("touchstone/locked-leaf", lineage=["touchstone/locked-root"])
        substrate.save(root.record)
        substrate.save(leaf.record)
        with pytest.raises(LineageLockViolation, match="touchstone/locked-root"):
            substrate.archive("touchstone/locked-root")

    def test_archive_allowed_for_leaf_with_no_referrers(self, substrate):
        root = _touchstone("touchstone/ar-root")
        leaf = _touchstone("touchstone/ar-leaf", lineage=["touchstone/ar-root"])
        substrate.save(root.record)
        substrate.save(leaf.record)
        # Archiving the leaf (nobody references it) should succeed
        archive_id = substrate.archive("touchstone/ar-leaf")
        assert archive_id != ""
        assert substrate.exists("touchstone/ar-leaf") is False

    def test_archive_allowed_when_no_referrers(self, substrate):
        ts = _touchstone("touchstone/solo")
        substrate.save(ts.record)
        archive_id = substrate.archive("touchstone/solo")
        assert "touchstone/solo" in archive_id

    def test_archive_profile_does_not_check_lineage_lock(self, substrate):
        profile = _profile("Archivable Profile", pid="prescriptive-profile/arch")
        substrate.save(profile.record)
        archive_id = substrate.archive(profile.id)
        assert archive_id != ""


# ---------------------------------------------------------------------------
# archive_prior_version
# ---------------------------------------------------------------------------


class TestArchivePriorVersion:
    def test_first_write_saves_without_archive(self, substrate):
        fc = _commitment(cid="foundational-commitment/first")
        archive_id = substrate.archive_prior_version(fc.id, new_version=fc.record)
        assert archive_id == ""
        assert substrate.exists(fc.id) is True

    def test_second_write_archives_prior_version(self, substrate):
        fc_v1 = _commitment(cid="foundational-commitment/evolving", version=1)
        substrate.archive_prior_version(fc_v1.id, new_version=fc_v1.record)

        fc_v2 = _commitment(cid="foundational-commitment/evolving", version=2)
        archive_id = substrate.archive_prior_version(fc_v2.id, new_version=fc_v2.record)

        assert archive_id != ""
        assert "foundational-commitment/evolving" in archive_id

    def test_prior_version_id_recorded_in_new_record(self, substrate):
        fc_v1 = _commitment(cid="foundational-commitment/tracked", version=1)
        substrate.archive_prior_version(fc_v1.id, new_version=fc_v1.record)

        fc_v2 = _commitment(cid="foundational-commitment/tracked", version=2)
        archive_id = substrate.archive_prior_version(fc_v2.id, new_version=fc_v2.record)

        loaded = substrate.load("foundational-commitment/tracked")
        assert loaded is not None
        assert archive_id in loaded.persistence_policy.prior_versions

    def test_rejects_non_foundational_commitment(self, substrate):
        profile = _profile("Invalid For APV", pid="prescriptive-profile/apv-reject")
        with pytest.raises(SubstrateError, match="FoundationalCommitment"):
            substrate.archive_prior_version(
                profile.id, new_version=profile.record
            )

    def test_rejects_mismatched_id(self, substrate):
        fc_a = _commitment(cid="foundational-commitment/a")
        fc_b = _commitment(cid="foundational-commitment/b")
        with pytest.raises(SubstrateError, match="must match"):
            substrate.archive_prior_version("foundational-commitment/a", new_version=fc_b.record)
