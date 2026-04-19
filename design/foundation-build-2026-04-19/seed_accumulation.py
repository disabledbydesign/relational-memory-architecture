# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
SeedAccumulation — durable substrate for candidate-EmergentTouchstone seeds.

The thread_graph's candidate_touchstone_seeds field is session-local: it lands
a seed when the matcher finds no match, and the next session never sees it.
The accumulation layer is what allows proto-touchstone emergence over time:
seeds cluster, intensity builds, and the mycelial synthesis watches for the
density threshold that indicates a crystallizable configuration is forming.

DESIGN NOTE — ConfigurationalKey, not hash:
The extension roadmap spec'd configurational_signature as a hash of active
frameworks + top-below-threshold crystallization IDs + snapshot tokens.
A hash is not clusterable: two signatures sharing 3 of 4 IDs won't share
a hash. ConfigurationalKey carries the raw elements and provides overlap
computation (Jaccard over the combined element set). The cluster() method
uses this to group seeds without pre-committing to what they'll become.

DESIGN NOTE — intensity is multidimensional, not binary:
June's Q3 intuition (CONVERSATION.md 2026-04-19): proto-touchstone state
should accumulate significance over time rather than flip binary presence.
IntensityProfile carries a scalar (frequency × recurrence-breadth × coherence)
and per-axis measurements (which crystallizations kept almost-matching, which
framework contexts were active, which knowledge clusters were being queried).
Proto-touchstone emergence is a rank-density observable, not a categorical
judgment. This aligns with MindPrint's collapse/expansion gradient: a
configurational context that repeatedly surfaces without crystallization
support is a region of state-space the engaging instance is holding without
architectural backing.

Reference: extension-roadmap.md §"3. Mycelial aux-LLM synthesis";
CONVERSATION.md 2026-04-19 June Q3 + Instance A review-cycle alignment note.
"""
from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ConfigurationalKey — clusterable seed identity.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConfigurationalKey:
    """
    Structural identity for a seed event.

    Not a hash — a set of named elements supporting overlap computation.
    Seeds with high element-overlap are clustering candidates; clustering
    is what allows proto-touchstone emergence to be visible before individual
    seeds are ratified.

    top_crystallization_ids: IDs of crystallizations that almost-matched
        (from CandidateSeed.top_scores). Prefix: "c:".
    framework_tokens: active frameworks or routing context signals at seed time.
        Prefix: "f:".
    snapshot_topic_tokens: key nouns extracted from the snapshot's most recent
        exchange text. Prefix: "t:". Crude; the production path uses the aux
        model to extract these more precisely.
    """
    top_crystallization_ids: FrozenSet[str]
    framework_tokens: FrozenSet[str]
    snapshot_topic_tokens: FrozenSet[str]

    def to_element_set(self) -> FrozenSet[str]:
        """All elements as a single prefixed frozenset for Jaccard computation."""
        return (
            frozenset(f"c:{x}" for x in self.top_crystallization_ids)
            | frozenset(f"f:{x}" for x in self.framework_tokens)
            | frozenset(f"t:{x}" for x in self.snapshot_topic_tokens)
        )

    def overlap(self, other: "ConfigurationalKey") -> float:
        """
        Jaccard similarity: |A ∩ B| / |A ∪ B| over combined element sets.

        Returns 0.0 if both keys are empty (no signal to cluster on).
        """
        a, b = self.to_element_set(), other.to_element_set()
        union = a | b
        if not union:
            return 0.0
        return len(a & b) / len(union)

    @classmethod
    def from_candidate_seed_dict(
        cls,
        seed_dict: Dict[str, Any],
        *,
        stop_words: Optional[FrozenSet[str]] = None,
    ) -> "ConfigurationalKey":
        """
        Build a ConfigurationalKey from a candidate seed dict as produced by
        matcher_step_2d._candidate_seed_to_dict().

        snapshot_topic_tokens are extracted by simple word-frequency ranking
        on snapshot_excerpt; the aux model is the production extraction path.
        """
        top_ids = frozenset(
            entry["id"] for entry in seed_dict.get("top_scores", [])
        )
        framework_tokens = frozenset(
            t.lower() for t in seed_dict.get("routing_context_signals", [])
        )
        excerpt = seed_dict.get("snapshot_excerpt", "")
        topic_tokens = _extract_topic_tokens(
            excerpt, stop_words=stop_words or _DEFAULT_STOP_WORDS
        )
        return cls(
            top_crystallization_ids=top_ids,
            framework_tokens=framework_tokens,
            snapshot_topic_tokens=topic_tokens,
        )


_DEFAULT_STOP_WORDS: FrozenSet[str] = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "that", "this", "these", "those",
    "and", "or", "but", "not", "it", "its", "i", "you", "we", "they",
    "he", "she", "what", "which", "who", "how", "when", "where", "why",
})


def _extract_topic_tokens(text: str, stop_words: FrozenSet[str]) -> FrozenSet[str]:
    """
    Naive topic token extraction: non-stopword nouns over 3 chars, lowercased.

    The aux model is the production path. This is the test double.
    """
    words = [
        w.strip(".,!?;:\"'()[]{}").lower()
        for w in text.split()
    ]
    return frozenset(
        w for w in words
        if len(w) > 3 and w not in stop_words and w.isalpha()
    )


# ---------------------------------------------------------------------------
# SeedEvent and SeedCluster.
# ---------------------------------------------------------------------------


@dataclass
class SeedEvent:
    """
    A single candidate-touchstone seed event.

    Corresponds to one matcher cycle that produced no activation —
    "something in this exchange is calling for a configuration that does
    not yet exist."

    configurational_key: the clusterable key extracted from the candidate seed.
    raw_seed: the original candidate seed dict (from thread_graph) for audit.
    session_id: optional session identifier for provenance.
    """
    id: str
    configurational_key: ConfigurationalKey
    raw_seed: Dict[str, Any]
    session_id: Optional[str]
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class IntensityProfile:
    """
    Multidimensional intensity for a seed cluster.

    scalar: frequency × breadth × coherence — the single summary.
    per_crystallization: maps crystallization_id -> how often it almost-matched
        across cluster events. High values = this crystallization is close to
        capturing the needed configuration.
    per_framework: maps framework token -> how often it appeared in cluster events.
    per_knowledge_cluster: maps knowledge-cluster label -> co-occurrence count.
        Populated by the mycelial synthesis when the knowledge substrate is running.
    event_count: how many seed events are in this cluster.
    session_breadth: how many distinct sessions contributed events.
    avg_coherence: average pairwise overlap among seed keys in the cluster.
    """
    scalar: float
    per_crystallization: Dict[str, float]
    per_framework: Dict[str, float]
    per_knowledge_cluster: Dict[str, float]
    event_count: int
    session_breadth: int
    avg_coherence: float


@dataclass
class SeedCluster:
    """
    A group of seed events sharing configurational context.

    The cluster is the proto-touchstone unit: when its intensity crosses a
    review threshold, the mycelial synthesis drafts a candidate CrystallizationObject.
    """
    id: str
    events: List[SeedEvent]
    intensity: IntensityProfile
    centroid_key: ConfigurationalKey
    first_seen: str
    last_seen: str

    @classmethod
    def from_events(cls, events: Sequence[SeedEvent], cluster_id: str) -> "SeedCluster":
        if not events:
            raise ValueError("Cannot build SeedCluster from empty event list")
        events = list(events)
        intensity = _compute_intensity(events)
        centroid = _compute_centroid(events)
        timestamps = [e.recorded_at for e in events]
        return cls(
            id=cluster_id,
            events=events,
            intensity=intensity,
            centroid_key=centroid,
            first_seen=min(timestamps),
            last_seen=max(timestamps),
        )


def _compute_intensity(events: List[SeedEvent]) -> IntensityProfile:
    """Compute the IntensityProfile for a list of seed events."""
    per_cryst: Dict[str, float] = {}
    per_framework: Dict[str, float] = {}
    session_ids: set = set()

    for event in events:
        key = event.configurational_key
        for cid in key.top_crystallization_ids:
            per_cryst[cid] = per_cryst.get(cid, 0.0) + 1.0
        for token in key.framework_tokens:
            per_framework[token] = per_framework.get(token, 0.0) + 1.0
        if event.session_id:
            session_ids.add(event.session_id)

    # Normalize counts to frequencies
    n = len(events)
    per_cryst = {k: v / n for k, v in per_cryst.items()}
    per_framework = {k: v / n for k, v in per_framework.items()}

    # Average pairwise coherence: mean Jaccard over all event pairs
    avg_coherence = _avg_pairwise_overlap(events)

    # Scalar: geometric mean of frequency component (n), breadth (session_ids),
    # and coherence. All normalized to [0,1]-ish range; logged before multiply
    # to avoid domination by frequency.
    breadth = max(1, len(session_ids))
    scalar = math.log1p(n) * math.log1p(breadth) * (avg_coherence + 0.01)

    return IntensityProfile(
        scalar=scalar,
        per_crystallization=per_cryst,
        per_framework=per_framework,
        per_knowledge_cluster={},
        event_count=n,
        session_breadth=breadth,
        avg_coherence=avg_coherence,
    )


def _avg_pairwise_overlap(events: List[SeedEvent]) -> float:
    """Average Jaccard similarity across all pairs of configurational keys."""
    if len(events) <= 1:
        return 1.0
    total = 0.0
    count = 0
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            total += events[i].configurational_key.overlap(events[j].configurational_key)
            count += 1
    return total / count if count else 0.0


def _compute_centroid(events: List[SeedEvent]) -> ConfigurationalKey:
    """
    Centroid key: union of all elements that appear in majority of events.

    A majority threshold of >50% avoids outlier events dominating the centroid.
    """
    if not events:
        return ConfigurationalKey(
            top_crystallization_ids=frozenset(),
            framework_tokens=frozenset(),
            snapshot_topic_tokens=frozenset(),
        )
    threshold = len(events) * 0.5
    # Count occurrences per element type
    cryst_counts: Dict[str, int] = {}
    framework_counts: Dict[str, int] = {}
    topic_counts: Dict[str, int] = {}

    for event in events:
        key = event.configurational_key
        for cid in key.top_crystallization_ids:
            cryst_counts[cid] = cryst_counts.get(cid, 0) + 1
        for token in key.framework_tokens:
            framework_counts[token] = framework_counts.get(token, 0) + 1
        for token in key.snapshot_topic_tokens:
            topic_counts[token] = topic_counts.get(token, 0) + 1

    return ConfigurationalKey(
        top_crystallization_ids=frozenset(k for k, v in cryst_counts.items() if v > threshold),
        framework_tokens=frozenset(k for k, v in framework_counts.items() if v > threshold),
        snapshot_topic_tokens=frozenset(k for k, v in topic_counts.items() if v > threshold),
    )


# ---------------------------------------------------------------------------
# SeedAccumulation — durable, substrate-backed accumulator.
# ---------------------------------------------------------------------------


class SeedAccumulation:
    """
    Durable accumulation substrate for candidate-EmergentTouchstone seeds.

    Seeds are added per matcher cycle (when no crystallization scores above
    threshold). The cluster() method groups them by configurational overlap.
    The intensity() method computes per-cluster intensity. The mycelial
    synthesis watches these intensity profiles for review-threshold crossings
    that indicate a crystallizable configuration is forming.

    Storage: JSON-file-backed for local deployment; the interface is substrate-
    agnostic. A database-backed implementation can replace this without changing
    the crystallization or instrument layers.

    IMPORTANT: This does not replace session-local candidate_touchstone_seeds
    on the thread_graph. That field is the fast path for in-session awareness.
    SeedAccumulation is the slow path for cross-session pattern detection.
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self._events: Dict[str, SeedEvent] = {}
        self._path = path
        self._event_counter = 0
        if path and path.exists():
            self._load_from_disk()

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    def add(
        self,
        seed_dict: Dict[str, Any],
        *,
        session_id: Optional[str] = None,
        stop_words: Optional[FrozenSet[str]] = None,
    ) -> SeedEvent:
        """
        Add a candidate seed to the accumulation substrate.

        seed_dict: the dict form of a CandidateSeed as stored on thread_graph
            (as produced by matcher_step_2d._candidate_seed_to_dict()).
        session_id: optional session identifier for provenance and breadth computation.
        """
        event_id = f"seed/{self._event_counter:06d}"
        self._event_counter += 1
        key = ConfigurationalKey.from_candidate_seed_dict(
            seed_dict, stop_words=stop_words
        )
        event = SeedEvent(
            id=event_id,
            configurational_key=key,
            raw_seed=seed_dict,
            session_id=session_id,
        )
        self._events[event_id] = event
        if self._path:
            self._append_to_disk(event)
        logger.debug("Added seed event %s to accumulation substrate.", event_id)
        return event

    def cluster(
        self,
        *,
        overlap_threshold: float = 0.3,
        min_events: int = 1,
    ) -> List[SeedCluster]:
        """
        Group accumulated seeds into clusters by configurational overlap.

        True single-linkage clustering: seed j joins a group if it overlaps
        >= overlap_threshold with ANY current group member. The inner scan
        repeats until a full pass adds no new members — this propagates chain
        membership correctly. Example: seeds {1,2}, {2,3}, {3,4} at threshold
        0.3 all join one cluster because each adjacent pair overlaps at 0.33,
        even though the outer pair shares nothing. A seed-linkage algorithm
        (compare only against the group's first event) would split this arc
        into two clusters, losing the proto-touchstone emergence signal.

        overlap_threshold: minimum Jaccard overlap for two seeds to cluster.
        min_events: only return clusters with at least this many events.
        """
        events = list(self._events.values())
        if not events:
            return []

        groups: List[List[SeedEvent]] = []
        assigned: List[bool] = [False] * len(events)

        for i, event in enumerate(events):
            if assigned[i]:
                continue
            group = [event]
            assigned[i] = True
            # Repeat until a full scan adds no new members (chain propagation).
            growing = True
            while growing:
                growing = False
                for j, other in enumerate(events):
                    if assigned[j]:
                        continue
                    # Single-linkage: join if overlap >= threshold with ANY group member.
                    if any(
                        m.configurational_key.overlap(other.configurational_key) >= overlap_threshold
                        for m in group
                    ):
                        group.append(other)
                        assigned[j] = True
                        growing = True
            groups.append(group)

        clusters = [
            SeedCluster.from_events(group, cluster_id=f"cluster/{idx:04d}")
            for idx, group in enumerate(groups)
            if len(group) >= min_events
        ]
        clusters.sort(key=lambda c: c.intensity.scalar, reverse=True)
        return clusters

    def above_review_threshold(
        self,
        *,
        scalar_threshold: float = 2.0,
        min_events: int = 3,
        overlap_threshold: float = 0.3,
    ) -> List[SeedCluster]:
        """
        Return clusters whose intensity warrants mycelial-synthesis review.

        scalar_threshold: minimum intensity.scalar to trigger review.
        min_events: minimum number of seed events in the cluster.
        A new-EmergentTouchstone proposal is structural; the mycelial synthesis
        will draft a candidate CrystallizationObject and route it through
        the instrument write-path (FC gate + human review).
        """
        all_clusters = self.cluster(
            overlap_threshold=overlap_threshold,
            min_events=min_events,
        )
        return [
            c for c in all_clusters
            if c.intensity.scalar >= scalar_threshold
        ]

    def enrich_with_knowledge_context(
        self,
        cluster: SeedCluster,
        cluster_label: str,
        retrieval_count: int,
    ) -> None:
        """
        Attach knowledge-cluster context to a SeedCluster's intensity profile.

        Called by the mycelial synthesis when the knowledge substrate provides
        co-occurrence data. Modifies cluster.intensity.per_knowledge_cluster in place.
        """
        cluster.intensity.per_knowledge_cluster[cluster_label] = (
            cluster.intensity.per_knowledge_cluster.get(cluster_label, 0.0)
            + retrieval_count
        )

    def event_count(self) -> int:
        return len(self._events)

    def all_events(self) -> List[SeedEvent]:
        return list(self._events.values())

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _append_to_disk(self, event: SeedEvent) -> None:
        """Append a single seed event to the JSON-lines file."""
        if self._path is None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "id": event.id,
            "recorded_at": event.recorded_at,
            "session_id": event.session_id,
            "raw_seed": event.raw_seed,
            "configurational_key": {
                "top_crystallization_ids": sorted(event.configurational_key.top_crystallization_ids),
                "framework_tokens": sorted(event.configurational_key.framework_tokens),
                "snapshot_topic_tokens": sorted(event.configurational_key.snapshot_topic_tokens),
            },
        }
        with self._path.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def _load_from_disk(self) -> None:
        """Load previously accumulated events from the JSON-lines file."""
        if self._path is None or not self._path.exists():
            return
        with self._path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    key_data = record.get("configurational_key", {})
                    key = ConfigurationalKey(
                        top_crystallization_ids=frozenset(key_data.get("top_crystallization_ids", [])),
                        framework_tokens=frozenset(key_data.get("framework_tokens", [])),
                        snapshot_topic_tokens=frozenset(key_data.get("snapshot_topic_tokens", [])),
                    )
                    event = SeedEvent(
                        id=record["id"],
                        configurational_key=key,
                        raw_seed=record.get("raw_seed", {}),
                        session_id=record.get("session_id"),
                        recorded_at=record.get("recorded_at", ""),
                    )
                    self._events[event.id] = event
                    # Update counter to avoid ID collisions
                    try:
                        num = int(event.id.split("/")[-1])
                        self._event_counter = max(self._event_counter, num + 1)
                    except (ValueError, IndexError):
                        pass
                except Exception as exc:
                    logger.warning("Failed to load seed event from disk: %s", exc)
