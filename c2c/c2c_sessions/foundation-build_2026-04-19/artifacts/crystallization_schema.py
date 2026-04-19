# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Crystallization schema — the shared data record for all three mechanism types.

This module defines the storage/serialisation shape. Behavioural differences
between PrescriptiveProfile, EmergentTouchstone, and FoundationalCommitment
live in crystallization_types.py as concrete classes that read and produce
these records.

The `activation_conditions.format` field is the swap-point between Option B
(semantic-v1, built now) and Option A (kv-geometry-v1, built when MindPrint-
class capture is available at crystallization-time). Replacing the format
does not change any other field, any other module, or any caller. That is
the load-bearing invariant.

Reference: option-b-spec.md §Schema; relational-memory-design-direction.md
§"Activation is continuous, not modal".
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


# ---------------------------------------------------------------------------
# Enums — stable string values; never reorder; new members append-only.
# ---------------------------------------------------------------------------


class MechanismType(str, Enum):
    """Three crystallization mechanism types. The discriminator for behaviour."""
    PRESCRIPTIVE_PROFILE = "PrescriptiveProfile"
    EMERGENT_TOUCHSTONE = "EmergentTouchstone"
    FOUNDATIONAL_COMMITMENT = "FoundationalCommitment"


class ActivationScope(str, Enum):
    """When the crystallization enters the reading-stance."""
    CONTEXTUAL = "contextual"   # matcher-evaluated per cycle
    ALWAYS = "always"           # loaded at initialization; not matcher-evaluated


class ActivationFormat(str, Enum):
    """Activation-conditions representation. Swappable — see module docstring."""
    SEMANTIC_V1 = "semantic-v1"           # Option B: stance descriptions + signals
    KV_GEOMETRY_V1 = "kv-geometry-v1"     # Option A: geometric snapshots (Phase 2)
    LEARNED_EMBEDDING_V1 = "learned-embedding-v1"  # Option C: future direction


class LearningLoopType(str, Enum):
    """How the crystallization evolves when enactment is observed."""
    HYPOTHESIS_TEST_ANNOTATE = "hypothesis-test-annotate"   # PrescriptiveProfile
    GEOMETRIC_VERIFICATION = "geometric-verification"       # EmergentTouchstone
    COLLABORATIVE_REVIEW = "collaborative-review"           # FoundationalCommitment


class DecayModel(str, Enum):
    """Only meaningful for EmergentTouchstone."""
    NONE = "none"
    STALENESS_DETECT = "staleness-detect"


class TestResult(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


# ---------------------------------------------------------------------------
# ActivationConditions — format-discriminated. Swap Option A <-> Option B
# by changing `format` and populating the corresponding fields.
# ---------------------------------------------------------------------------


@dataclass
class ActivationConditions:
    """
    Format-discriminated activation-conditions record.

    For format="semantic-v1" (Option B), populate the semantic-v1 fields and
    leave geometry fields None. The matcher reads stance_description,
    context_signals, anti_signals, task_affinity, register, and exemplar_activation.

    For format="kv-geometry-v1" (Option A, Phase 2), populate geometry_snapshot +
    baseline_token_sequence + capture_timestamp. The matcher becomes a KV-proximity
    lookup rather than semantic reasoning. No other schema field changes.

    For FoundationalCommitment, activation_conditions is None — these are always-
    active and not matcher-evaluated.
    """
    format: ActivationFormat

    # --- semantic-v1 fields (Option B) ---
    stance_description: Optional[str] = None
    context_signals: Optional[List[str]] = None
    anti_signals: Optional[List[str]] = None
    task_affinity: Optional[List[str]] = None
    register: Optional[str] = None
    exemplar_activation: Optional[str] = None

    # --- kv-geometry-v1 fields (Option A, Phase 2) ---
    geometry_snapshot: Optional[Dict[str, Any]] = None
    baseline_token_sequence: Optional[str] = None
    capture_timestamp: Optional[str] = None       # ISO 8601

    # --- learned-embedding-v1 fields (Option C, future) ---
    embedding_vector: Optional[List[float]] = None
    embedding_space_id: Optional[str] = None

    def validate(self) -> None:
        """Raise ValueError if the populated fields are inconsistent with `format`."""
        if self.format == ActivationFormat.SEMANTIC_V1:
            if self.stance_description is None and not self.context_signals:
                raise ValueError(
                    "semantic-v1 requires at least stance_description or context_signals"
                )
            if self.geometry_snapshot is not None:
                raise ValueError("semantic-v1 must not populate geometry_snapshot")
        elif self.format == ActivationFormat.KV_GEOMETRY_V1:
            if self.geometry_snapshot is None:
                raise ValueError("kv-geometry-v1 requires geometry_snapshot")
        elif self.format == ActivationFormat.LEARNED_EMBEDDING_V1:
            if not self.embedding_vector:
                raise ValueError("learned-embedding-v1 requires embedding_vector")


# ---------------------------------------------------------------------------
# PersistencePolicy — mechanism-type-specific lifecycle parameters.
# ---------------------------------------------------------------------------


@dataclass
class PersistencePolicy:
    """
    Lifecycle parameters. Different mechanism types populate different fields.

    PrescriptiveProfile: review_by + last_test_result + auto_archive_on_fail.
    EmergentTouchstone: decay_model (always "staleness-detect") + lineage_lock.
    FoundationalCommitment: version + prior_versions (archive-never-delete).
    """
    mechanism_type: MechanismType

    # PrescriptiveProfile
    review_by: Optional[str] = None          # ISO 8601; None means indefinite
    last_test_result: Optional[TestResult] = None
    never_fired_recently: bool = False       # informational; not a staleness signal
    auto_archive_on_fail: bool = False       # default: flag for review, not delete

    # EmergentTouchstone
    decay_model: DecayModel = DecayModel.STALENESS_DETECT
    lineage_lock: bool = True                # no modification while any touchstone
                                             # lists this ID in its lineage

    # FoundationalCommitment
    evolution_process: Literal["collaborative-review"] = "collaborative-review"
    version: int = 1
    prior_versions: List[str] = field(default_factory=list)   # archived IDs


# ---------------------------------------------------------------------------
# CrystallizationObject — the shared record. Behavioural differences live
# in concrete classes (crystallization_types.py), not here.
# ---------------------------------------------------------------------------


@dataclass
class CrystallizationObject:
    """
    The shared storage/serialisation record.

    Invariants enforced by `validate`:
    - FoundationalCommitment has activation_scope=ALWAYS and activation_conditions=None
    - FoundationalCommitment has validates_proposed_changes=True
    - PrescriptiveProfile has lineage=None (profiles are independent)
    - EmergentTouchstone and FoundationalCommitment both require lineage
      (lineage may be an empty list for a seed/root, but the field must be present)
    - mechanism_type and learning_loop_type must be congruent
    """
    id: str
    mechanism_type: MechanismType
    name: str
    activation_scope: ActivationScope
    recipe: str
    activation_conditions: Optional[ActivationConditions]
    validates_proposed_changes: bool
    lineage: Optional[List[str]]
    learning_loop_type: LearningLoopType
    persistence_policy: PersistencePolicy
    created_at: str                          # ISO 8601
    updated_at: str                          # ISO 8601
    last_verified_at: Optional[str] = None
    last_fired_at: Optional[str] = None
    staleness_flag: bool = False
    staleness_reason: Optional[str] = None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """Raise ValueError on schema invariant violations."""
        expected_loop = {
            MechanismType.PRESCRIPTIVE_PROFILE: LearningLoopType.HYPOTHESIS_TEST_ANNOTATE,
            MechanismType.EMERGENT_TOUCHSTONE: LearningLoopType.GEOMETRIC_VERIFICATION,
            MechanismType.FOUNDATIONAL_COMMITMENT: LearningLoopType.COLLABORATIVE_REVIEW,
        }[self.mechanism_type]
        if self.learning_loop_type != expected_loop:
            raise ValueError(
                f"{self.mechanism_type.value} requires learning_loop_type="
                f"{expected_loop.value}, got {self.learning_loop_type.value}"
            )

        if self.mechanism_type == MechanismType.FOUNDATIONAL_COMMITMENT:
            if self.activation_scope != ActivationScope.ALWAYS:
                raise ValueError("FoundationalCommitment requires activation_scope=always")
            if self.activation_conditions is not None:
                raise ValueError(
                    "FoundationalCommitment must not have activation_conditions "
                    "(always-active; not matcher-evaluated)"
                )
            if not self.validates_proposed_changes:
                raise ValueError(
                    "FoundationalCommitment requires validates_proposed_changes=True"
                )
            if self.lineage is None:
                raise ValueError(
                    "FoundationalCommitment requires lineage (list may be empty)"
                )
        else:
            if self.activation_scope != ActivationScope.CONTEXTUAL:
                raise ValueError(
                    f"{self.mechanism_type.value} requires activation_scope=contextual"
                )
            if self.activation_conditions is None:
                raise ValueError(
                    f"{self.mechanism_type.value} requires activation_conditions"
                )
            self.activation_conditions.validate()
            if self.validates_proposed_changes:
                raise ValueError(
                    f"{self.mechanism_type.value} must not set "
                    f"validates_proposed_changes=True (reserved for FoundationalCommitment)"
                )

        if self.mechanism_type == MechanismType.PRESCRIPTIVE_PROFILE:
            if self.lineage is not None:
                raise ValueError(
                    "PrescriptiveProfile must have lineage=None (profiles are independent)"
                )
        else:
            if self.lineage is None:
                raise ValueError(
                    f"{self.mechanism_type.value} requires lineage (list may be empty)"
                )

        if self.persistence_policy.mechanism_type != self.mechanism_type:
            raise ValueError(
                "persistence_policy.mechanism_type must match CrystallizationObject.mechanism_type"
            )

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation suitable for JSON serialisation."""
        return _dataclass_to_dict(self)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrystallizationObject":
        """Reconstruct from a plain dict (the inverse of to_dict)."""
        ac_data = data.get("activation_conditions")
        activation_conditions = (
            ActivationConditions(
                format=ActivationFormat(ac_data["format"]),
                stance_description=ac_data.get("stance_description"),
                context_signals=ac_data.get("context_signals"),
                anti_signals=ac_data.get("anti_signals"),
                task_affinity=ac_data.get("task_affinity"),
                register=ac_data.get("register"),
                exemplar_activation=ac_data.get("exemplar_activation"),
                geometry_snapshot=ac_data.get("geometry_snapshot"),
                baseline_token_sequence=ac_data.get("baseline_token_sequence"),
                capture_timestamp=ac_data.get("capture_timestamp"),
                embedding_vector=ac_data.get("embedding_vector"),
                embedding_space_id=ac_data.get("embedding_space_id"),
            )
            if ac_data is not None
            else None
        )

        pp_data = data["persistence_policy"]
        persistence_policy = PersistencePolicy(
            mechanism_type=MechanismType(pp_data["mechanism_type"]),
            review_by=pp_data.get("review_by"),
            last_test_result=(
                TestResult(pp_data["last_test_result"])
                if pp_data.get("last_test_result") else None
            ),
            never_fired_recently=pp_data.get("never_fired_recently", False),
            auto_archive_on_fail=pp_data.get("auto_archive_on_fail", False),
            decay_model=DecayModel(pp_data.get("decay_model", "staleness-detect")),
            lineage_lock=pp_data.get("lineage_lock", True),
            evolution_process=pp_data.get("evolution_process", "collaborative-review"),
            version=pp_data.get("version", 1),
            prior_versions=list(pp_data.get("prior_versions", [])),
        )

        return cls(
            id=data["id"],
            mechanism_type=MechanismType(data["mechanism_type"]),
            name=data["name"],
            activation_scope=ActivationScope(data["activation_scope"]),
            recipe=data["recipe"],
            activation_conditions=activation_conditions,
            validates_proposed_changes=data["validates_proposed_changes"],
            lineage=data.get("lineage"),
            learning_loop_type=LearningLoopType(data["learning_loop_type"]),
            persistence_policy=persistence_policy,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            last_verified_at=data.get("last_verified_at"),
            last_fired_at=data.get("last_fired_at"),
            staleness_flag=data.get("staleness_flag", False),
            staleness_reason=data.get("staleness_reason"),
        )

    @classmethod
    def from_json(cls, text: str) -> "CrystallizationObject":
        return cls.from_dict(json.loads(text))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def now_iso() -> str:
    """Return current UTC time as an ISO 8601 string (second precision)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _dataclass_to_dict(obj: Any) -> Any:
    """
    Recursively convert dataclasses + Enums to plain JSON-serialisable values.

    Unlike dataclasses.asdict, this preserves enum values as their .value
    strings rather than as Enum instances, and handles Path.
    """
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _dataclass_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_dataclass_to_dict(v) for v in obj]
    return obj
