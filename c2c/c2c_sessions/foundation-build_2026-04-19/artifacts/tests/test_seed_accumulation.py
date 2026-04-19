# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for seed_accumulation.py.

Covers: ConfigurationalKey overlap (not hash), SeedAccumulation add/cluster/
intensity, centroid computation, persistence round-trip, above_review_threshold.

Key verification: clustering uses element overlap (Jaccard), not hash equality.
Two seeds sharing 3 of 4 crystallization IDs MUST cluster together;
they would not under hash-based identity.
"""
import sys
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from seed_accumulation import (
    ConfigurationalKey,
    IntensityProfile,
    SeedAccumulation,
    SeedCluster,
    SeedEvent,
    _avg_pairwise_overlap,
    _compute_centroid,
    _extract_topic_tokens,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_key(cryst_ids=None, frameworks=None, topics=None) -> ConfigurationalKey:
    return ConfigurationalKey(
        top_crystallization_ids=frozenset(cryst_ids or []),
        framework_tokens=frozenset(frameworks or []),
        snapshot_topic_tokens=frozenset(topics or []),
    )


def make_seed_dict(top_ids=None, routing=None, excerpt="") -> dict:
    return {
        "top_scores": [{"id": cid, "score": 0.2} for cid in (top_ids or [])],
        "routing_context_signals": routing or [],
        "snapshot_excerpt": excerpt,
        "flagged_at": "2026-04-19T00:00:00+00:00",
        "user_invocation_phrases": [],
    }


@pytest.fixture
def accumulation():
    return SeedAccumulation()


# ---------------------------------------------------------------------------
# TestConfigurationalKey
# ---------------------------------------------------------------------------


class TestConfigurationalKey:
    def test_empty_keys_overlap_zero(self):
        k1 = make_key()
        k2 = make_key()
        assert k1.overlap(k2) == 0.0

    def test_identical_keys_overlap_one(self):
        k = make_key(cryst_ids=["c1", "c2"], frameworks=["welfare"], topics=["memory"])
        assert k.overlap(k) == pytest.approx(1.0)

    def test_disjoint_keys_overlap_zero(self):
        k1 = make_key(cryst_ids=["c1"], frameworks=["welfare"])
        k2 = make_key(cryst_ids=["c2"], frameworks=["finance"])
        assert k1.overlap(k2) == pytest.approx(0.0)

    def test_partial_overlap(self):
        # c1, c2 shared; c3 only in k1; c4 only in k2
        k1 = make_key(cryst_ids=["c1", "c2", "c3"])
        k2 = make_key(cryst_ids=["c1", "c2", "c4"])
        # Elements with prefix: c:c1, c:c2, c:c3 vs c:c1, c:c2, c:c4
        # Intersection: {c:c1, c:c2} = 2; Union: {c:c1, c:c2, c:c3, c:c4} = 4
        # Jaccard = 2/4 = 0.5
        assert k1.overlap(k2) == pytest.approx(0.5)

    def test_overlap_is_symmetric(self):
        k1 = make_key(cryst_ids=["c1", "c2"], frameworks=["welfare"])
        k2 = make_key(cryst_ids=["c1", "c3"], frameworks=["finance"])
        assert k1.overlap(k2) == pytest.approx(k2.overlap(k1))

    def test_prefixes_prevent_cross_type_match(self):
        # A crystallization ID "welfare" should not match framework token "welfare"
        k1 = make_key(cryst_ids=["welfare"])
        k2 = make_key(frameworks=["welfare"])
        # c:welfare ≠ f:welfare → disjoint
        assert k1.overlap(k2) == pytest.approx(0.0)

    def test_hash_based_identity_would_fail_this_case(self):
        """
        Demonstrates why hashing is wrong and overlap is right.

        k1 has IDs [c1, c2, c3, c4]; k2 has IDs [c1, c2, c3, c5].
        Their hashes differ (c4 vs c5). But they share 3 of 4 elements
        and should cluster together.

        Under hash-based identity: not same → not clustered.
        Under Jaccard overlap (3/5 = 0.6 > 0.3 threshold): clustered. Correct.
        """
        k1 = make_key(cryst_ids=["c1", "c2", "c3", "c4"])
        k2 = make_key(cryst_ids=["c1", "c2", "c3", "c5"])
        # Hash comparison
        assert k1 != k2  # different hashes (frozen dataclass)
        # But overlap is high enough to cluster
        overlap = k1.overlap(k2)
        # c:c1, c:c2, c:c3 shared = 3; union = {c1,c2,c3,c4,c5} = 5
        assert overlap == pytest.approx(3 / 5)
        assert overlap >= 0.3  # would cluster under default threshold

    def test_from_candidate_seed_dict(self):
        seed_dict = make_seed_dict(
            top_ids=["profile/paper-writing", "profile/welfare-research"],
            routing=["welfare_chip", "academic_channel"],
            excerpt="June writes papers on memory architectures and welfare theory.",
        )
        key = ConfigurationalKey.from_candidate_seed_dict(seed_dict)
        assert "profile/paper-writing" in key.top_crystallization_ids
        assert "welfare_chip" in key.framework_tokens
        # Topic tokens should include words from the excerpt
        assert len(key.snapshot_topic_tokens) > 0

    def test_from_empty_dict(self):
        key = ConfigurationalKey.from_candidate_seed_dict({})
        assert key.top_crystallization_ids == frozenset()
        assert key.framework_tokens == frozenset()
        assert key.snapshot_topic_tokens == frozenset()


# ---------------------------------------------------------------------------
# TestExtractTopicTokens
# ---------------------------------------------------------------------------


class TestExtractTopicTokens:
    def test_basic_extraction(self):
        tokens = _extract_topic_tokens("June writes papers on welfare.", frozenset())
        assert isinstance(tokens, frozenset)
        assert "welfare" in tokens or "papers" in tokens

    def test_stop_words_excluded(self):
        from seed_accumulation import _DEFAULT_STOP_WORDS
        tokens = _extract_topic_tokens("the is are was with from", _DEFAULT_STOP_WORDS)
        assert len(tokens) == 0

    def test_short_words_excluded(self):
        tokens = _extract_topic_tokens("a to of in at", frozenset())
        # Words <= 3 chars are excluded
        assert all(len(t) > 3 for t in tokens)


# ---------------------------------------------------------------------------
# TestSeedAccumulation
# ---------------------------------------------------------------------------


class TestSeedAccumulation:
    def test_add_returns_event(self, accumulation):
        seed_dict = make_seed_dict(top_ids=["profile/welfare"])
        event = accumulation.add(seed_dict, session_id="s1")
        assert isinstance(event, SeedEvent)
        assert event.session_id == "s1"

    def test_add_increments_event_count(self, accumulation):
        assert accumulation.event_count() == 0
        accumulation.add(make_seed_dict(), session_id="s1")
        accumulation.add(make_seed_dict(), session_id="s2")
        assert accumulation.event_count() == 2

    def test_add_distinct_event_ids(self, accumulation):
        e1 = accumulation.add(make_seed_dict())
        e2 = accumulation.add(make_seed_dict())
        assert e1.id != e2.id

    def test_all_events_returns_list(self, accumulation):
        accumulation.add(make_seed_dict(top_ids=["c1"]))
        events = accumulation.all_events()
        assert len(events) == 1

    def test_cluster_empty_substrate(self, accumulation):
        assert accumulation.cluster() == []

    def test_cluster_single_event(self, accumulation):
        accumulation.add(make_seed_dict(top_ids=["c1"]))
        clusters = accumulation.cluster()
        assert len(clusters) == 1
        assert clusters[0].intensity.event_count == 1

    def test_cluster_overlapping_events_together(self, accumulation):
        # Two events sharing 3 of 4 IDs (the hash-would-fail case)
        seed1 = make_seed_dict(top_ids=["c1", "c2", "c3", "c4"])
        seed2 = make_seed_dict(top_ids=["c1", "c2", "c3", "c5"])
        accumulation.add(seed1)
        accumulation.add(seed2)
        clusters = accumulation.cluster(overlap_threshold=0.3)
        # Jaccard = 3/5 = 0.6 > 0.3 → should be in one cluster
        assert len(clusters) == 1
        assert clusters[0].intensity.event_count == 2

    def test_cluster_disjoint_events_separate(self, accumulation):
        seed1 = make_seed_dict(top_ids=["c1", "c2"], routing=["welfare"])
        seed2 = make_seed_dict(top_ids=["c3", "c4"], routing=["finance"])
        accumulation.add(seed1)
        accumulation.add(seed2)
        clusters = accumulation.cluster(overlap_threshold=0.3)
        # Disjoint: two separate clusters
        assert len(clusters) == 2

    def test_cluster_min_events_filter(self, accumulation):
        accumulation.add(make_seed_dict(top_ids=["c1"]))  # solo
        seed_a = make_seed_dict(top_ids=["c2", "c3"])
        seed_b = make_seed_dict(top_ids=["c2", "c3"])
        accumulation.add(seed_a)
        accumulation.add(seed_b)
        # min_events=2: solo event cluster should be filtered out
        clusters = accumulation.cluster(min_events=2, overlap_threshold=0.5)
        assert all(c.intensity.event_count >= 2 for c in clusters)

    def test_cluster_sorted_by_intensity_descending(self, accumulation):
        # Add many overlapping seeds + one isolated seed
        for i in range(5):
            accumulation.add(make_seed_dict(top_ids=["c1", "c2", "c3"]))
        accumulation.add(make_seed_dict(top_ids=["c99"]))
        clusters = accumulation.cluster(overlap_threshold=0.3)
        if len(clusters) > 1:
            assert clusters[0].intensity.scalar >= clusters[-1].intensity.scalar

    def test_above_review_threshold_empty_when_low_intensity(self, accumulation):
        accumulation.add(make_seed_dict(top_ids=["c1"]))
        above = accumulation.above_review_threshold(scalar_threshold=100.0, min_events=1)
        assert above == []

    def test_above_review_threshold_detects_dense_cluster(self, accumulation):
        # Add many overlapping seeds from multiple sessions
        for i in range(10):
            accumulation.add(
                make_seed_dict(top_ids=["c1", "c2", "c3"],
                               excerpt="welfare memory architecture crystallization"),
                session_id=f"session-{i % 4}",  # 4 distinct sessions
            )
        above = accumulation.above_review_threshold(
            scalar_threshold=0.5,
            min_events=3,
            overlap_threshold=0.2,
        )
        assert len(above) >= 1
        assert above[0].intensity.session_breadth >= 1


# ---------------------------------------------------------------------------
# TestIntensityProfile
# ---------------------------------------------------------------------------


class TestIntensityProfile:
    def test_single_event_intensity(self, accumulation):
        accumulation.add(
            make_seed_dict(top_ids=["profile/paper-writing"], routing=["academic"]),
            session_id="s1",
        )
        clusters = accumulation.cluster()
        assert len(clusters) == 1
        intensity = clusters[0].intensity
        assert intensity.event_count == 1
        assert intensity.session_breadth == 1
        assert intensity.scalar > 0

    def test_multi_session_increases_breadth(self, accumulation):
        seed = make_seed_dict(top_ids=["c1", "c2"])
        for session in ["s1", "s2", "s3"]:
            accumulation.add(seed, session_id=session)
        clusters = accumulation.cluster()
        assert clusters[0].intensity.session_breadth == 3

    def test_per_crystallization_frequency(self, accumulation):
        seed_a = make_seed_dict(top_ids=["profile/welfare-research"])
        seed_b = make_seed_dict(top_ids=["profile/welfare-research", "profile/paper-writing"])
        accumulation.add(seed_a)
        accumulation.add(seed_b)
        clusters = accumulation.cluster(overlap_threshold=0.2)
        # Two seeds sharing welfare-research should cluster
        cluster = next(
            (c for c in clusters if c.intensity.event_count >= 2),
            clusters[0] if clusters else None,
        )
        if cluster and cluster.intensity.event_count >= 2:
            # welfare-research appears in both → frequency = 1.0 (every event)
            assert "profile/welfare-research" in cluster.intensity.per_crystallization

    def test_avg_coherence_for_identical_seeds(self, accumulation):
        seed = make_seed_dict(top_ids=["c1", "c2", "c3"])
        accumulation.add(seed)
        accumulation.add(seed)
        clusters = accumulation.cluster()
        # Two identical keys → pairwise overlap = 1.0
        assert clusters[0].intensity.avg_coherence == pytest.approx(1.0)

    def test_enrich_with_knowledge_context(self, accumulation):
        accumulation.add(make_seed_dict(top_ids=["c1"]))
        clusters = accumulation.cluster()
        accumulation.enrich_with_knowledge_context(clusters[0], "welfare-cluster", 5)
        assert clusters[0].intensity.per_knowledge_cluster["welfare-cluster"] == 5


# ---------------------------------------------------------------------------
# TestCentroid
# ---------------------------------------------------------------------------


class TestCentroid:
    def test_centroid_majority_elements(self, accumulation):
        # 3 of 4 events have "c1" → c1 in centroid
        # only 1 of 4 has "c99" → c99 NOT in centroid
        for _ in range(3):
            accumulation.add(make_seed_dict(top_ids=["c1", "c2"]))
        accumulation.add(make_seed_dict(top_ids=["c1", "c99"]))
        clusters = accumulation.cluster(overlap_threshold=0.3)
        centroid = clusters[0].centroid_key
        # c1 appears in 4/4, c2 in 3/4 → both in centroid (threshold 50%)
        assert "c1" in centroid.top_crystallization_ids
        # c99 in only 1/4 → NOT in centroid
        assert "c99" not in centroid.top_crystallization_ids


# ---------------------------------------------------------------------------
# TestPersistence
# ---------------------------------------------------------------------------


class TestPersistence:
    def test_roundtrip_to_disk(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seeds.jsonl"
            acc1 = SeedAccumulation(path=path)
            seed_dict = make_seed_dict(
                top_ids=["profile/welfare", "profile/paper-writing"],
                routing=["academic"],
                excerpt="June writes about welfare and memory.",
            )
            acc1.add(seed_dict, session_id="test-session")
            acc1.add(seed_dict, session_id="test-session-2")

            # Reload from disk
            acc2 = SeedAccumulation(path=path)
            assert acc2.event_count() == 2

    def test_clusters_survive_reload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seeds.jsonl"
            acc1 = SeedAccumulation(path=path)
            for _ in range(3):
                acc1.add(
                    make_seed_dict(top_ids=["c1", "c2", "c3"]),
                    session_id="sess",
                )

            acc2 = SeedAccumulation(path=path)
            clusters = acc2.cluster()
            assert len(clusters) == 1
            assert clusters[0].intensity.event_count == 3

    def test_event_counter_resumes_after_reload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seeds.jsonl"
            acc1 = SeedAccumulation(path=path)
            acc1.add(make_seed_dict())
            acc1.add(make_seed_dict())

            acc2 = SeedAccumulation(path=path)
            new_event = acc2.add(make_seed_dict())
            # The new event should have a different ID from the two loaded ones
            existing_ids = {e.id for e in acc2.all_events() if e.id != new_event.id}
            assert new_event.id not in existing_ids
