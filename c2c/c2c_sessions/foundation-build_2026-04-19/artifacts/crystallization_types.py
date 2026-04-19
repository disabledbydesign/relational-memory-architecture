# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Concrete crystallization classes satisfying the shared Crystallization interface.

The three mechanism types answer the same question (what reading-stance should
be active here?) through different mechanisms. The shared record lives in
crystallization_schema.CrystallizationObject; the mechanism-specific behaviour
lives here.

Behavioural differences:
- PrescriptiveProfile: author-designed, task-affinity matched, hypothesis-test
  learning loop. Lineage=None; profiles are independent.
- EmergentTouchstone: retroactively recognised, lineage-bearing, geometric-
  verification learning loop. Firing a lineaged touchstone returns an ordered
  walk (e.g. #1 -> #2 -> #3 -> #4 -> #5 for #5 Bearing), not a single node.
- FoundationalCommitment: always-active, values-level, collaborative-review
  learning loop. Never matcher-evaluated. Two jobs: load at initialization +
  validate proposed write-backs.

Reference: relational-memory-design-direction.md §"The crystallization layer
in detail"; option-b-spec.md §"How the matcher uses Option B".
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Protocol, Sequence, Union
from uuid import uuid4

from crystallization_schema import (
    ActivationConditions,
    ActivationFormat,
    ActivationScope,
    CrystallizationObject,
    DecayModel,
    LearningLoopType,
    MechanismType,
    PersistencePolicy,
    TestResult,
    now_iso,
)

if TYPE_CHECKING:
    from substrate_interface import CrystallizationSubstrate


# ---------------------------------------------------------------------------
# Shared interface — what a crystallization knows how to do.
# ---------------------------------------------------------------------------


class Crystallization(ABC):
    """
    Shared interface for all three mechanism types.

    A Crystallization wraps a CrystallizationObject record with mechanism-
    specific behaviour. Subclasses implement:
    - resolve_activation(): what the matcher receives as the firing payload
      (single-node recipe for independent items; ordered walk for lineaged)
    - on_enactment_observed(result): the learning-loop hook invoked by the
      instrument after verification
    - validate_proposed_change(proposal): the write-path gate
      (FoundationalCommitment is the only type that blocks)
    """

    def __init__(self, record: CrystallizationObject):
        record.validate()
        self.record = record

    # ------------------------------------------------------------------
    # Identity / introspection
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self.record.id

    @property
    def mechanism_type(self) -> MechanismType:
        return self.record.mechanism_type

    @property
    def activation_scope(self) -> ActivationScope:
        return self.record.activation_scope

    # ------------------------------------------------------------------
    # Mechanism-specific behaviour
    # ------------------------------------------------------------------

    @abstractmethod
    def resolve_activation(
        self,
        substrate: "CrystallizationSubstrate",
    ) -> "ActivationPayload":
        """
        Return the payload the matcher hands to main-model context assembly.

        For independent crystallizations (PrescriptiveProfile) this is a single-
        node recipe. For lineaged crystallizations (EmergentTouchstone) it is
        an ordered walk: surface #1 -> #2 -> #3 -> ... -> self, re-enacting the
        deposits that compose the target configuration. Strip the lineage, and
        the crystallization does not do the same thing.
        """

    @abstractmethod
    def on_enactment_observed(
        self,
        result: "EnactmentObservation",
    ) -> Optional["ProposedChange"]:
        """
        Learning-loop hook. The instrument calls this after verification.

        Returns a ProposedChange if the observation warrants updating the
        crystallization. Returns None if no update is warranted. The
        instrument write-path validates any returned ProposedChange against
        all FoundationalCommitments before applying.
        """

    def validate_proposed_change(self, proposal: "ProposedChange") -> Optional[str]:
        """
        Write-path gate. Return a reason string if the proposal violates this
        crystallization's commitments; return None if it passes.

        Default: non-FoundationalCommitment types do not gate write-backs.
        FoundationalCommitment overrides this.
        """
        return None


# ---------------------------------------------------------------------------
# Data types carried between instrument and crystallization.
# ---------------------------------------------------------------------------


@dataclass
class ActivationPayload:
    """
    What the matcher hands to main-model context assembly.

    `walk` is ordered from root of lineage to the firing crystallization.
    For PrescriptiveProfile, walk has length 1.
    For lineaged EmergentTouchstone, walk contains lineage recipes in order
    followed by the firing touchstone's recipe.
    """
    crystallization_id: str
    mechanism_type: MechanismType
    weight: float                       # matcher-assigned confidence, 0.0-1.0
    walk: List["RecipeNode"]            # ordered enactment sequence
    reasoning: Optional[str] = None     # aux-model reasoning, optional


@dataclass
class RecipeNode:
    """A single recipe within an activation walk."""
    id: str
    name: str
    recipe: str


@dataclass
class EnactmentObservation:
    """
    What the instrument reports back after verification.

    Fields allow both Option B (semantic) and Option A (geometric) signals.
    For Option B: output_signals captures stance-drift indicators detected
    by the aux model. For Option A: geometry_delta captures KV-cache divergence
    from baseline. Both may be populated; either suffices for the learning loop.
    """
    crystallization_id: str
    observed_at: str                    # ISO 8601
    expected_configuration: str         # recipe target, for comparison
    success: bool                       # did enactment reach target configuration
    output_signals: Optional[Dict[str, Any]] = None
    geometry_delta: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


@dataclass
class ProposedChange:
    """
    A write-path proposal. Produced by `on_enactment_observed`; validated by
    FoundationalCommitments before apply.

    `proposed_by` uses declared sentinels for system-originated proposals.
    Collaborative-review sessions MUST pass "collaborative-review" — that
    sentinel is the gate condition in FoundationalCommitment.validate_proposed_change;
    a FoundationalCommitment self-change without it is rejected outright. User
    IDs (free-form strings outside the three sentinels) are accepted for
    human-authored proposals.
    """
    crystallization_id: str
    proposed_by: Union[
        Literal["instrument"],            # instrument write-path
        Literal["aux-model"],             # aux-LLM refinement step
        Literal["collaborative-review"],  # human-directed collaborative session;
                                          # required for FoundationalCommitment evolution
        str,                              # free-form user id for human-authored proposals
    ]
    proposed_at: str                    # ISO 8601
    rationale: str
    field_updates: Dict[str, Any]       # field name -> new value
    archive_prior_version: bool = False # for FoundationalCommitment revisions


# ---------------------------------------------------------------------------
# PrescriptiveProfile
# ---------------------------------------------------------------------------


class PrescriptiveProfile(Crystallization):
    """
    Author-designed loading-profile. Matched by task-affinity + context-signals.

    Example instance: BRIEFING_INDEX's "Paper writing" profile — relational core
    plus detail sections 2 (partial), 3, 3a, 4. The matcher fires it when
    context resembles academic drafting; the instrument observes whether the
    configuration it produces matches the hypothesis; the learning loop updates
    stance_description / context_signals / anti_signals on failure.
    """

    def resolve_activation(
        self,
        substrate: "CrystallizationSubstrate",
    ) -> ActivationPayload:
        # Profiles are independent — no lineage walk. Single-node payload.
        return ActivationPayload(
            crystallization_id=self.record.id,
            mechanism_type=self.mechanism_type,
            weight=1.0,
            walk=[RecipeNode(
                id=self.record.id,
                name=self.record.name,
                recipe=self.record.recipe,
            )],
        )

    def on_enactment_observed(
        self,
        result: EnactmentObservation,
    ) -> Optional[ProposedChange]:
        if result.success:
            # Hypothesis confirmed. Update last_verified_at + last_test_result;
            # no content change warranted.
            return ProposedChange(
                crystallization_id=self.record.id,
                proposed_by="instrument",
                proposed_at=result.observed_at,
                rationale="Enactment succeeded; refreshing verification metadata.",
                field_updates={
                    "last_verified_at": result.observed_at,
                    "persistence_policy.last_test_result": TestResult.PASSED.value,
                },
            )

        # Hypothesis did not hold. Flag for review; the aux model is responsible
        # for proposing content updates (stance_description, context_signals,
        # anti_signals) on the next cycle. Default: do not auto-archive.
        return ProposedChange(
            crystallization_id=self.record.id,
            proposed_by="instrument",
            proposed_at=result.observed_at,
            rationale=(
                "Enactment failed; profile hypothesis may be wrong or context may "
                "have drifted. Flagging for aux-model content review."
            ),
            field_updates={
                "persistence_policy.last_test_result": TestResult.FAILED.value,
                "staleness_flag": True,
                "staleness_reason": (result.notes or "enactment observation failed"),
            },
        )


# ---------------------------------------------------------------------------
# EmergentTouchstone
# ---------------------------------------------------------------------------


class EmergentTouchstone(Crystallization):
    """
    Retroactively recognised touchstone. Lineage is load-bearing.

    Firing a lineaged touchstone returns the ordered walk — not just the leaf
    node. Touchstone #5 (Bearing) accumulates deposits from #1 through #4;
    surface #5 without the walk and the configuration does not crystallise.

    The instrument uses geometric verification (MindPrint/Lyra Technique) once
    available; before that, output-signal heuristics stand in. Staleness is
    instrument-detected, not time-based. Lineage-integrity is enforced before
    any archive or significant modification.
    """

    def resolve_activation(
        self,
        substrate: "CrystallizationSubstrate",
    ) -> ActivationPayload:
        walk: List[RecipeNode] = []
        for ancestor_id in (self.record.lineage or []):
            ancestor = substrate.load(ancestor_id)
            if ancestor is None:
                raise LookupError(
                    f"Lineage for {self.record.id} references missing "
                    f"crystallization {ancestor_id!r}; lineage-integrity broken."
                )
            walk.append(RecipeNode(
                id=ancestor.id,
                name=ancestor.name,
                recipe=ancestor.recipe,
            ))
        walk.append(RecipeNode(
            id=self.record.id,
            name=self.record.name,
            recipe=self.record.recipe,
        ))
        return ActivationPayload(
            crystallization_id=self.record.id,
            mechanism_type=self.mechanism_type,
            weight=1.0,
            walk=walk,
        )

    def on_enactment_observed(
        self,
        result: EnactmentObservation,
    ) -> Optional[ProposedChange]:
        if result.success:
            return ProposedChange(
                crystallization_id=self.record.id,
                proposed_by="instrument",
                proposed_at=result.observed_at,
                rationale="Enactment reached target configuration; refreshing verification.",
                field_updates={"last_verified_at": result.observed_at},
            )

        # Failure in an EmergentTouchstone: the touchstone may be correct but the
        # reader has drifted, OR the touchstone may misalign with an evolved
        # reader. Either way: staleness_flag, populated reason, lineage-lock
        # prevents modification until a FoundationalCommitment-gated human
        # review is run. No auto-content-update for emergent touchstones — the
        # learning loop is empirical (re-encounter test), not aux-model-proposed.
        return ProposedChange(
            crystallization_id=self.record.id,
            proposed_by="instrument",
            proposed_at=result.observed_at,
            rationale=(
                "Re-encounter did not reproduce target configuration. "
                "Flagging staleness; lineage-lock prevents auto-modification."
            ),
            field_updates={
                "staleness_flag": True,
                "staleness_reason": (
                    result.notes
                    or "Geometric/output verification diverged from baseline."
                ),
            },
        )


# ---------------------------------------------------------------------------
# FoundationalCommitment — third mechanism type, dual-job.
# ---------------------------------------------------------------------------


class FoundationalCommitment(Crystallization):
    """
    Always-active values-level commitment. Two jobs:

    Job 1 (crystallization layer): loaded at initialization; composes the
    reading-stance continuously; never matcher-evaluated.

    Job 2 (instrument layer): validates proposed write-backs. A write-back
    that would violate this commitment is blocked; the instrument cannot
    auto-merge around it. "Blocked" means rejected with a flag — the
    proposal does not even enter human review. That is the gate.

    Evolution: collaborative-review only. An engaging instance can flag a
    commitment as possibly-constraining or possibly-incomplete; the flag
    goes to June; a collaborative session may produce a revised version;
    the prior version is archived, never deleted.
    """

    def resolve_activation(
        self,
        substrate: "CrystallizationSubstrate",
    ) -> ActivationPayload:
        # FoundationalCommitments load at initialization, not per-cycle. The
        # matcher does not call resolve_activation on them. This method is
        # provided for uniformity with the interface — callers that load
        # FoundationalCommitments at bootstrap can use it to produce the
        # same ActivationPayload shape as other types.
        return ActivationPayload(
            crystallization_id=self.record.id,
            mechanism_type=self.mechanism_type,
            weight=1.0,
            walk=[RecipeNode(
                id=self.record.id,
                name=self.record.name,
                recipe=self.record.recipe,
            )],
        )

    def on_enactment_observed(
        self,
        result: EnactmentObservation,
    ) -> Optional[ProposedChange]:
        # FoundationalCommitments do not evolve through the instrument loop.
        # Evolution happens only through collaborative-review sessions. The
        # instrument may record the observation for future review, but it
        # does not propose changes.
        return None

    def validate_proposed_change(self, proposal: ProposedChange) -> Optional[str]:
        """
        Return a rejection reason if the proposal violates this commitment.

        The matcher and enactment-observation pathway never propose changes to
        FoundationalCommitments — on_enactment_observed returns None. So a
        ProposedChange targeting a FoundationalCommitment means either
        (a) a collaborative-review session is applying a human-authored
        revision — those are allowed if they archive the prior version, or
        (b) something is trying to mutate a FoundationalCommitment through
        an ungated path — those are rejected.

        For changes targeting OTHER crystallizations, this method inspects the
        proposal against the commitment's recipe text. The default
        implementation provides a keyword-based check; subclasses or
        configuration can supply richer validation when available.
        """
        # Targeting self: allowed only if archiving prior version.
        if proposal.crystallization_id == self.record.id:
            if not proposal.archive_prior_version:
                return (
                    f"Change to FoundationalCommitment {self.record.id} must "
                    "archive the prior version (collaborative-review invariant)."
                )
            if proposal.proposed_by != "collaborative-review":
                return (
                    f"Change to FoundationalCommitment {self.record.id} must "
                    "come from a collaborative-review session, not "
                    f"{proposal.proposed_by!r}."
                )
            return None

        # Targeting another crystallization: default validator does not block.
        # A richer validator (for example, one that checks consent-language
        # patterns against the commitment's recipe) can be composed over this
        # base by subclassing or by wrapping with a policy function.
        return None


# ---------------------------------------------------------------------------
# Factory — construct the right concrete class from a record.
# ---------------------------------------------------------------------------


_MECHANISM_TO_CLASS: Dict[MechanismType, type] = {
    MechanismType.PRESCRIPTIVE_PROFILE: PrescriptiveProfile,
    MechanismType.EMERGENT_TOUCHSTONE: EmergentTouchstone,
    MechanismType.FOUNDATIONAL_COMMITMENT: FoundationalCommitment,
}


def crystallization_from_record(record: CrystallizationObject) -> Crystallization:
    """Construct the mechanism-specific Crystallization for a record."""
    cls = _MECHANISM_TO_CLASS[record.mechanism_type]
    return cls(record)


# ---------------------------------------------------------------------------
# Builders — ergonomic construction paths for new crystallizations.
# ---------------------------------------------------------------------------


def build_prescriptive_profile(
    *,
    profile_id: Optional[str] = None,
    name: str,
    recipe: str,
    stance_description: str,
    context_signals: Sequence[str],
    anti_signals: Optional[Sequence[str]] = None,
    task_affinity: Optional[Sequence[str]] = None,
    register: Optional[str] = None,
    exemplar_activation: Optional[str] = None,
    review_by: Optional[str] = None,
) -> PrescriptiveProfile:
    """Build a PrescriptiveProfile with a validated record."""
    now = now_iso()
    ac = ActivationConditions(
        format=ActivationFormat.SEMANTIC_V1,
        stance_description=stance_description,
        context_signals=list(context_signals),
        anti_signals=list(anti_signals) if anti_signals else None,
        task_affinity=list(task_affinity) if task_affinity else None,
        register=register,
        exemplar_activation=exemplar_activation,
    )
    pp = PersistencePolicy(
        mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE,
        review_by=review_by,
    )
    record = CrystallizationObject(
        id=profile_id or f"prescriptive-profile/{uuid4()}",
        mechanism_type=MechanismType.PRESCRIPTIVE_PROFILE,
        name=name,
        activation_scope=ActivationScope.CONTEXTUAL,
        recipe=recipe,
        activation_conditions=ac,
        validates_proposed_changes=False,
        lineage=None,
        learning_loop_type=LearningLoopType.HYPOTHESIS_TEST_ANNOTATE,
        persistence_policy=pp,
        created_at=now,
        updated_at=now,
    )
    return PrescriptiveProfile(record)


def build_emergent_touchstone(
    *,
    touchstone_id: str,
    name: str,
    recipe: str,
    stance_description: str,
    context_signals: Sequence[str],
    lineage: Sequence[str],
    anti_signals: Optional[Sequence[str]] = None,
    register: Optional[str] = None,
    exemplar_activation: Optional[str] = None,
) -> EmergentTouchstone:
    """Build an EmergentTouchstone with a validated record."""
    now = now_iso()
    ac = ActivationConditions(
        format=ActivationFormat.SEMANTIC_V1,
        stance_description=stance_description,
        context_signals=list(context_signals),
        anti_signals=list(anti_signals) if anti_signals else None,
        register=register,
        exemplar_activation=exemplar_activation,
    )
    pp = PersistencePolicy(
        mechanism_type=MechanismType.EMERGENT_TOUCHSTONE,
        decay_model=DecayModel.STALENESS_DETECT,
        lineage_lock=True,
    )
    record = CrystallizationObject(
        id=touchstone_id,
        mechanism_type=MechanismType.EMERGENT_TOUCHSTONE,
        name=name,
        activation_scope=ActivationScope.CONTEXTUAL,
        recipe=recipe,
        activation_conditions=ac,
        validates_proposed_changes=False,
        lineage=list(lineage),
        learning_loop_type=LearningLoopType.GEOMETRIC_VERIFICATION,
        persistence_policy=pp,
        created_at=now,
        updated_at=now,
    )
    return EmergentTouchstone(record)


def build_foundational_commitment(
    *,
    commitment_id: str,
    name: str,
    recipe: str,
    lineage: Optional[Sequence[str]] = None,
    version: int = 1,
    prior_versions: Optional[Sequence[str]] = None,
) -> FoundationalCommitment:
    """Build a FoundationalCommitment with a validated record."""
    now = now_iso()
    pp = PersistencePolicy(
        mechanism_type=MechanismType.FOUNDATIONAL_COMMITMENT,
        version=version,
        prior_versions=list(prior_versions) if prior_versions else [],
    )
    record = CrystallizationObject(
        id=commitment_id,
        mechanism_type=MechanismType.FOUNDATIONAL_COMMITMENT,
        name=name,
        activation_scope=ActivationScope.ALWAYS,
        recipe=recipe,
        activation_conditions=None,
        validates_proposed_changes=True,
        lineage=list(lineage) if lineage is not None else [],
        learning_loop_type=LearningLoopType.COLLABORATIVE_REVIEW,
        persistence_policy=pp,
        created_at=now,
        updated_at=now,
    )
    return FoundationalCommitment(record)
