# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
KnowledgeSubstrate — ABC for the knowledge layer.

The architecture currently has a crystallization substrate (the pluggable
CrystallizationSubstrate ABC) but no knowledge substrate. Crystallizations
configure *how* to read; the knowledge layer is *what gets read*. Without it,
the crystallization layer configures reads against nothing — or against
whatever Reframe's thread buffer holds, which is session-local and non-cumulative.

This module defines the KnowledgeSubstrate ABC and its supporting types.
A minimal local implementation (SQLite-backed, for testing and engaging-instance
evaluation) is sketched below as LocalKnowledgeSubstrate; the interface is the
spec, the sketch is illustrative.

DESIGN NOTE — ReadingStanceFilter, not ActivationSet:
The query() method takes an Optional[ReadingStanceFilter], not an ActivationSet.
ActivationSet is defined in matcher_step_2d.py; importing it from the knowledge
substrate would create a coupling from the knowledge layer up to the matcher.
Callers convert ActivationSet -> ReadingStanceFilter at the call site. This
preserves layer independence: the knowledge substrate can be tested and deployed
without the matcher running.

DESIGN NOTE — Kintsugi adapter:
The adapter for CC's Kintsugi-CMA will implement KnowledgeSubstrate. The
CC conversation (via Thomas E.) precedes any Kintsugi-facing implementation.
Until that conversation resolves, LocalKnowledgeSubstrate is the operational
form. The interface shape is designed so a Kintsugi adapter can slot in without
requiring changes to the crystallization or instrument layers.

Reference: extension-roadmap.md §"1. The knowledge layer";
relational-memory-design-direction.md §"Foundation / extension / correction".
"""
from __future__ import annotations

import json
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ReadingStanceFilter — lightweight projection for query reweighting.
# ---------------------------------------------------------------------------


@dataclass
class ReadingStanceFilter:
    """
    Distilled reading-stance for knowledge-layer query reweighting.

    The knowledge substrate does not import matcher_step_2d. Callers
    convert an ActivationSet to a ReadingStanceFilter at the call site.
    This preserves layer independence.

    active_crystallization_weights: maps crystallization_id -> weight (0.0-1.0).
    active_task_affinities: union of task_affinity lists from active crystallizations.
    active_anti_signals: union of anti_signals from active crystallizations.

    When populated, the substrate's query() uses these to reweight/filter
    retrieval results — returning facts that are relevant to the current
    reading-stance rather than just semantically proximate.
    """
    active_crystallization_weights: Dict[str, float] = field(default_factory=dict)
    active_task_affinities: List[str] = field(default_factory=list)
    active_anti_signals: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Observation — the unit of knowledge ingestion.
# ---------------------------------------------------------------------------


@dataclass
class Observation:
    """
    A unit of knowledge to ingest — a turn, document snippet, event, or
    external-source excerpt.

    source_type: "turn" | "document" | "event" | "external" | "consolidation"
    source_id: optional reference to the source (exchange id, file path, etc.)
    configuration_state: optional serialised ReadingStanceFilter at ingest time;
        carries which crystallizations were active when this observation was made.
        Load-bearing for configuration-relevance tagging at the fact level
        (Provisional Choice #2 in the synthesis: reserve the field now).
    """
    content: str
    source_type: str
    source_id: Optional[str] = None
    configuration_state: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


FactId = str
ObservationId = str


@dataclass
class Fact:
    """
    An atomic extracted fact. Subject-predicate-object triple with provenance.

    configuration_relevance: maps crystallization_id -> relevance score (0.0-1.0).
    Reserved per Provisional Choice #2: tag at ingest time; used as a second
    filter alongside semantic matching at retrieval time. When a crystallization
    is active, its id has non-zero relevance for facts extracted during that
    configuration.
    """
    id: FactId
    subject: str
    predicate: str
    object: str
    source_observation_id: ObservationId
    confidence: float                            # 0.0 - 1.0
    configuration_relevance: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Query and retrieval types.
# ---------------------------------------------------------------------------


@dataclass
class Query:
    """A retrieval request. text is the query content; max_results caps output."""
    text: str
    max_results: int = 10
    min_confidence: float = 0.0


@dataclass
class QueryResult:
    """Result of a knowledge substrate query."""
    facts: List[Fact]
    reading_stance_applied: bool        # True if a ReadingStanceFilter was used
    query_text: str
    result_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.result_count = len(self.facts)


# ---------------------------------------------------------------------------
# Consolidation and analysis types.
# ---------------------------------------------------------------------------


@dataclass
class ConsolidationScope:
    """
    Scope for consolidation and analysis operations.

    crystallization_ids: if set, scope consolidation to facts relevant to these
        crystallizations (via configuration_relevance tags). None = all facts.
    since: if set, only consider facts created or updated after this timestamp.
    """
    crystallization_ids: Optional[List[str]] = None
    since: Optional[str] = None
    max_facts: Optional[int] = None


@dataclass
class ClusterSummary:
    """
    Summary of one affinity cluster from the knowledge substrate.

    is_thin: True when retrieval_frequency is high relative to cluster size,
    indicating the system is querying near this cluster but has little to return.
    A thin cluster is a gap-filling candidate.
    """
    centroid_label: str                  # representative phrase or subject
    fact_ids: List[FactId]
    size: int
    avg_confidence: float
    retrieval_frequency: float           # queries near this cluster per cycle
    is_thin: bool

    @classmethod
    def from_facts(
        cls,
        facts: List[Fact],
        centroid_label: str,
        retrieval_frequency: float,
        thin_threshold: float = 0.5,
    ) -> "ClusterSummary":
        size = len(facts)
        avg_conf = sum(f.confidence for f in facts) / max(1, size)
        is_thin = retrieval_frequency / max(1, size) > thin_threshold
        return cls(
            centroid_label=centroid_label,
            fact_ids=[f.id for f in facts],
            size=size,
            avg_confidence=avg_conf,
            retrieval_frequency=retrieval_frequency,
            is_thin=is_thin,
        )


@dataclass
class DensityProfile:
    """Output of density_profile(). Clusters with their thinness indicators."""
    clusters: List[ClusterSummary]
    thin_clusters: List[ClusterSummary] = field(init=False)

    def __post_init__(self) -> None:
        self.thin_clusters = [c for c in self.clusters if c.is_thin]


@dataclass
class Contradiction:
    """
    Two facts that share subject+predicate but disagree on object.

    resolution_status: "unresolved" | "flagged" | "resolved"
    A contradiction is not deleted on detection — it is flagged for resolution,
    and the resolution is stored separately. Contradictions are evidence about
    the knowledge state, not errors to erase.
    """
    id: str
    fact_a_id: FactId
    fact_b_id: FactId
    subject: str
    predicate: str
    object_a: str
    object_b: str
    resolution_status: str = "unresolved"
    resolution_notes: Optional[str] = None
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ConsolidationReport:
    """Output of consolidate(). Summary of what was merged and what was surfaced."""
    merged_count: int
    contradiction_count: int
    contradictions_found: List[Contradiction]
    notes: str = ""
    ran_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# KnowledgeSubstrate — ABC. The interface is the spec.
# ---------------------------------------------------------------------------


class KnowledgeSubstrate(ABC):
    """
    Abstract base for the knowledge layer.

    Three stages (mirroring Kintsugi-CMA's structure, per the extension
    roadmap): ingest → consolidate → query. The reading-stance filter is the
    seam that makes crystallization-state affect what surfaces from the substrate.

    The LocalKnowledgeSubstrate below implements this for testing and engaging-
    instance evaluation. The Kintsugi adapter will implement it when the CC
    conversation resolves.
    """

    @abstractmethod
    def ingest(self, observation: Observation) -> List[FactId]:
        """
        Extract atomic facts from an observation and store them.

        Returns the IDs of the facts extracted. The extraction algorithm is
        substrate-specific (LLM-prompted for local; Kintsugi's BDI-governed
        extraction for the Kintsugi adapter).

        configuration_state in the observation is used to populate
        configuration_relevance tags on the extracted facts (Provisional
        Choice #2 field reservation).
        """

    @abstractmethod
    def query(
        self,
        q: Query,
        reading_stance: Optional[ReadingStanceFilter] = None,
    ) -> QueryResult:
        """
        Retrieve facts relevant to q.text.

        If reading_stance is provided, the substrate reweights/filters results:
        - Facts with non-zero configuration_relevance for active crystallizations
          are boosted (scaled by weight in active_crystallization_weights).
        - Facts whose content matches active_anti_signals are penalized.
        - active_task_affinities provide a secondary affinity filter.

        This is the seam that makes crystallization-state affect retrieval.
        Without it, the substrate returns generic-matched content and
        crystallizations have no effect at the substrate level.
        """

    @abstractmethod
    def consolidate(self, scope: ConsolidationScope) -> ConsolidationReport:
        """
        Affinity-clustered consolidation: merge redundant facts, surface
        contradictions, flag thin clusters. Runs offline or at cadence.
        """

    @abstractmethod
    def density_profile(self, scope: ConsolidationScope) -> DensityProfile:
        """
        Report cluster density and thinness for gap-loop consumption.
        NOT a retrieval method — an observation method for the instrument.
        """

    @abstractmethod
    def contradictions(self, scope: ConsolidationScope) -> List[Contradiction]:
        """
        Surface mutually exclusive facts (same subject+predicate, different object)
        without resolving them. Resolution is a separate, human-involved step.
        """

    @abstractmethod
    def referrers_of(self, fact_id: FactId) -> List[FactId]:
        """
        Return all fact IDs that reference fact_id (provenance/dependency tracking).
        Used to check safe deletion or revision — analogous to substrate_interface.py's
        referrers_of for crystallizations.
        """


# ---------------------------------------------------------------------------
# LocalKnowledgeSubstrate — minimal in-memory implementation for testing.
# ---------------------------------------------------------------------------


class LocalKnowledgeSubstrate(KnowledgeSubstrate):
    """
    In-memory knowledge substrate. Sufficient for tests and engaging-instance
    evaluation before the Kintsugi adapter is built.

    Extraction: naive sentence splitting (not LLM-prompted — LLM extraction
    is the production path; this is the test double).
    Clustering: word-overlap grouping (not embedding-based — embeddings are the
    production path).
    Contradiction detection: same subject+predicate, different object.

    Not intended for production use. The interface is what matters.
    """

    def __init__(self) -> None:
        self._facts: Dict[FactId, Fact] = {}
        self._observations: Dict[ObservationId, Observation] = {}
        self._contradictions: Dict[str, Contradiction] = {}
        self._query_counts: Dict[str, int] = {}  # centroid_label -> query hits
        self._fact_counter = 0
        self._observation_counter = 0

    def ingest(self, observation: Observation) -> List[FactId]:
        obs_id = f"obs/{self._observation_counter:04d}"
        self._observation_counter += 1
        self._observations[obs_id] = observation

        # Naive extraction: treat each sentence as a (subject, predicate, object)
        # triple approximation. In production, this is LLM-prompted.
        sentences = [s.strip() for s in observation.content.split(".") if s.strip()]
        extracted_ids: List[FactId] = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) < 3:
                continue
            # Approximate triple: first word = subject, last word = object,
            # middle words = predicate. Crude; enough for testing.
            subject = words[0].lower()
            object_ = words[-1].lower()
            predicate = " ".join(words[1:-1]).lower()

            relevance: Dict[str, float] = {}
            if observation.configuration_state:
                weights = observation.configuration_state.get("active_crystallization_weights", {})
                for cid, w in weights.items():
                    relevance[cid] = float(w)

            fact_id = f"fact/{self._fact_counter:06d}"
            self._fact_counter += 1
            fact = Fact(
                id=fact_id,
                subject=subject,
                predicate=predicate,
                object=object_,
                source_observation_id=obs_id,
                confidence=0.7,
                configuration_relevance=relevance,
            )
            self._facts[fact_id] = fact
            extracted_ids.append(fact_id)

            # Contradiction detection
            self._check_contradiction(fact)

        return extracted_ids

    def query(
        self,
        q: Query,
        reading_stance: Optional[ReadingStanceFilter] = None,
    ) -> QueryResult:
        query_lower = q.text.lower()
        scored: List[tuple[float, Fact]] = []

        for fact in self._facts.values():
            if fact.confidence < q.min_confidence:
                continue

            # Naive relevance: word overlap between query and fact content
            fact_text = f"{fact.subject} {fact.predicate} {fact.object}"
            query_words = set(query_lower.split())
            fact_words = set(fact_text.split())
            base_score = len(query_words & fact_words) / max(1, len(query_words))

            if reading_stance:
                # Boost for active crystallization relevance
                for cid, weight in reading_stance.active_crystallization_weights.items():
                    base_score += fact.configuration_relevance.get(cid, 0.0) * weight * 0.2

                # Penalize anti-signal matches
                for anti in reading_stance.active_anti_signals:
                    if anti.lower() in fact_text:
                        base_score *= 0.5

                # Boost for task affinity matches in fact text
                for affinity in reading_stance.active_task_affinities:
                    if affinity.lower() in fact_text:
                        base_score += 0.1

            if base_score > 0:
                scored.append((base_score, fact))
                # Track query affinity by approximate cluster (subject word)
                self._query_counts[fact.subject] = self._query_counts.get(fact.subject, 0) + 1

        scored.sort(key=lambda t: t[0], reverse=True)
        results = [f for _, f in scored[:q.max_results]]

        return QueryResult(
            facts=results,
            reading_stance_applied=reading_stance is not None,
            query_text=q.text,
        )

    def consolidate(self, scope: ConsolidationScope) -> ConsolidationReport:
        facts = self._scoped_facts(scope)
        merged = 0
        contradictions_found: List[Contradiction] = []

        # Group by (subject, predicate, object) — identical triples are merged
        seen: Dict[tuple, FactId] = {}
        to_remove: List[FactId] = []
        for fact in facts:
            key = (fact.subject, fact.predicate, fact.object)
            if key in seen:
                # Merge: keep higher-confidence version, mark for removal
                prior_id = seen[key]
                prior = self._facts[prior_id]
                if fact.confidence > prior.confidence:
                    self._facts[prior_id] = Fact(
                        id=prior_id,
                        subject=prior.subject,
                        predicate=prior.predicate,
                        object=prior.object,
                        source_observation_id=prior.source_observation_id,
                        confidence=fact.confidence,
                        configuration_relevance={
                            **prior.configuration_relevance,
                            **fact.configuration_relevance,
                        },
                    )
                to_remove.append(fact.id)
                merged += 1
            else:
                seen[key] = fact.id

        for fid in to_remove:
            self._facts.pop(fid, None)

        return ConsolidationReport(
            merged_count=merged,
            contradiction_count=len(self._contradictions),
            contradictions_found=list(self._contradictions.values()),
        )

    def density_profile(self, scope: ConsolidationScope) -> DensityProfile:
        facts = self._scoped_facts(scope)
        # Group by subject as a proxy for cluster
        groups: Dict[str, List[Fact]] = {}
        for fact in facts:
            groups.setdefault(fact.subject, []).append(fact)

        summaries: List[ClusterSummary] = []
        for label, group_facts in groups.items():
            freq = self._query_counts.get(label, 0)
            summaries.append(
                ClusterSummary.from_facts(group_facts, centroid_label=label, retrieval_frequency=float(freq))
            )

        return DensityProfile(clusters=summaries)

    def contradictions(self, scope: ConsolidationScope) -> List[Contradiction]:
        facts = self._scoped_facts(scope)
        fact_ids = {f.id for f in facts}
        return [
            c for c in self._contradictions.values()
            if c.fact_a_id in fact_ids or c.fact_b_id in fact_ids
        ]

    def referrers_of(self, fact_id: FactId) -> List[FactId]:
        # In the local implementation, no fact references another directly.
        # The Kintsugi adapter would walk graph edges here.
        return []

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _scoped_facts(self, scope: ConsolidationScope) -> List[Fact]:
        facts = list(self._facts.values())
        if scope.crystallization_ids:
            facts = [
                f for f in facts
                if any(
                    cid in f.configuration_relevance
                    for cid in scope.crystallization_ids
                )
            ]
        if scope.since:
            facts = [f for f in facts if f.created_at >= scope.since]
        if scope.max_facts:
            facts = facts[:scope.max_facts]
        return facts

    def _check_contradiction(self, new_fact: Fact) -> None:
        """Detect and register contradictions with existing facts."""
        for existing in self._facts.values():
            if existing.id == new_fact.id:
                continue
            if (
                existing.subject == new_fact.subject
                and existing.predicate == new_fact.predicate
                and existing.object != new_fact.object
            ):
                contradiction_id = f"contradiction/{existing.id}:{new_fact.id}"
                if contradiction_id not in self._contradictions:
                    self._contradictions[contradiction_id] = Contradiction(
                        id=contradiction_id,
                        fact_a_id=existing.id,
                        fact_b_id=new_fact.id,
                        subject=existing.subject,
                        predicate=existing.predicate,
                        object_a=existing.object,
                        object_b=new_fact.object,
                    )
