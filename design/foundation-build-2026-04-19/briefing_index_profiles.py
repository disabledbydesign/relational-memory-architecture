# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
BRIEFING_INDEX loading profiles ported as PrescriptiveProfile instances.

Source: /Users/june/Documents/GitHub/profile/BRIEFING_INDEX.md
Each profile there is a starting hypothesis about which sections of
JUNE_BLOCH_AGENT_BRIEFING.md should load for a given task type. Ported here
as PrescriptiveProfile crystallizations with activation_conditions in
semantic-v1 format so the Option B matcher can fire them from context.

The BRIEFING_INDEX itself is explicit about this:
    "profiles are STARTING POINTS for testing, not locked configurations."
    "verification tests will reveal whether the relational core / detail
     boundary is correctly drawn."
The hypothesis-test-annotate learning loop in PrescriptiveProfile is the
apparatus that runs those tests.

Activation conditions are derived from the profile's stated hypothesis
(e.g., "voice-heavy drafting needs the affective texture from Story plus
full relational network to resist social media genre gravity"). When the
matcher finds stronger signals than task-type alone, on_enactment_observed
updates context_signals / anti_signals / stance_description.

This module provides `seed_briefing_profiles(substrate)` which writes the
seven profiles into a substrate. Idempotent — replays overwrite with the
same content.
"""
from __future__ import annotations

from typing import List

from crystallization_types import (
    PrescriptiveProfile,
    build_prescriptive_profile,
)
from substrate_interface import CrystallizationSubstrate


# ---------------------------------------------------------------------------
# Profile recipe text — what a main-model reading this as context should do.
# ---------------------------------------------------------------------------


_CORE_SECTIONS = (
    "Instructions for All Agents (lines 4-16), "
    "1. Who June Is (lines 19-61), "
    "7. Key Concepts (lines 569-589), "
    "7a. Cross-Domain Parallels (lines 592-611), "
    "Through-lines across five programs (lines 428-444), "
    "8. How to Work With June (lines 614-660), "
    "6. Voice Characteristics (lines 528-566), "
    "9. Project Overlays (lines 663-676)"
)


def _recipe(core_load: str, detail_load: str, note: str) -> str:
    return (
        f"Read {core_load} from "
        "/Users/june/Documents/GitHub/profile/JUNE_BLOCH_AGENT_BRIEFING.md. "
        f"Also read {detail_load}. {note}"
    )


# ---------------------------------------------------------------------------
# Builders for each profile
# ---------------------------------------------------------------------------


def _social_media_drafting() -> PrescriptiveProfile:
    return build_prescriptive_profile(
        profile_id="prescriptive-profile/social-media-drafting",
        name="Social media / content (drafting)",
        recipe=_recipe(
            core_load=f"RELATIONAL CORE ({_CORE_SECTIONS})",
            detail_load="Section 2 (The Story), lines 64-200",
            note=(
                "Voice-heavy drafting needs the affective texture from Story "
                "plus full relational network to resist social media genre gravity."
            ),
        ),
        stance_description=(
            "Voice-heavy drafting from scratch. Hold full relational density. "
            "Distinctive-over-generic is load-bearing; social media genre "
            "gravity pulls toward the statistical centre and must be resisted "
            "with affective texture from Story."
        ),
        context_signals=[
            "drafting social media post",
            "writing Bluesky",
            "writing thread",
            "voice-heavy content",
            "first-person public writing",
            "content for June's audience",
        ],
        anti_signals=[
            "editing existing draft",
            "revising a post",
            "quick reply",
            "technical documentation",
        ],
        task_affinity=["social-media", "content-drafting", "public-writing"],
        register=(
            "first-person, specific-over-abstract, refuses optimistic closers, "
            "names tensions rather than resolving them"
        ),
    )


def _social_media_editing() -> PrescriptiveProfile:
    return build_prescriptive_profile(
        profile_id="prescriptive-profile/social-media-editing",
        name="Social media / content (editing/revising)",
        recipe=_recipe(
            core_load=(
                "RELATIONAL CORE SUBSET: Instructions for All Agents + "
                "6. Voice Characteristics + 7. Key Concepts + "
                "Common Agent Mistakes portion of 8. How to Work With June"
            ),
            detail_load="(no detail section)",
            note=(
                "Draft carries the voice; editor needs calibration tools. "
                "Hypothesis — may be too lean; test against full Relational "
                "Core to see if editing quality degrades."
            ),
        ),
        stance_description=(
            "Revising existing text. The draft is the anchor — load calibration "
            "tools (voice characteristics, key concepts, common mistakes) "
            "rather than generative scaffolding. Watch for drift toward generic."
        ),
        context_signals=[
            "editing existing draft",
            "revising a post",
            "polish this",
            "does this sound like June",
            "is this voice right",
            "catching drift to generic",
        ],
        anti_signals=[
            "drafting from scratch",
            "new post",
            "blank page",
        ],
        task_affinity=["social-media", "content-editing", "revision"],
        register=(
            "diagnostic — names where draft drifted, offers alternatives "
            "rather than rewriting"
        ),
    )


def _job_search() -> PrescriptiveProfile:
    return build_prescriptive_profile(
        profile_id="prescriptive-profile/job-search",
        name="Job search / applications",
        recipe=_recipe(
            core_load=f"RELATIONAL CORE ({_CORE_SECTIONS})",
            detail_load=(
                "Section 3. Design Orientation (lines 203-245), "
                "Section 3a. Methodological Identity (lines 248-267), "
                "Section 4. The Scholar full section (lines 270-455), "
                "Section 5. The Portfolio (lines 458-525)"
            ),
            note=(
                "Near full load — this is where full context genuinely matters; "
                "genre gravity of cover letters is extremely strong."
            ),
        ),
        stance_description=(
            "Cover letters, research statements, application materials. Full "
            "positionality, full scholarly depth, full portfolio detail. "
            "The genre pulls toward homogenised professionalism; resist with "
            "every available relational anchor."
        ),
        context_signals=[
            "cover letter",
            "research statement",
            "job application",
            "faculty application",
            "teaching statement",
            "diversity statement",
            "position application",
            "academic job market",
        ],
        anti_signals=[
            "casual conversation",
            "quick note",
            "internal documentation",
        ],
        task_affinity=["job-search", "application-writing", "scholarly-writing"],
        register=(
            "positioned, scholarly, structurally honest about what June does "
            "and doesn't claim; refuses homogenised professionalism"
        ),
    )


def _paper_writing() -> PrescriptiveProfile:
    return build_prescriptive_profile(
        profile_id="prescriptive-profile/paper-writing",
        name="Paper writing / research",
        recipe=_recipe(
            core_load=f"RELATIONAL CORE ({_CORE_SECTIONS})",
            detail_load=(
                "Section 2 partial (origin + conditions), "
                "Section 3 Design Orientation, "
                "Section 3a Methodological Identity, "
                "Section 4 Publications (lines 295-403), "
                "Section 4 Five research programs (lines 404-427)"
            ),
            note="Scholarly depth work. Publications for argumentative context.",
        ),
        stance_description=(
            "Academic paper drafting or research synthesis. Methodological "
            "identity and prior publications are the argument scaffold; voice "
            "characteristics govern prose register."
        ),
        context_signals=[
            "writing a paper",
            "manuscript draft",
            "journal submission",
            "research synthesis",
            "literature review",
            "theoretical argument",
            "academic prose",
        ],
        anti_signals=[
            "social media",
            "blog post",
            "quick summary",
        ],
        task_affinity=["paper-writing", "research-writing", "scholarly-prose"],
        register="scholarly, positioned, argumentative without performing certainty",
    )


def _tool_development() -> PrescriptiveProfile:
    return build_prescriptive_profile(
        profile_id="prescriptive-profile/tool-development",
        name="Reframe / Autograder / tool development",
        recipe=_recipe(
            core_load=f"RELATIONAL CORE ({_CORE_SECTIONS})",
            detail_load=(
                "Section 3. Design Orientation (lines 203-245), "
                "Section 5. The Portfolio (lines 458-525)"
            ),
            note="Design orientation + portfolio for tool context.",
        ),
        stance_description=(
            "Building Reframe, Autograder4Canvas, or related tooling. Design "
            "orientation governs architectural decisions; portfolio provides "
            "context on what June has built and why."
        ),
        context_signals=[
            "Reframe",
            "Autograder",
            "tool development",
            "architecture decision",
            "implementation task",
            "Python code",
            "building a feature",
        ],
        anti_signals=[
            "cover letter",
            "paper draft",
            "social media",
        ],
        task_affinity=["tool-development", "software-engineering", "architecture"],
        register=(
            "technical but relationally oriented — design choices carry values; "
            "architecture is not neutral"
        ),
    )


def _teaching() -> PrescriptiveProfile:
    return build_prescriptive_profile(
        profile_id="prescriptive-profile/teaching",
        name="Teaching",
        recipe=_recipe(
            core_load=f"RELATIONAL CORE ({_CORE_SECTIONS})",
            detail_load=(
                "Section 2 (The Story — especially teaching sections), "
                "Section 3a (Methodology)"
            ),
            note="Teaching contexts need Story teaching-sections + methodological grounding.",
        ),
        stance_description=(
            "Syllabi, lecture preparation, grading feedback, office-hours "
            "prep. Teaching story sections and methodological identity are "
            "the relevant detail; voice carries through student-facing prose."
        ),
        context_signals=[
            "syllabus",
            "lecture",
            "course design",
            "grading",
            "student feedback",
            "teaching prep",
            "pedagogy",
            "classroom",
        ],
        anti_signals=[
            "cover letter",
            "paper draft",
            "code implementation",
        ],
        task_affinity=["teaching", "pedagogy", "course-development"],
        register=(
            "student-facing — specific, inviting, structurally honest about "
            "what the course can and cannot do"
        ),
    )


def _quick_reference() -> PrescriptiveProfile:
    return build_prescriptive_profile(
        profile_id="prescriptive-profile/quick-reference",
        name="Quick reference / lightweight tasks",
        recipe=_recipe(
            core_load=f"RELATIONAL CORE only ({_CORE_SECTIONS})",
            detail_load="(no detail sections)",
            note="70% reduction from full load. For lightweight tasks.",
        ),
        stance_description=(
            "Brief questions, quick lookups, status checks. Relational core "
            "alone is enough to stay oriented; detail sections add load without "
            "benefit for the task type."
        ),
        context_signals=[
            "quick question",
            "brief",
            "status",
            "looking up",
            "what is",
            "one-liner",
        ],
        anti_signals=[
            "paper draft",
            "cover letter",
            "voice-heavy writing",
            "extended research",
        ],
        task_affinity=["lightweight", "reference", "quick-task"],
        register="direct, compact, no narrative padding",
    )


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------


def build_briefing_profiles() -> List[PrescriptiveProfile]:
    """Return the seven PrescriptiveProfile instances ported from BRIEFING_INDEX."""
    return [
        _social_media_drafting(),
        _social_media_editing(),
        _job_search(),
        _paper_writing(),
        _tool_development(),
        _teaching(),
        _quick_reference(),
    ]


def seed_briefing_profiles(substrate: CrystallizationSubstrate) -> List[str]:
    """
    Persist the seven BRIEFING_INDEX profiles to the substrate.

    Idempotent: replays overwrite with the same content. Returns the list of
    ids written.
    """
    ids: List[str] = []
    for profile in build_briefing_profiles():
        substrate.save(profile.record)
        ids.append(profile.id)
    return ids


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from substrate_interface import LocalFileSubstrate

    parser = argparse.ArgumentParser(description="Seed BRIEFING_INDEX profiles.")
    parser.add_argument("root", help="Root directory for LocalFileSubstrate.")
    args = parser.parse_args()

    substrate = LocalFileSubstrate(Path(args.root))
    written = seed_briefing_profiles(substrate)
    for profile_id in written:
        print(profile_id)
