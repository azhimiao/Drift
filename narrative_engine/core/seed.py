"""World seed loader — engine-native bootstrap. No external scenario packs."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

from .types import AgentState, Faction, Skill, WorldState


@dataclass
class WorldSeed:
    seed_id: str
    display_name: str
    narrative_title: str
    factions: list[dict]
    agents: list[dict]
    skill_verbs: dict[str, list[str]]
    skill_affinity: dict[str, list[str]]
    crises: list[str]
    conflicts: list[dict]


def default_seed_path() -> Path:
    return Path(__file__).resolve().parent.parent / "seeds" / "default.json"


def load_seed(path: Path | None = None) -> WorldSeed:
    p = path or default_seed_path()
    data = json.loads(p.read_text(encoding="utf-8"))
    return WorldSeed(
        seed_id=data["seed_id"],
        display_name=data["display_name"],
        narrative_title=data["narrative_title"],
        factions=data["factions"],
        agents=data["agents"],
        skill_verbs=data["skill_verbs"],
        skill_affinity=data["skill_affinity"],
        crises=data["crises"],
        conflicts=data["conflicts"],
    )


def bootstrap_world(seed: WorldSeed, rng: random.Random) -> WorldState:
    factions: dict[str, Faction] = {}
    for spec in seed.factions:
        factions[spec["id"]] = Faction(
            id=spec["id"],
            name=spec["name"],
            pressure=spec.get("pressure", 0.3),
            resources=spec.get("resources", 0.5),
        )
    ids = list(factions.keys())
    for a in ids:
        for b in ids:
            if a != b:
                factions[a].trust[b] = rng.uniform(0.35, 0.75)

    return WorldState(
        seed_id=seed.seed_id,
        display_name=seed.display_name,
        narrative_title=seed.narrative_title,
        factions=factions,
        crisis_pool=list(seed.crises),
        conflict_templates=list(seed.conflicts),
        veil_density=rng.uniform(0.2, 0.5),
        narrative_pressure=rng.uniform(0.3, 0.5),
        causality_stability=rng.uniform(0.55, 0.85),
    )


def bootstrap_agents(seed: WorldSeed, rng: random.Random) -> list[AgentState]:
    agents: list[AgentState] = []
    for spec in seed.agents:
        skills = [
            Skill(id=s, name=s, potency=rng.uniform(0.35, 0.65))
            for s in spec["skills"]
        ]
        agents.append(
            AgentState(
                id=spec["id"],
                name=spec["name"],
                faction_id=spec["faction"],
                goals=list(spec["goals"]),
                skills=skills,
            )
        )
    return agents
