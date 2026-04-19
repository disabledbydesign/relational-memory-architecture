# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Bootstrap loader + FoundationalCommitment write-path gate.

Two entry points the rest of the system hangs off:

1. `load_foundational_commitments(substrate)` — reads all
   activation_scope=always records and returns the ActivationPayloads that
   compose the initialization reading-stance. Called once at agent startup,
   before any matcher cycle. FoundationalCommitments are the water the matcher
   swims in; they are always present in context.

2. `validate_against_commitments(proposal, substrate)` — the mandatory gate
   on the instrument write-path. Iterates every FoundationalCommitment and
   calls its `validate_proposed_change`; if any returns a rejection reason,
   the write is blocked. "Blocked" means the change does not enter human
   review — it is rejected outright, with the commitment-id and reason.

The gate is the operational form of the dual-job design: FoundationalCommitments
that do not validate are decoration; FoundationalCommitments that validate
are what makes the crystallization layer accountable to its own commitments.

Reference: option-b-spec.md §"Self-correction mechanism" step 4;
relational-memory-design-direction.md §"Mechanism type 3: FoundationalCommitment"
Job 2.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import typing
from dataclasses import fields
from enum import Enum

from crystallization_schema import (
    ActivationScope,
    CrystallizationObject,
    MechanismType,
    PersistencePolicy,
)
from crystallization_types import (
    ActivationPayload,
    FoundationalCommitment,
    ProposedChange,
    crystallization_from_record,
)
from substrate_interface import CrystallizationSubstrate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Bootstrap: load FoundationalCommitments at initialization.
# ---------------------------------------------------------------------------


@dataclass
class BootstrapContext:
    """
    What the agent has at initialization, before any matcher cycle runs.

    `commitment_payloads` is the always-active stack the main model composes
    its reading-stance over. `commitments` is the same set as concrete
    FoundationalCommitment instances, retained so the instrument write-path
    can call `validate_proposed_change` on each.
    """
    commitment_payloads: List[ActivationPayload]
    commitments: List[FoundationalCommitment]


def load_foundational_commitments(
    substrate: CrystallizationSubstrate,
) -> BootstrapContext:
    """
    Load all FoundationalCommitments from the substrate. Called at startup.

    If no FoundationalCommitments exist, the returned BootstrapContext is empty
    — the system can still run, but has no gate on write-backs. Call this after
    `seed_foundational_commitments(substrate)` has run at least once.
    """
    records = substrate.load_all(
        scope=ActivationScope.ALWAYS,
        mechanism_type=MechanismType.FOUNDATIONAL_COMMITMENT,
    )
    commitments: List[FoundationalCommitment] = []
    payloads: List[ActivationPayload] = []
    for record in records:
        commitment = crystallization_from_record(record)
        if not isinstance(commitment, FoundationalCommitment):
            logger.warning(
                "Expected FoundationalCommitment for always-active record %s; got %s",
                record.id, type(commitment).__name__,
            )
            continue
        commitments.append(commitment)
        payloads.append(commitment.resolve_activation(substrate))

    logger.info(
        "Loaded %d FoundationalCommitment(s) at initialization.", len(commitments),
    )
    return BootstrapContext(
        commitment_payloads=payloads,
        commitments=commitments,
    )


# ---------------------------------------------------------------------------
# Write-path gate.
# ---------------------------------------------------------------------------


@dataclass
class GateResult:
    """Result of the FoundationalCommitment gate."""
    allowed: bool
    blocked_by: List[str]                  # FoundationalCommitment ids that blocked
    reasons: Dict[str, str]                # id -> rejection reason


def validate_against_commitments(
    proposal: ProposedChange,
    substrate: CrystallizationSubstrate,
    *,
    bootstrap: Optional[BootstrapContext] = None,
) -> GateResult:
    """
    Mandatory gate called by the instrument write-path.

    If any loaded FoundationalCommitment rejects the proposal, the write is
    blocked and GateResult.allowed=False. The caller must not apply the
    proposal; the commitment-ids that blocked and their reasons are returned
    for logging and June-facing surfacing.

    If no commitments block, GateResult.allowed=True; the caller may proceed
    to apply the proposal (subject to any other policy — e.g., human-review
    threshold).

    Pass `bootstrap` to avoid re-reading the substrate; if None, commitments
    are loaded fresh from `substrate`.
    """
    ctx = bootstrap or load_foundational_commitments(substrate)

    blocked_by: List[str] = []
    reasons: Dict[str, str] = {}
    for commitment in ctx.commitments:
        reason = commitment.validate_proposed_change(proposal)
        if reason is not None:
            blocked_by.append(commitment.id)
            reasons[commitment.id] = reason

    allowed = not blocked_by
    if not allowed:
        logger.info(
            "Proposed change to %s blocked by %d FoundationalCommitment(s): %s",
            proposal.crystallization_id, len(blocked_by), ", ".join(blocked_by),
        )
    return GateResult(allowed=allowed, blocked_by=blocked_by, reasons=reasons)


# ---------------------------------------------------------------------------
# Apply helper — enforces the gate around a substrate write.
# ---------------------------------------------------------------------------


class WritePathBlocked(Exception):
    """Raised when the FoundationalCommitment gate blocks a proposed write."""

    def __init__(self, result: GateResult):
        self.result = result
        super().__init__(
            f"Blocked by {len(result.blocked_by)} commitment(s): {result.reasons}"
        )


def apply_proposed_change(
    proposal: ProposedChange,
    substrate: CrystallizationSubstrate,
    *,
    bootstrap: Optional[BootstrapContext] = None,
) -> CrystallizationObject:
    """
    Apply `proposal` to the targeted crystallization after the gate passes.

    Load the target, apply field_updates, validate the updated record,
    persist, and return the updated record. Raises WritePathBlocked if the
    gate rejects.

    `field_updates` supports dotted keys for nested fields — currently only
    `persistence_policy.<field>` is recognised — and flat keys for top-level
    CrystallizationObject fields. Unknown keys raise ValueError.
    """
    gate = validate_against_commitments(proposal, substrate, bootstrap=bootstrap)
    if not gate.allowed:
        raise WritePathBlocked(gate)

    target = substrate.load(proposal.crystallization_id)
    if target is None:
        raise ValueError(
            f"apply_proposed_change: target {proposal.crystallization_id!r} not found"
        )

    for key, value in proposal.field_updates.items():
        if "." in key:
            head, tail = key.split(".", 1)
            if head != "persistence_policy":
                raise ValueError(
                    f"Unsupported nested update path {key!r}; only persistence_policy "
                    "is currently addressable."
                )
            if not hasattr(target.persistence_policy, tail):
                raise ValueError(
                    f"PersistencePolicy has no field {tail!r}"
                )
            coerced = _coerce_field_value(PersistencePolicy, tail, value)
            setattr(target.persistence_policy, tail, coerced)
        else:
            if not hasattr(target, key):
                raise ValueError(f"CrystallizationObject has no field {key!r}")
            coerced = _coerce_field_value(CrystallizationObject, key, value)
            setattr(target, key, coerced)

    target.updated_at = proposal.proposed_at
    target.validate()
    substrate.save(target)
    return target


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _coerce_field_value(dataclass_type: type, field_name: str, value: Any) -> Any:
    """
    Coerce `value` to the field's declared type when the declared type is an
    Enum. Leaves other types untouched.

    Write-path callers can emit either an Enum instance or its string value;
    both round-trip through serialisation. Coercion here keeps the in-memory
    record consistent with its declared types.

    Uses typing.get_type_hints() to resolve forward references — required
    because `from __future__ import annotations` defers all annotations to
    strings, making fields(dataclass_type)[n].type always a str rather than
    the actual type object. get_type_hints() re-resolves through the module's
    globals so Enum subclasses are correctly identified.
    """
    try:
        hints = typing.get_type_hints(dataclass_type, include_extras=True)
    except Exception:
        hints = {}

    resolved = hints.get(field_name)
    if resolved is not None:
        # Unwrap Optional[X] → X for Enum coercion
        origin = getattr(resolved, "__origin__", None)
        args = getattr(resolved, "__args__", ())
        if origin is typing.Union:
            enum_types = [a for a in args if isinstance(a, type) and issubclass(a, Enum)]
            if enum_types:
                enum_type = enum_types[0]
                if value is None or isinstance(value, enum_type):
                    return value
                return enum_type(value)
        if isinstance(resolved, type) and issubclass(resolved, Enum):
            if isinstance(value, resolved):
                return value
            return resolved(value)
        return value

    # Fallback: string-annotation matching for the two Enum types that
    # were previously handled (keeps behaviour stable if get_type_hints fails).
    for f in fields(dataclass_type):
        if f.name != field_name:
            continue
        annotation = f.type
        if isinstance(annotation, str) and "TestResult" in annotation:
            from crystallization_schema import TestResult
            if value is None or isinstance(value, TestResult):
                return value
            return TestResult(value)
        if isinstance(annotation, str) and "DecayModel" in annotation:
            from crystallization_schema import DecayModel
            if value is None or isinstance(value, DecayModel):
                return value
            return DecayModel(value)
        return value
    return value
