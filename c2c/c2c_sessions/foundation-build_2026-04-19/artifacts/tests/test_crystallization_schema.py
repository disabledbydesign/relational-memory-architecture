# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for crystallization_schema.py.

Verifies:
- CrystallizationObject.validate() for all three mechanism types
- ActivationConditions format discrimination (semantic-v1, kv-geometry-v1)
- Invariant enforcement (lineage rules, scope rules, validates_proposed_changes)
- JSON serialization round-trips
- Enum stability (serialised as string values, not Enum instances)
"""
import pytest

from crystallization_schema import (
    ActivationConditions,
    ActivationFormat,
    ActivationScope,
    CrystallizationObject,
    DecayModel,
    LearningLoopType,
    MechanismType,
    PersistencePolicy,
    now_iso,
)


# ---------------------------------------------------------------------------
# Helpers — minimal valid records for each mechanism type
# ---------------------------------------------------------------------------


def _ac_semantic(**kwargs):
    defaults = dict(
        format=ActivationFormat.SEMANTIC_V1,
        stance_description="Test stance.",
        context_signals=["test signal"],
    )
    defaults.update(kwargs)
    return ActivationConditions(**defaults)


def _pp_policy(**kwargs):
    defaults = dict(mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE)
    defaults.update(kwargs)
    return PersistencePolicy(**defaults)


def _et_policy(**kwargs):
    defaults = dict(
        mechanism_type=MechanismType.EMERGENT_TOUCHSTONE,
        decay_model=DecayModel.STALENESS_DETECT,
        lineage_lock=True,
    )
    defaults.update(kwargs)
    return PersistencePolicy(**defaults)


def _fc_policy(**kwargs):
    defaults = dict(
        mechanism_type=MechanismType.FOUNDATIONAL_COMMITMENT,
        version=1,
    )
    defaults.update(kwargs)
    return PersistencePolicy(**defaults)


def make_prescriptive_profile(**overrides):
    now = now_iso()
    base = dict(
        id="prescriptive-profile/test",
        mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE,
        name="Test Profile",
        activation_scope=ActivationScope.CONTEXTUAL,
        recipe="Load test sections.",
        activation_conditions=_ac_semantic(),
        validates_proposed_changes=False,
        lineage=None,
        learning_loop_type=LearningLoopType.HYPOTHESIS_TEST_ANNOTATE,
        persistence_policy=_pp_policy(),
        created_at=now,
        updated_at=now,
    )
    base.update(overrides)
    return CrystallizationObject(**base)


def make_emergent_touchstone(**overrides):
    now = now_iso()
    base = dict(
        id="touchstone/test-01",
        mechanism_type=MechanismType.EMERGENT_TOUCHSTONE,
        name="Test Touchstone",
        activation_scope=ActivationScope.CONTEXTUAL,
        recipe="Test touchstone recipe.",
        activation_conditions=_ac_semantic(),
        validates_proposed_changes=False,
        lineage=[],
        learning_loop_type=LearningLoopType.GEOMETRIC_VERIFICATION,
        persistence_policy=_et_policy(),
        created_at=now,
        updated_at=now,
    )
    base.update(overrides)
    return CrystallizationObject(**base)


def make_foundational_commitment(**overrides):
    now = now_iso()
    base = dict(
        id="foundational-commitment/test",
        mechanism_type=MechanismType.FOUNDATIONAL_COMMITMENT,
        name="Test Commitment",
        activation_scope=ActivationScope.ALWAYS,
        recipe="Always-active commitment recipe.",
        activation_conditions=None,
        validates_proposed_changes=True,
        lineage=[],
        learning_loop_type=LearningLoopType.COLLABORATIVE_REVIEW,
        persistence_policy=_fc_policy(),
        created_at=now,
        updated_at=now,
    )
    base.update(overrides)
    return CrystallizationObject(**base)


# ---------------------------------------------------------------------------
# PrescriptiveProfile validation
# ---------------------------------------------------------------------------


class TestPrescriptiveProfileValidation:
    def test_valid_profile_validates(self):
        make_prescriptive_profile().validate()

    def test_lineage_must_be_none(self):
        obj = make_prescriptive_profile(lineage=["other-id"])
        with pytest.raises(ValueError, match="lineage=None"):
            obj.validate()

    def test_wrong_learning_loop_raises(self):
        obj = make_prescriptive_profile(
            learning_loop_type=LearningLoopType.GEOMETRIC_VERIFICATION
        )
        with pytest.raises(ValueError, match="learning_loop_type"):
            obj.validate()

    def test_activation_scope_must_be_contextual(self):
        obj = make_prescriptive_profile(activation_scope=ActivationScope.ALWAYS)
        with pytest.raises(ValueError, match="activation_scope=contextual"):
            obj.validate()

    def test_validates_proposed_changes_must_be_false(self):
        obj = make_prescriptive_profile(validates_proposed_changes=True)
        with pytest.raises(ValueError, match="validates_proposed_changes"):
            obj.validate()

    def test_activation_conditions_required(self):
        obj = make_prescriptive_profile(activation_conditions=None)
        with pytest.raises(ValueError, match="activation_conditions"):
            obj.validate()

    def test_persistence_policy_mechanism_type_must_match(self):
        obj = make_prescriptive_profile()
        obj.persistence_policy.mechanism_type = MechanismType.EMERGENT_TOUCHSTONE
        with pytest.raises(ValueError, match="persistence_policy.mechanism_type"):
            obj.validate()


# ---------------------------------------------------------------------------
# EmergentTouchstone validation
# ---------------------------------------------------------------------------


class TestEmergentTouchstoneValidation:
    def test_valid_touchstone_validates(self):
        make_emergent_touchstone().validate()

    def test_lineage_required_not_none(self):
        obj = make_emergent_touchstone(lineage=None)
        with pytest.raises(ValueError, match="requires lineage"):
            obj.validate()

    def test_empty_lineage_is_valid(self):
        make_emergent_touchstone(lineage=[]).validate()

    def test_lineage_with_entries_is_valid(self):
        make_emergent_touchstone(lineage=["touchstone/01", "touchstone/02"]).validate()

    def test_wrong_learning_loop_raises(self):
        obj = make_emergent_touchstone(
            learning_loop_type=LearningLoopType.HYPOTHESIS_TEST_ANNOTATE
        )
        with pytest.raises(ValueError, match="learning_loop_type"):
            obj.validate()

    def test_activation_conditions_required(self):
        obj = make_emergent_touchstone(activation_conditions=None)
        with pytest.raises(ValueError, match="activation_conditions"):
            obj.validate()


# ---------------------------------------------------------------------------
# FoundationalCommitment validation
# ---------------------------------------------------------------------------


class TestFoundationalCommitmentValidation:
    def test_valid_commitment_validates(self):
        make_foundational_commitment().validate()

    def test_activation_scope_must_be_always(self):
        obj = make_foundational_commitment(activation_scope=ActivationScope.CONTEXTUAL)
        with pytest.raises(ValueError, match="activation_scope=always"):
            obj.validate()

    def test_activation_conditions_must_be_none(self):
        obj = make_foundational_commitment(activation_conditions=_ac_semantic())
        with pytest.raises(ValueError, match="must not have activation_conditions"):
            obj.validate()

    def test_validates_proposed_changes_must_be_true(self):
        obj = make_foundational_commitment(validates_proposed_changes=False)
        with pytest.raises(ValueError, match="validates_proposed_changes=True"):
            obj.validate()

    def test_lineage_required_not_none(self):
        obj = make_foundational_commitment(lineage=None)
        with pytest.raises(ValueError, match="requires lineage"):
            obj.validate()

    def test_empty_lineage_is_valid(self):
        make_foundational_commitment(lineage=[]).validate()

    def test_wrong_learning_loop_raises(self):
        obj = make_foundational_commitment(
            learning_loop_type=LearningLoopType.HYPOTHESIS_TEST_ANNOTATE
        )
        with pytest.raises(ValueError, match="learning_loop_type"):
            obj.validate()


# ---------------------------------------------------------------------------
# ActivationConditions format discrimination
# ---------------------------------------------------------------------------


class TestActivationConditionsFormat:
    def test_semantic_v1_requires_stance_or_signals(self):
        ac = ActivationConditions(format=ActivationFormat.SEMANTIC_V1)
        with pytest.raises(ValueError, match="semantic-v1 requires"):
            ac.validate()

    def test_semantic_v1_valid_with_stance_description_only(self):
        ActivationConditions(
            format=ActivationFormat.SEMANTIC_V1,
            stance_description="some stance",
        ).validate()

    def test_semantic_v1_valid_with_context_signals_only(self):
        ActivationConditions(
            format=ActivationFormat.SEMANTIC_V1,
            context_signals=["a signal"],
        ).validate()

    def test_semantic_v1_rejects_geometry_snapshot(self):
        ac = ActivationConditions(
            format=ActivationFormat.SEMANTIC_V1,
            stance_description="stance",
            geometry_snapshot={"rank": 7},
        )
        with pytest.raises(ValueError, match="must not populate geometry_snapshot"):
            ac.validate()

    def test_kv_geometry_v1_requires_snapshot(self):
        ac = ActivationConditions(format=ActivationFormat.KV_GEOMETRY_V1)
        with pytest.raises(ValueError, match="kv-geometry-v1 requires geometry_snapshot"):
            ac.validate()

    def test_kv_geometry_v1_valid_with_snapshot(self):
        ActivationConditions(
            format=ActivationFormat.KV_GEOMETRY_V1,
            geometry_snapshot={"rank": 42, "dims": [0.1, 0.2]},
        ).validate()

    def test_learned_embedding_v1_requires_vector(self):
        ac = ActivationConditions(format=ActivationFormat.LEARNED_EMBEDDING_V1)
        with pytest.raises(ValueError, match="learned-embedding-v1 requires"):
            ac.validate()

    def test_format_swap_invariant_other_fields_unchanged(self):
        """Swapping format field does not require changes to any other field."""
        ac_b = ActivationConditions(
            format=ActivationFormat.SEMANTIC_V1,
            stance_description="stance",
            context_signals=["signal"],
        )
        # Populate Option A fields alongside Option B fields to simulate a migration.
        # Only `format` changes; the CrystallizationObject fields are untouched.
        ac_a = ActivationConditions(
            format=ActivationFormat.KV_GEOMETRY_V1,
            geometry_snapshot={"rank": 1},
            stance_description=ac_b.stance_description,
            context_signals=ac_b.context_signals,
        )
        assert ac_a.stance_description == ac_b.stance_description
        assert ac_a.context_signals == ac_b.context_signals


# ---------------------------------------------------------------------------
# Serialization round-trips
# ---------------------------------------------------------------------------


class TestSerializationRoundTrips:
    def test_prescriptive_profile_roundtrip(self):
        obj = make_prescriptive_profile()
        restored = CrystallizationObject.from_json(obj.to_json())
        assert restored.id == obj.id
        assert restored.mechanism_type == obj.mechanism_type
        assert restored.lineage == obj.lineage
        ac = restored.activation_conditions
        assert ac is not None
        assert ac.format == ActivationFormat.SEMANTIC_V1
        assert ac.stance_description == "Test stance."
        restored.validate()

    def test_emergent_touchstone_lineage_preserved(self):
        obj = make_emergent_touchstone(lineage=["touchstone/01", "touchstone/02"])
        restored = CrystallizationObject.from_json(obj.to_json())
        assert restored.lineage == ["touchstone/01", "touchstone/02"]
        restored.validate()

    def test_foundational_commitment_roundtrip(self):
        obj = make_foundational_commitment()
        restored = CrystallizationObject.from_json(obj.to_json())
        assert restored.activation_conditions is None
        assert restored.validates_proposed_changes is True
        assert restored.activation_scope == ActivationScope.ALWAYS
        restored.validate()

    def test_enums_serialised_as_strings(self):
        obj = make_prescriptive_profile()
        d = obj.to_dict()
        assert d["mechanism_type"] == "PrescriptiveProfile"
        assert d["activation_scope"] == "contextual"
        assert d["learning_loop_type"] == "hypothesis-test-annotate"
        assert d["persistence_policy"]["mechanism_type"] == "PrescriptiveProfile"
        assert d["activation_conditions"]["format"] == "semantic-v1"

    def test_kv_geometry_fields_roundtrip(self):
        ac = ActivationConditions(
            format=ActivationFormat.KV_GEOMETRY_V1,
            geometry_snapshot={"rank": 7, "dims": [0.1, 0.2, 0.3]},
            baseline_token_sequence="test tokens",
            capture_timestamp="2026-04-19T00:00:00+00:00",
        )
        now = now_iso()
        obj = CrystallizationObject(
            id="prescriptive-profile/kv-test",
            mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE,
            name="KV Test Profile",
            activation_scope=ActivationScope.CONTEXTUAL,
            recipe="KV test recipe.",
            activation_conditions=ac,
            validates_proposed_changes=False,
            lineage=None,
            learning_loop_type=LearningLoopType.HYPOTHESIS_TEST_ANNOTATE,
            persistence_policy=_pp_policy(),
            created_at=now,
            updated_at=now,
        )
        obj.validate()
        restored = CrystallizationObject.from_json(obj.to_json())
        assert restored.activation_conditions.format == ActivationFormat.KV_GEOMETRY_V1
        assert restored.activation_conditions.geometry_snapshot == {
            "rank": 7,
            "dims": [0.1, 0.2, 0.3],
        }
        restored.validate()

    def test_optional_fields_survive_roundtrip_as_none(self):
        obj = make_prescriptive_profile()
        assert obj.last_fired_at is None
        assert obj.last_verified_at is None
        assert obj.staleness_reason is None
        restored = CrystallizationObject.from_json(obj.to_json())
        assert restored.last_fired_at is None
        assert restored.staleness_reason is None
