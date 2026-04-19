# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for matcher_step_2d.py.

Verifies:
- Signal scoring: context_signal hit activates; no hit produces CandidateSeed
- Anti-signal penalty: reduces score; alone clamps score to zero
- User-invocation boost: profile name in invocation phrase fires boost
- Routing-context affinity: routing_context_signals + task_affinity add score
- FoundationalCommitments excluded from scoring (scope=ALWAYS)
- Multiple activations sorted by score; max_active caps results
- Aux-LLM threshold reapplication: demoted score below threshold is removed
- ContextSnapshot builder: exchange_buffer parsing, invocation detection
"""
import pytest

from crystallization_types import (
    build_emergent_touchstone,
    build_foundational_commitment,
    build_prescriptive_profile,
)
from matcher_step_2d import (
    ANTI_SIGNAL_PENALTY,
    DEFAULT_ACTIVATION_THRESHOLD,
    ROUTING_SIGNAL_WEIGHT,
    USER_INVOCATION_BOOST,
    ActivationSet,
    CandidateSeed,
    ContextSnapshot,
    CrystallizationMatcher,
    build_snapshot_from_exchange_buffer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _profile(
    name,
    pid=None,
    signals=None,
    anti_signals=None,
    task_affinity=None,
    register=None,
):
    return build_prescriptive_profile(
        profile_id=pid or f"prescriptive-profile/{name.lower().replace(' ', '-')}",
        name=name,
        recipe=f"Recipe for {name}.",
        stance_description=f"Stance for {name}.",
        context_signals=signals or [f"{name.lower()} signal"],
        anti_signals=anti_signals,
        task_affinity=task_affinity,
        register=register,
    )


def _snapshot(texts=None, invocations=None, routing=None, files=None, register=None):
    return ContextSnapshot(
        exchange_texts=texts or [],
        user_invocation_phrases=invocations or [],
        routing_context_signals=routing or [],
        active_files=files or [],
        affective_register_hint=register,
    )


def _matcher(substrate, threshold=None, max_active=4, aux_llm_fn=None):
    return CrystallizationMatcher(
        substrate=substrate,
        activation_threshold=threshold if threshold is not None else DEFAULT_ACTIVATION_THRESHOLD,
        max_active=max_active,
        aux_llm_fn=aux_llm_fn,
    )


# ---------------------------------------------------------------------------
# Signal scoring
# ---------------------------------------------------------------------------


class TestMatcherBasicScoring:
    def test_context_signal_hit_activates(self, substrate):
        profile = _profile("Hypothesis Test", signals=["hypothesis testing"])
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["Let us run a hypothesis testing loop."]))
        assert len(result.activations) == 1
        assert result.activations[0].payload.crystallization_id == profile.id
        assert result.candidate_seed is None

    def test_no_matching_signals_produces_candidate_seed(self, substrate):
        profile = _profile("Niche Profile", signals=["very specific niche signal xyz"])
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["Completely unrelated conversation."]))
        assert len(result.activations) == 0
        assert isinstance(result.candidate_seed, CandidateSeed)

    def test_candidate_seed_carries_top_scores(self, substrate):
        profile = _profile("Almost Profile", signals=["very niche signal abc"])
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["Unrelated."]))
        assert result.candidate_seed is not None
        assert isinstance(result.candidate_seed.top_scores, list)

    def test_empty_substrate_produces_candidate_seed(self, substrate):
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["Hello."]))
        assert result.candidate_seed is not None
        assert result.activations == []

    def test_signal_score_normalised_by_total(self, substrate):
        # 4 signals, 1 matches: signal_score = 0.25 = threshold → activates
        profile = _profile(
            "Threshold Profile",
            signals=["matching signal", "absent one", "absent two", "absent three"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate, threshold=0.25)
        result = matcher.match(_snapshot(texts=["matching signal found here"]))
        assert len(result.activations) == 1


class TestMatcherAntiSignal:
    def test_anti_signal_reduces_score(self, substrate):
        profile = _profile(
            "Penalised",
            signals=["geometry"],
            anti_signals=["explicit refusal"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        # Both signal and anti-signal hit: score = 1.0 - 0.35 = 0.65
        result = matcher.match(
            _snapshot(texts=["geometry exploration; explicit refusal encountered"])
        )
        assert len(result.activations) == 1
        act = result.activations[0]
        assert act.score == pytest.approx(1.0 - ANTI_SIGNAL_PENALTY, abs=1e-9)
        assert "explicit refusal" in act.matched_anti_signals

    def test_anti_signal_alone_clamps_to_zero_produces_seed(self, substrate):
        profile = _profile(
            "Anti Only",
            signals=["absent signal xyz"],
            anti_signals=["blocking keyword"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["blocking keyword in context"]))
        assert len(result.activations) == 0
        assert result.candidate_seed is not None

    def test_score_breakdown_contains_anti_penalty(self, substrate):
        profile = _profile(
            "Breakdown Check",
            signals=["data analysis"],
            anti_signals=["shutdown"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["data analysis needed; shutdown flag"]))
        act = result.activations[0]
        assert act.score_breakdown["anti_signal_penalty"] == pytest.approx(
            -ANTI_SIGNAL_PENALTY, abs=1e-9
        )


# ---------------------------------------------------------------------------
# User-invocation boost
# ---------------------------------------------------------------------------


class TestMatcherUserInvocationBoost:
    def test_invocation_phrase_containing_profile_name_boosts(self, substrate):
        # No context signals match, but name in invocation phrase → boost fires
        profile = _profile(
            "Research Depth",
            signals=["absent signal xyz"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(
            _snapshot(
                texts=["Hello."],
                invocations=["inhabit this position: Research Depth"],
            )
        )
        assert len(result.activations) == 1
        act = result.activations[0]
        assert act.score_breakdown["user_invocation_boost"] == pytest.approx(
            USER_INVOCATION_BOOST, abs=1e-9
        )

    def test_invocation_phrase_containing_profile_id_boosts(self, substrate):
        profile = _profile(
            "Custom Profile",
            pid="prescriptive-profile/custom-id-target",
            signals=["absent xyz"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(
            _snapshot(
                texts=["routine message"],
                invocations=["load the profile: prescriptive-profile/custom-id-target"],
            )
        )
        assert len(result.activations) == 1

    def test_unrelated_invocation_phrase_no_boost(self, substrate):
        profile = _profile("Specific Profile", signals=["absent xyz"])
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(
            _snapshot(
                texts=["routine"],
                invocations=["inhabit this position: Some Other Profile"],
            )
        )
        assert len(result.activations) == 0


# ---------------------------------------------------------------------------
# Routing context / task affinity
# ---------------------------------------------------------------------------


class TestMatcherRoutingContext:
    def test_routing_signal_acts_as_tiebreaker(self, substrate):
        # 5 signals, 1 matches → signal_score = 0.20 < threshold (0.25).
        # Routing affinity fires (+0.15) → total = 0.35 → activates.
        # Without routing, the same profile would fall below threshold.
        profile = _profile(
            "Affinity Tiebreak",
            signals=["one match", "absent a", "absent b", "absent c", "absent d"],
            task_affinity=["research"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate, threshold=0.25)
        result = matcher.match(
            _snapshot(texts=["one match here"], routing=["deep research mode active"])
        )
        assert len(result.activations) == 1
        act = result.activations[0]
        assert act.score_breakdown["affinity_alignment"] >= ROUTING_SIGNAL_WEIGHT

    def test_routing_miss_adds_no_affinity(self, substrate):
        profile = _profile(
            "Affinity Miss",
            signals=["one match", "absent a", "absent b", "absent c", "absent d"],
            task_affinity=["research"],
        )
        substrate.save(profile.record)
        matcher = _matcher(substrate, threshold=0.25)
        # Signal-only score = 0.20 < threshold; routing misses → no activation
        result = matcher.match(
            _snapshot(texts=["one match here"], routing=["unrelated context"])
        )
        assert len(result.activations) == 0


# ---------------------------------------------------------------------------
# FoundationalCommitments excluded
# ---------------------------------------------------------------------------


class TestMatcherFoundationalCommitmentsExcluded:
    def test_foundational_commitment_never_scored(self, substrate):
        fc = build_foundational_commitment(
            commitment_id="foundational-commitment/test-fc",
            name="Test FC",
            recipe="Always active.",
        )
        substrate.save(fc.record)
        matcher = _matcher(substrate)
        # haystack contains everything — if FC were scored, signals would match
        result = matcher.match(_snapshot(texts=["Test FC always active commitment"]))
        assert len(result.activations) == 0
        assert result.candidate_seed is not None

    def test_fc_and_profile_together_only_profile_scored(self, substrate):
        fc = build_foundational_commitment(
            commitment_id="foundational-commitment/fc-mixed",
            name="FC Mixed",
            recipe="FC recipe.",
        )
        profile = _profile("Mixed Profile", signals=["mixed signal"])
        substrate.save(fc.record)
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["mixed signal context"]))
        assert len(result.activations) == 1
        assert result.activations[0].payload.crystallization_id == profile.id


# ---------------------------------------------------------------------------
# Multiple activations, sorting, max_active
# ---------------------------------------------------------------------------


class TestMatcherMultipleActivations:
    def test_multiple_profiles_can_activate(self, substrate):
        p1 = _profile("Alpha", signals=["alpha signal"])
        p2 = _profile("Beta", signals=["beta signal"])
        substrate.save(p1.record)
        substrate.save(p2.record)
        matcher = _matcher(substrate)
        result = matcher.match(
            _snapshot(texts=["alpha signal and beta signal both present"])
        )
        assert len(result.activations) == 2

    def test_activations_sorted_by_score_descending(self, substrate):
        # p1: 2/2 signals = 1.0; p2: 1/4 signals = 0.25
        p1 = _profile("High Score", signals=["high one", "high two"])
        p2 = _profile(
            "Low Score",
            pid="prescriptive-profile/low",
            signals=["low one", "low two", "low three", "low four"],
        )
        substrate.save(p1.record)
        substrate.save(p2.record)
        matcher = _matcher(substrate, threshold=0.25)
        result = matcher.match(
            _snapshot(texts=["high one and high two; low one present"])
        )
        assert len(result.activations) == 2
        assert result.activations[0].score >= result.activations[1].score

    def test_max_active_caps_results(self, substrate):
        for i in range(3):
            p = _profile(f"Profile {i}", signals=[f"signal {i}"])
            substrate.save(p.record)
        matcher = _matcher(substrate, max_active=2)
        result = matcher.match(
            _snapshot(texts=["signal 0 signal 1 signal 2"])
        )
        assert len(result.activations) <= 2

    def test_candidate_seed_absent_when_any_activation_passes(self, substrate):
        profile = _profile("Active", signals=["present signal"])
        substrate.save(profile.record)
        matcher = _matcher(substrate)
        result = matcher.match(_snapshot(texts=["present signal found"]))
        assert result.candidate_seed is None


# ---------------------------------------------------------------------------
# Aux-LLM threshold reapplication
# ---------------------------------------------------------------------------


class TestAuxLlmRefinement:
    def test_threshold_reapplied_after_aux_llm_demotion(self, substrate):
        # 4 signals, 1 match → score = 0.25 (exactly at threshold)
        # aux-LLM returns "unfits" → score -= 0.2 → 0.05 → below threshold → removed
        profile = _profile(
            "Threshold Edge",
            signals=["one match", "absent a", "absent b", "absent c"],
        )
        substrate.save(profile.record)

        def demoting_llm(prompt: str) -> str:
            return "unfits — stance does not align with exchange"

        matcher = _matcher(substrate, threshold=0.25, aux_llm_fn=demoting_llm)
        result = matcher.match(_snapshot(texts=["one match present"]))
        assert len(result.activations) == 0
        assert result.candidate_seed is not None

    def test_aux_llm_boost_keeps_activation(self, substrate):
        profile = _profile(
            "Boost Edge",
            signals=["relevant term"],
        )
        substrate.save(profile.record)

        def boosting_llm(prompt: str) -> str:
            return "fits — stance clearly matches the current exchange"

        matcher = _matcher(substrate, aux_llm_fn=boosting_llm)
        result = matcher.match(_snapshot(texts=["relevant term in context"]))
        assert len(result.activations) == 1
        assert result.activations[0].score > 1.0 - 1e-9 or result.activations[0].score >= 1.0

    def test_aux_llm_failure_preserves_pattern_match_score(self, substrate):
        profile = _profile("Resilient", signals=["resilient signal"])
        substrate.save(profile.record)

        def crashing_llm(prompt: str) -> str:
            raise RuntimeError("aux LLM unavailable")

        matcher = _matcher(substrate, aux_llm_fn=crashing_llm)
        result = matcher.match(_snapshot(texts=["resilient signal present"]))
        assert len(result.activations) == 1

    def test_no_aux_llm_no_reapplication_path(self, substrate):
        profile = _profile("No Aux", signals=["plain signal"])
        substrate.save(profile.record)
        matcher = _matcher(substrate, aux_llm_fn=None)
        result = matcher.match(_snapshot(texts=["plain signal context"]))
        assert len(result.activations) == 1


# ---------------------------------------------------------------------------
# ContextSnapshot builder
# ---------------------------------------------------------------------------


class TestSnapshotBuilder:
    def _exchange(self, user_text="", assistant_text=""):
        class _Ex:
            user_prompt_preview = user_text
            assistant_response = assistant_text
        return _Ex()

    def test_recent_n_exchanges_respected(self):
        buffer = [self._exchange(f"message {i}") for i in range(10)]
        snapshot = build_snapshot_from_exchange_buffer(buffer, recent_n=3)
        assert len(snapshot.exchange_texts) == 3

    def test_exchange_texts_populated_from_buffer(self):
        buffer = [self._exchange("user says hello", "assistant responds")]
        snapshot = build_snapshot_from_exchange_buffer(buffer)
        assert any("user says hello" in t for t in snapshot.exchange_texts)

    def test_invocation_phrase_extracted(self):
        buffer = [self._exchange("inhabit this position: Research Mode")]
        snapshot = build_snapshot_from_exchange_buffer(buffer)
        assert len(snapshot.user_invocation_phrases) == 1
        assert "Research Mode" in snapshot.user_invocation_phrases[0]

    def test_no_invocation_phrases_when_absent(self):
        buffer = [self._exchange("just a normal question")]
        snapshot = build_snapshot_from_exchange_buffer(buffer)
        assert snapshot.user_invocation_phrases == []

    def test_routing_context_signals_passed_through(self):
        buffer = [self._exchange("hello")]
        snapshot = build_snapshot_from_exchange_buffer(
            buffer, routing_context_signals=["research-deep"]
        )
        assert "research-deep" in snapshot.routing_context_signals

    def test_empty_buffer_produces_empty_snapshot(self):
        snapshot = build_snapshot_from_exchange_buffer([])
        assert snapshot.exchange_texts == []
        assert snapshot.user_invocation_phrases == []
