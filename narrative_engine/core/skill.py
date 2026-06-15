"""Skill evolution engine — failure mutates, success reinforces."""

from __future__ import annotations

import random

from .seed import WorldSeed
from .types import AgentState, Skill, WorldState


def choose_skill(
    agent: AgentState, world: WorldState, seed: WorldSeed, rng: random.Random
) -> Skill:
    scored: list[tuple[float, Skill]] = []
    affinity = seed.skill_affinity

    for skill in agent.skills:
        base = skill.id.split("_")[0]
        score = skill.potency
        for goal in agent.goals:
            for kw in affinity.get(base, []):
                if kw in goal:
                    score += 0.2
        if world.narrative_pressure > 0.6 and base in ("negotiate", "deception"):
            score += 0.15
        if world.global_memory_index < 0.5 and base in ("memory", "archive"):
            score += 0.2
        if world.veil_density > 0.6 and base == "beacon":
            score += 0.2
        scored.append((score + rng.uniform(0, 0.1), skill))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


def evolve_skill(skill: Skill, success: bool, rng: random.Random) -> Skill:
    if success:
        if rng.random() < 0.25:
            return Skill(
                id=skill.id,
                name=skill.name,
                version=skill.version,
                potency=min(1.0, skill.potency + 0.08),
                tags=skill.tags,
            )
        return skill

    if rng.random() < 0.55:
        return skill.mutate("failure")
    return skill
