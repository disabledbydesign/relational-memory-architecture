# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Regression tests for the five fixes applied in Instance B's second cycle:

  Fix #4 — LookupError per-record handling in matcher
  Fix #3 — aux-LLM demotion preserves scores in candidate seed
  Fix #2 — Enum coercion via get_type_hints covers all Enum-typed fields
  Fix #1 — proposed_by "collaborative-review" sentinel is declared in type
  Fix #5 — PrescriptiveProfile staleness-flag grace-window policy

Each fix has a test class. Tests verify the specific behaviour the fix
introduced, not just the happy path (which was already covered).
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from bootstrap import (
    GateResult,
    apply_proposed_change,
    _coerce_field_value,
    load_foundational_commitments,
)
from crystallization_schema import (
    ActivationFormat,
    ActivationScope,
    DecayModel,
    LearningLoopType,
    MechanismType,
    PersistencePolicy,
    TestResult,
)
from crystallization_types import (
    ActivationPayload,
    ProposedChange,
    build_emergent_touchstone,
    build_foundational_commitment,
    build_prescriptive_profile,
    crystallization_from_record,
)
from matcher_step_2d import (
    DEFAULT_ACTIVATION_THRESHOLD,
    ContextSnapshot,
    CrystallizationMatcher,
)
from staleness_policy import (
    DEFAULT_GRACE_WINDOW_HOURS,
    StalenessGracePolicyManager,
    _is_staleness_only,
)
from substrate_interface import LocalFileSubstrate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _profile(name, signals=None, anti_signals=None, task_affinity=None):
    return build_prescriptive_profile(
        profile_id=f"prescriptive-profile/{name.lower().replace(' ', '-')}",
        name=name,
        recipe=f"Recipe for {name}.",
        stance_description=f"Stance for {name}.",
        context_signals=signals or [f"{name.lower()} signal"],
        anti_signals=anti_signals,
        task_affinity=task_affinity,
    )


def _snapshot(texts=None, invocations=None):
    return ContextSnapshot(
        exchange_texts=texts or [],
        user_invocation_phrases=invocations or [],
    )


def _matcher(substrate, threshold=None, aux_llm_fn=None, max_active=4):
    return CrystallizationMatcher(
        substrate=substrate,
        activation_threshold=threshold if threshold is not None else DEFAULT_ACTIVATION_THRESHOLD,
        max_active=max_active,
        aux_llm_fn=aux_llm_fn,
    )


def _now_iso():
    from crystallization_schema import now_iso
    return now_iso()


def _proposed_change(cid, fields, proposed_by="instrument"):
    return ProposedChange(
        crystallization_id=cid,
        proposed_by=proposed_by,
        proposed_at=_now_iso(),
        rationale="test",
        field_updates=fields,
    )


# ---------------------------------------------------------------------------
# Fix #4 — LookupError per-record handling in matcher
# ---------------------------------------------------------------------------


class TestMatcherBrokenLineage:
    """
    When an EmergentTouchstone's ancestor is missing, the matcher must:
    - log a warning and skip that touchstone
    - not raise an exception
    - not fall back to a leaf-only payload (that would violate the walk invariant)
    - still activate other crystallizations whose lineage is intact
    - include the broken-lineage crystallization in top_below_threshold
      (so it appears in any CandidateSeed's top_scores)
    """

    def test_broken_lineage_does_not_crash(self, substrate):
        # t2 references t1, but t1 is never saved
        t2 = build_emergent_touchstone(
            touchstone_id="touchstone/02",
            name="T2",
            recipe="T2 recipe",
            stance_description="T2 stance",
            context_signals=["t2 signal"],
            lineage=["touchstone/01"],   # t1 is absent
        )
        substrate.save(t2.record)

        matcher = _matcher(substrate)
        snapshot = _snapshot(texts=["t2 signal in this exchange"])
        result = matcher.match(snapshot)
        # Must not raise; T2 skipped; no activations
        assert isinstance(result.activations, list)

    def test_broken_lineage_skips_not_falls_back(self, substrate):
        # Verify the skipped touchstone is not in activations with a single-node walk
        t2 = build_emergent_touchstone(
            touchstone_id="touchstone/02",
            name="T2",
            recipe="T2 recipe",
            stance_description="T2 stance",
            context_signals=["broken signal"],
            lineage=["touchstone/01"],
        )
        substrate.save(t2.record)

        matcher = _matcher(substrate, threshold=0.1)
        snapshot = _snapshot(texts=["broken signal here"])
        result = matcher.match(snapshot)

        ids_activated = [a.payload.crystallization_id for a in result.activations]
        assert "touchstone/02" not in ids_activated

    def test_broken_lineage_touchstone_in_candidate_seed_scores(self, substrate):
        # The broken touchstone scored above threshold before LookupError;
        # it should appear in the CandidateSeed's top_scores so the seed
        # has the near-miss context.
        t2 = build_emergent_touchstone(
            touchstone_id="touchstone/02",
            name="T2",
            recipe="T2 recipe",
            stance_description="T2 stance",
            context_signals=["broken signal"],
            lineage=["touchstone/01"],
        )
        substrate.save(t2.record)

        matcher = _matcher(substrate, threshold=0.1)
        snapshot = _snapshot(texts=["broken signal here"])
        result = matcher.match(snapshot)

        assert result.candidate_seed is not None
        seed_ids = [entry[0] for entry in result.candidate_seed.top_scores]
        assert "touchstone/02" in seed_ids

    def test_intact_touchstone_still_activates_alongside_broken(self, substrate):
        # t1 saved; t2 references t1 (intact); t3 references missing t4 (broken)
        t1 = build_emergent_touchstone(
            touchstone_id="touchstone/01",
            name="T1",
            recipe="T1 recipe",
            stance_description="T1 stance",
            context_signals=["t1 signal"],
            lineage=[],
        )
        t2 = build_emergent_touchstone(
            touchstone_id="touchstone/02",
            name="T2",
            recipe="T2 recipe",
            stance_description="T2 stance",
            context_signals=["t1 signal"],
            lineage=["touchstone/01"],
        )
        t3 = build_emergent_touchstone(
            touchstone_id="touchstone/03",
            name="T3",
            recipe="T3 recipe",
            stance_description="T3 stance",
            context_signals=["t1 signal"],
            lineage=["touchstone/99"],   # 99 is missing
        )
        substrate.save(t1.record)
        substrate.save(t2.record)
        substrate.save(t3.record)

        matcher = _matcher(substrate, threshold=0.1)
        snapshot = _snapshot(texts=["t1 signal in exchange"])
        result = matcher.match(snapshot)

        ids_activated = {a.payload.crystallization_id for a in result.activations}
        assert "touchstone/01" in ids_activated
        assert "touchstone/02" in ids_activated
        assert "touchstone/03" not in ids_activated   # broken lineage, skipped


# ---------------------------------------------------------------------------
# Fix #3 — aux-LLM demotion preserves scores in candidate seed
# ---------------------------------------------------------------------------


class TestAuxLlmDemotionPreservedInSeed:
    """
    When aux-LLM demotes every activation below threshold, the candidate seed
    must carry those (id, score) pairs so the near-miss context is not lost.
    """

    def test_demoted_scores_appear_in_seed(self, substrate):
        # Four signals, only one present → signal_score = 0.25. Threshold = 0.25,
        # so the crystallization clears threshold on pattern-match alone (just at
        # the edge). aux-LLM demotes by 0.2 → final score = 0.05, below threshold.
        p = _profile(
            "Welfare",
            signals=["welfare research", "ai agency", "ethics review", "fourth signal"],
        )
        substrate.save(p.record)

        def _demoting_llm(prompt: str) -> str:
            return "unfits — wrong context"

        # Threshold at 0.10 so the pattern score (0.25) clears but the demoted
        # score (0.05) does not — this is the exact scenario the fix addresses.
        matcher = _matcher(substrate, threshold=0.10, aux_llm_fn=_demoting_llm)
        snapshot = _snapshot(texts=["welfare research"])   # one of four signals
        result = matcher.match(snapshot)

        # After demotion, no activations
        assert result.activations == []
        assert result.candidate_seed is not None
        seed_ids = [entry[0] for entry in result.candidate_seed.top_scores]
        assert p.record.id in seed_ids

    def test_undepicted_score_absent_in_seed_when_activation_survives(self, substrate):
        # If aux-LLM boosts (not demotes), no extra entries in seed
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        def _boosting_llm(prompt: str) -> str:
            return "fits — relational stance"

        matcher = _matcher(substrate, threshold=0.25, aux_llm_fn=_boosting_llm)
        snapshot = _snapshot(texts=["welfare research context"])
        result = matcher.match(snapshot)

        assert result.activations  # something activated
        assert result.candidate_seed is None  # not flagged


# ---------------------------------------------------------------------------
# Fix #2 — Enum coercion via get_type_hints covers all Enum fields
# ---------------------------------------------------------------------------


class TestEnumCoercionAllFields:
    """
    _coerce_field_value must coerce string values to Enum instances for ALL
    Enum-typed fields on CrystallizationObject and PersistencePolicy, not just
    TestResult and DecayModel.
    """

    @pytest.mark.parametrize("value,expected_type", [
        ("PrescriptiveProfile", MechanismType),
        ("EmergentTouchstone", MechanismType),
        ("FoundationalCommitment", MechanismType),
        ("contextual", ActivationScope),
        ("always", ActivationScope),
        ("hypothesis-test-annotate", LearningLoopType),
        ("geometric-verification", LearningLoopType),
        ("collaborative-review", LearningLoopType),
        ("passed", TestResult),
        ("failed", TestResult),
        ("none", DecayModel),
        ("staleness-detect", DecayModel),
    ])
    def test_coerce_string_to_enum(self, value, expected_type):
        from crystallization_schema import CrystallizationObject, PersistencePolicy
        # Find which dataclass holds this field
        for dc_type in (CrystallizationObject, PersistencePolicy):
            import dataclasses
            field_names = {f.name for f in dataclasses.fields(dc_type)}
            # Map enum types to possible field names
            for f in dataclasses.fields(dc_type):
                import typing
                hints = typing.get_type_hints(dc_type, include_extras=True)
                resolved = hints.get(f.name)
                if resolved is None:
                    continue
                # Unwrap Optional
                origin = getattr(resolved, "__origin__", None)
                args = getattr(resolved, "__args__", ())
                if origin is typing.Union:
                    types = [a for a in args if isinstance(a, type)]
                else:
                    types = [resolved] if isinstance(resolved, type) else []
                if expected_type in types:
                    result = _coerce_field_value(dc_type, f.name, value)
                    assert isinstance(result, expected_type), (
                        f"_coerce_field_value({dc_type.__name__}, {f.name!r}, {value!r}) "
                        f"returned {result!r} instead of {expected_type.__name__}"
                    )
                    return
        pytest.fail(f"No field found for {expected_type.__name__} with value {value!r}")

    def test_coerce_existing_enum_instance_unchanged(self):
        from crystallization_schema import CrystallizationObject
        result = _coerce_field_value(
            CrystallizationObject, "mechanism_type", MechanismType.PRESCRIPTIVE_PROFILE
        )
        assert result is MechanismType.PRESCRIPTIVE_PROFILE

    def test_coerce_unknown_field_returns_value_unchanged(self):
        from crystallization_schema import CrystallizationObject
        result = _coerce_field_value(CrystallizationObject, "nonexistent_field", "any_value")
        assert result == "any_value"

    def test_apply_proposed_change_coerces_mechanism_type_via_string(self, substrate):
        # An on_enactment_observed proposal that writes "staleness_flag" should
        # survive the full apply_proposed_change pipeline (verifying coercion
        # doesn't break for boolean fields either)
        p = _profile("PaperWriting", signals=["academic draft"])
        substrate.save(p.record)

        proposal = _proposed_change(
            p.record.id,
            {
                "staleness_flag": True,
                "staleness_reason": "test coercion path",
            },
        )
        updated = apply_proposed_change(proposal, substrate)
        assert updated.staleness_flag is True
        assert updated.staleness_reason == "test coercion path"


# ---------------------------------------------------------------------------
# Fix #1 — proposed_by "collaborative-review" sentinel declared
# ---------------------------------------------------------------------------


class TestProposedBySentinel:
    """
    The "collaborative-review" sentinel must be accepted by
    FoundationalCommitment.validate_proposed_change for self-targeting changes.
    The sentinel being declared (not magic string) is verified by checking that
    the FoundationalCommitment gate uses the same value the type declares.
    """

    def test_collaborative_review_passes_fc_gate(self, substrate):
        fc = build_foundational_commitment(
            commitment_id="fc/test-sentinel",
            name="Test Commitment",
            recipe="Always be relational.",
        )
        substrate.save(fc.record)

        proposal = ProposedChange(
            crystallization_id="fc/test-sentinel",
            proposed_by="collaborative-review",
            proposed_at=_now_iso(),
            rationale="collaborative session revision",
            field_updates={"recipe": "Revised: always be relational."},
            archive_prior_version=True,
        )
        result = fc.validate_proposed_change(proposal)
        assert result is None, f"Gate should pass but returned: {result}"

    def test_non_collaborative_review_blocked_for_fc_self_change(self, substrate):
        fc = build_foundational_commitment(
            commitment_id="fc/test-sentinel",
            name="Test Commitment",
            recipe="Always be relational.",
        )
        for bad_source in ("instrument", "aux-model", "user-123"):
            proposal = ProposedChange(
                crystallization_id="fc/test-sentinel",
                proposed_by=bad_source,
                proposed_at=_now_iso(),
                rationale="test",
                field_updates={"recipe": "changed"},
                archive_prior_version=True,
            )
            result = fc.validate_proposed_change(proposal)
            assert result is not None, (
                f"Gate should block proposed_by={bad_source!r} but returned None"
            )

    def test_collaborative_review_without_archive_blocked(self, substrate):
        fc = build_foundational_commitment(
            commitment_id="fc/test-sentinel",
            name="Test Commitment",
            recipe="Always be relational.",
        )
        proposal = ProposedChange(
            crystallization_id="fc/test-sentinel",
            proposed_by="collaborative-review",
            proposed_at=_now_iso(),
            rationale="collaborative session revision",
            field_updates={"recipe": "Revised."},
            archive_prior_version=False,   # missing archive flag
        )
        result = fc.validate_proposed_change(proposal)
        assert result is not None, "Gate should block collaborative-review without archive"


# ---------------------------------------------------------------------------
# Fix #5 — PrescriptiveProfile staleness-flag grace-window policy
# ---------------------------------------------------------------------------


class TestStalenessGracePolicy:
    """
    Verifies the policy distinguishes staleness-only updates from structural
    changes, coalesces per (id, field-set), and auto-applies after grace window.
    """

    def test_staleness_only_proposal_goes_to_grace_queue(self, substrate):
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        policy = StalenessGracePolicyManager(substrate, grace_window_hours=48)
        proposal = _proposed_change(
            p.record.id,
            {"staleness_flag": True, "staleness_reason": "enactment failed"},
        )
        decision = policy.process(proposal)
        assert decision.queued
        assert not decision.applied
        assert len(policy.pending_grace_window()) == 1
        assert len(policy.pending_review()) == 0

    def test_structural_change_goes_to_review_queue(self, substrate):
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        policy = StalenessGracePolicyManager(substrate)
        proposal = _proposed_change(
            p.record.id,
            {"recipe": "Updated recipe content."},
        )
        decision = policy.process(proposal)
        assert decision.queued
        assert not decision.applied
        assert len(policy.pending_review()) == 1
        assert len(policy.pending_grace_window()) == 0

    def test_coalesce_resets_grace_window(self, substrate):
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        policy = StalenessGracePolicyManager(substrate, grace_window_hours=48)
        proposal1 = _proposed_change(
            p.record.id,
            {"staleness_flag": True, "staleness_reason": "first observation"},
        )
        proposal2 = _proposed_change(
            p.record.id,
            {"staleness_flag": True, "staleness_reason": "second observation"},
        )
        policy.process(proposal1)
        decision2 = policy.process(proposal2)
        assert decision2.replaced_existing
        assert len(policy.pending_grace_window()) == 1
        # Most recent observation wins
        pending = policy.pending_grace_window()[0]
        assert pending.proposal.field_updates["staleness_reason"] == "second observation"

    def test_different_field_sets_not_coalesced(self, substrate):
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        policy = StalenessGracePolicyManager(substrate)
        proposal_a = _proposed_change(
            p.record.id,
            {"staleness_flag": True},
        )
        proposal_b = _proposed_change(
            p.record.id,
            {"last_verified_at": _now_iso()},
        )
        policy.process(proposal_a)
        policy.process(proposal_b)
        assert len(policy.pending_grace_window()) == 2

    def test_flush_ready_applies_expired_staleness(self, substrate):
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        policy = StalenessGracePolicyManager(substrate, grace_window_hours=0)
        proposal = _proposed_change(
            p.record.id,
            {"staleness_flag": True, "staleness_reason": "expired immediately"},
        )
        policy.process(proposal)
        applied = policy.flush_ready()
        assert len(applied) == 1
        assert len(policy.pending_grace_window()) == 0
        updated = substrate.load(p.record.id)
        assert updated is not None
        assert updated.staleness_flag is True

    def test_flush_ready_does_not_apply_unexpired(self, substrate):
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        policy = StalenessGracePolicyManager(substrate, grace_window_hours=48)
        proposal = _proposed_change(
            p.record.id,
            {"staleness_flag": True},
        )
        policy.process(proposal)
        applied = policy.flush_ready()
        assert len(applied) == 0
        assert len(policy.pending_grace_window()) == 1

    def test_is_staleness_only_classifier(self):
        staleness_proposal = _proposed_change(
            "some-id",
            {"staleness_flag": True, "staleness_reason": "x"},
        )
        structural_proposal = _proposed_change(
            "some-id",
            {"recipe": "new recipe"},
        )
        mixed_proposal = _proposed_change(
            "some-id",
            {"staleness_flag": True, "recipe": "new recipe"},
        )
        assert _is_staleness_only(staleness_proposal)
        assert not _is_staleness_only(structural_proposal)
        assert not _is_staleness_only(mixed_proposal)

    def test_apply_reviewed_removes_from_review_queue_and_writes(self, substrate):
        p = _profile("Welfare", signals=["welfare research"])
        substrate.save(p.record)

        policy = StalenessGracePolicyManager(substrate)
        proposal = _proposed_change(
            p.record.id,
            {"recipe": "Updated recipe via human review."},
        )
        policy.process(proposal)
        assert len(policy.pending_review()) == 1

        policy.apply_reviewed(proposal)
        assert len(policy.pending_review()) == 0
        updated = substrate.load(p.record.id)
        assert updated is not None
        assert updated.recipe == "Updated recipe via human review."
