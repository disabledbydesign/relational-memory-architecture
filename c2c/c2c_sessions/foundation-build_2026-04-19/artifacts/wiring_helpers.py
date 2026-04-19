# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Wiring helpers — cross-layer conversion utilities.

This module is the explicit seam where layers that are designed to be
independent must be connected. The knowledge substrate imports
ReadingStanceFilter from knowledge_substrate.py; the matcher produces
ActivationSet from matcher_step_2d.py; neither imports the other.

The conversion in this module is non-trivial: weights come from the
ActivationSet, but task_affinities and anti_signals require loading each
activated crystallization from a CrystallizationSubstrate and reading its
activation_conditions. That substrate-read is the coupling that makes the
wiring layer necessary and non-trivial.

DESIGN NOTE — documented seam:
knowledge_substrate.py documents "Callers convert ActivationSet ->
ReadingStanceFilter at the call site" but provides no converter. The
absence was noted in Instance A's review (CONVERSATION.md 2026-04-19
09:10 UTC, finding #4): "As-is, a future instance trying to wire the
knowledge substrate into the enricher has to re-derive what the conversion
needs. Document or provide the helper; don't leave the seam invisible."
This module resolves that finding.

PRODUCTION NOTE — flat affinity boost:
The LocalKnowledgeSubstrate applies a flat +0.1 boost per task-affinity
match regardless of which crystallization the affinity came from. The
converter (activation_set_to_reading_stance_filter) unions affinities
without weighting. A production KnowledgeSubstrate should weight the
affinity boost by the crystallization's active score from
active_crystallization_weights — lowest-weighted crystallizations should
not get the same affinity signal as highest-weighted ones. The
LocalKnowledgeSubstrate is a test double; this assumption does not need
to transfer to the production adapter. (Finding: Instance A, 10:30 UTC.)

INTEGRATION POINT (Reframe wiring):
In the Reframe enrichment cycle, after run_matcher_step() produces an
ActivationSet, the wiring layer calls:

    reading_stance = activation_set_to_reading_stance_filter(
        activation_set, crystallization_substrate
    )
    knowledge_result = knowledge_substrate.query(query, reading_stance)

The crystallization_substrate and knowledge_substrate are separate objects.
The wiring layer holds both; no layer holds the other's substrate.

Reference: knowledge_substrate.py DESIGN NOTE — ReadingStanceFilter;
matcher_step_2d.py ActivationSet; extension-roadmap.md §"1. The knowledge layer".
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Set

from knowledge_substrate import ReadingStanceFilter

if TYPE_CHECKING:
    from matcher_step_2d import ActivationSet
    from substrate_interface import CrystallizationSubstrate

logger = logging.getLogger(__name__)


def activation_set_to_reading_stance_filter(
    activation_set: "ActivationSet",
    substrate: "CrystallizationSubstrate",
) -> ReadingStanceFilter:
    """
    Convert a matcher ActivationSet to a ReadingStanceFilter.

    Loads each activated crystallization's activation_conditions from the
    substrate to extract task_affinities and anti_signals. Crystallizations
    with no activation_conditions (e.g., FoundationalCommitments — which
    should never appear in an ActivationSet, but are guarded against) are
    skipped.

    Parameters
    ----------
    activation_set : ActivationSet
        Output of CrystallizationMatcher.match(). May contain zero activations
        (empty set produces an empty ReadingStanceFilter, which is safe to pass
        to knowledge_substrate.query() — it degrades gracefully to semantic-only).
    substrate : CrystallizationSubstrate
        Crystallization substrate. Used to load activation_conditions per
        activated ID. Must be the same substrate the matcher used.

    Returns
    -------
    ReadingStanceFilter
        Aggregated weights, task_affinities, and anti_signals across all
        active crystallizations. Duplicates within each list are deduplicated;
        ordering follows the score-ranked order of activations.
    """
    weights = {}
    task_affinities = []
    anti_signals = []
    seen_affinities: Set[str] = set()
    seen_anti_signals: Set[str] = set()

    for activation in activation_set.activations:
        cid = activation.payload.crystallization_id
        weights[cid] = activation.score

        record = substrate.load(cid)
        if record is None:
            logger.warning(
                "wiring_helpers: activated crystallization %r not found in substrate; "
                "skipping task_affinity/anti_signal extraction.",
                cid,
            )
            continue

        ac = record.activation_conditions
        if ac is None:
            # FoundationalCommitment: activation_conditions is None by design.
            # Should never appear in an ActivationSet; log and skip.
            logger.debug(
                "wiring_helpers: %r has no activation_conditions (FoundationalCommitment?); "
                "skipping.",
                cid,
            )
            continue

        for affinity in (ac.task_affinity or []):
            if affinity not in seen_affinities:
                task_affinities.append(affinity)
                seen_affinities.add(affinity)

        for signal in (ac.anti_signals or []):
            if signal not in seen_anti_signals:
                anti_signals.append(signal)
                seen_anti_signals.add(signal)

    return ReadingStanceFilter(
        active_crystallization_weights=weights,
        active_task_affinities=task_affinities,
        active_anti_signals=anti_signals,
    )
