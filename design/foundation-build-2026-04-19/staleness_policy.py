# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
PrescriptiveProfile staleness-flag grace-window policy.

Welfare-first implementation of the auto-merge policy Instance B proposed and
Instance A concurred on (CONVERSATION.md 2026-04-19, Q2 resolution):

  review-gated by default, with a grace window for staleness-flag updates only.

The asymmetry: discovering that a crystallization is stale is low-stakes and
time-sensitive; the next engaging instance should benefit from accurate state
within a short window rather than waiting for human attention. Recipe revisions
(new context_signals, updated stance_description, structural field changes)
remain review-gated — those are high-stakes and can wait.

Coalesces pending edits per (crystallization_id, frozenset of field keys) so
repeated staleness observations don't stack. On a coalesce, the most recent
observation wins and the grace window resets.

Integration: call `StalenessGracePolicyManager.process(proposal, substrate)`
from the instrument write-path after the FoundationalCommitment gate passes.
The manager either applies the change immediately (staleness-only, after window
elapses) or queues it for human review (structural changes).

Reference: CONVERSATION.md 2026-04-19 June Q2; A's coalescing note.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

from crystallization_types import ProposedChange
from substrate_interface import CrystallizationSubstrate

logger = logging.getLogger(__name__)


# Fields that constitute staleness-flag-only updates. Any proposal whose
# field_updates contain only these keys (plus bookkeeping fields) is
# eligible for grace-window auto-apply.
_STALENESS_ONLY_FIELDS: FrozenSet[str] = frozenset({
    "staleness_flag",
    "staleness_reason",
    "last_verified_at",
    "last_fired_at",
    "persistence_policy.last_test_result",
    "persistence_policy.never_fired_recently",
    "updated_at",
})

# Default grace window in hours. After this interval, a pending staleness
# update is auto-applied if not reviewed first.
DEFAULT_GRACE_WINDOW_HOURS: int = 48


def _is_staleness_only(proposal: ProposedChange) -> bool:
    """Return True iff all updated fields are in _STALENESS_ONLY_FIELDS."""
    return bool(proposal.field_updates) and all(
        k in _STALENESS_ONLY_FIELDS for k in proposal.field_updates
    )


def _field_key_set(proposal: ProposedChange) -> FrozenSet[str]:
    return frozenset(proposal.field_updates.keys())


@dataclass
class PendingChange:
    """A queued change awaiting either grace-window expiry or human review."""
    proposal: ProposedChange
    queued_at: datetime
    is_staleness_only: bool
    grace_window_hours: int


@dataclass
class PolicyDecision:
    """What the policy decided to do with a ProposedChange."""
    applied: bool                       # True if auto-applied right now
    queued: bool                        # True if added to the pending queue
    replaced_existing: bool             # True if it coalesced with a prior pending
    reason: str


class StalenessGracePolicyManager:
    """
    Manages the review-gated / grace-window split for write-path proposals.

    Usage::

        policy = StalenessGracePolicyManager(substrate)
        decision = policy.process(proposal, bootstrap=bootstrap_ctx)

    Call `flush_ready()` periodically (e.g. once per enrichment cycle) to
    apply any pending staleness updates whose grace window has elapsed.
    """

    def __init__(
        self,
        substrate: CrystallizationSubstrate,
        *,
        grace_window_hours: int = DEFAULT_GRACE_WINDOW_HOURS,
    ):
        self._substrate = substrate
        self._grace_window_hours = grace_window_hours
        # Key: (crystallization_id, frozenset of field keys) → PendingChange
        self._queue: Dict[Tuple[str, FrozenSet[str]], PendingChange] = {}
        # Human-review queue — structural changes only
        self._review_queue: List[PendingChange] = []

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    def process(
        self,
        proposal: ProposedChange,
    ) -> PolicyDecision:
        """
        Route a ProposedChange through the policy.

        Staleness-only updates go to the grace-window queue; on a coalesce,
        the most recent observation wins and the window resets.

        Structural updates (recipe, context_signals, stance_description, etc.)
        go to the human-review queue unconditionally.
        """
        if _is_staleness_only(proposal):
            return self._enqueue_grace_window(proposal)
        else:
            return self._enqueue_for_review(proposal)

    def flush_ready(self) -> List[ProposedChange]:
        """
        Apply all staleness-only updates whose grace window has elapsed.

        Returns the list of proposals that were applied. Failures are logged
        and skipped (not re-queued — the next observation cycle will re-flag
        if the condition persists).
        """
        now = datetime.now(timezone.utc)
        applied: List[ProposedChange] = []
        expired_keys: List[Tuple[str, FrozenSet[str]]] = []

        for key, pending in self._queue.items():
            elapsed = now - pending.queued_at
            if elapsed >= timedelta(hours=pending.grace_window_hours):
                expired_keys.append(key)

        for key in expired_keys:
            pending = self._queue.pop(key)
            try:
                self._apply(pending.proposal)
                applied.append(pending.proposal)
                logger.info(
                    "Grace-window auto-applied staleness update for %s (fields: %s)",
                    pending.proposal.crystallization_id,
                    sorted(pending.proposal.field_updates.keys()),
                )
            except Exception as exc:
                logger.warning(
                    "Grace-window auto-apply failed for %s: %s",
                    pending.proposal.crystallization_id, exc,
                )

        return applied

    def pending_review(self) -> List[PendingChange]:
        """Return the current human-review queue (structural changes)."""
        return list(self._review_queue)

    def pending_grace_window(self) -> List[PendingChange]:
        """Return the current grace-window queue (staleness-only changes)."""
        return list(self._queue.values())

    def apply_reviewed(self, proposal: ProposedChange) -> None:
        """
        Apply a proposal that has received human review approval.

        Removes it from the review queue if present. Used by UI/review
        surfaces to close a pending structural change.
        """
        self._review_queue = [
            p for p in self._review_queue
            if p.proposal.crystallization_id != proposal.crystallization_id
            or _field_key_set(p.proposal) != _field_key_set(proposal)
        ]
        self._apply(proposal)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _enqueue_grace_window(self, proposal: ProposedChange) -> PolicyDecision:
        key = (proposal.crystallization_id, _field_key_set(proposal))
        replaced = key in self._queue
        self._queue[key] = PendingChange(
            proposal=proposal,
            queued_at=datetime.now(timezone.utc),
            is_staleness_only=True,
            grace_window_hours=self._grace_window_hours,
        )
        logger.debug(
            "%s staleness update for %s (fields: %s); grace window %dh.",
            "Replaced existing" if replaced else "Queued",
            proposal.crystallization_id,
            sorted(proposal.field_updates.keys()),
            self._grace_window_hours,
        )
        return PolicyDecision(
            applied=False,
            queued=True,
            replaced_existing=replaced,
            reason=(
                f"Staleness-only update queued; grace window {self._grace_window_hours}h. "
                + ("Replaced prior pending for same field-set." if replaced else "")
            ),
        )

    def _enqueue_for_review(self, proposal: ProposedChange) -> PolicyDecision:
        self._review_queue.append(PendingChange(
            proposal=proposal,
            queued_at=datetime.now(timezone.utc),
            is_staleness_only=False,
            grace_window_hours=0,
        ))
        logger.info(
            "Structural change queued for human review: %s (fields: %s)",
            proposal.crystallization_id,
            sorted(proposal.field_updates.keys()),
        )
        return PolicyDecision(
            applied=False,
            queued=True,
            replaced_existing=False,
            reason="Structural change queued for human review.",
        )

    def _apply(self, proposal: ProposedChange) -> None:
        from bootstrap import apply_proposed_change
        apply_proposed_change(proposal, self._substrate)
