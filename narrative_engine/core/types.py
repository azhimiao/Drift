"""Shared types for the autonomous narrative engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventKind(str, Enum):
    WORLD_DRIFT = "world_drift"
    CONFLICT_SPAWN = "conflict_spawn"
    AGENT_ACTION = "agent_action"
    SKILL_EVOLVE = "skill_evolve"
    WORLD_REACT = "world_react"
    CRISIS = "crisis"
    TRUST_SHIFT = "trust_shift"
    MEMORY_FADE = "memory_fade"
    # DRIFT game
    AGENT_LOG = "agent_log"
    AGENT_THOUGHT = "agent_thought"
    EXPLORE = "explore"
    CLUE_FOUND = "clue_found"
    RULE_SHIFT = "rule_shift"
    LOCATION_UNLOCK = "location_unlock"
    LAYER_SHIFT = "layer_shift"
    DRIFT_SURGE = "drift_surge"
    SKILL_FORK = "skill_fork"
    WORLD_ADAPT = "world_adapt"
    CHAPTER = "chapter"
    OBSERVER_REVEAL = "observer_reveal"
    SYSTEM_NOTICE = "system_notice"
    PHASE_END = "phase_end"
    ENDING = "ending"


@dataclass
class Event:
    tick: int
    kind: EventKind
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"tick": self.tick, "kind": self.kind.value, "payload": self.payload}


@dataclass
class Skill:
    id: str
    name: str
    version: int = 1
    potency: float = 0.5
    tags: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        base = self.id.split("_")[0] if "_" in self.id else self.id
        return f"{base}_v{self.version}" if self.version > 1 else self.id

    def mutate(self, reason: str) -> Skill:
        tag_map = {
            "deception": "trust_risk",
            "memory": "archive",
            "broadcast": "voice",
            "lighthouse": "navigation",
            "negotiate": "faction",
            "archive": "history",
        }
        base_id = self.id.split("_")[0]
        new_version = self.version + 1
        new_id = f"{base_id}_v{new_version}"
        return Skill(
            id=new_id,
            name=self.name,
            version=new_version,
            potency=min(1.0, self.potency + 0.15),
            tags=self.tags + [tag_map.get(base_id, "adapted")],
        )


@dataclass
class Faction:
    id: str
    name: str
    trust: dict[str, float] = field(default_factory=dict)
    pressure: float = 0.3
    resources: float = 0.5

    def trust_toward(self, other_id: str, default: float = 0.5) -> float:
        return self.trust.get(other_id, default)


@dataclass
class WorldState:
    tick: int = 0
    seed_id: str = "default"
    display_name: str = "漂移聚落"
    narrative_title: str = "漂移纪事"
    causality_stability: float = 0.7
    narrative_pressure: float = 0.4
    veil_density: float = 0.3
    active_crises: list[str] = field(default_factory=list)
    crisis_pool: list[str] = field(default_factory=list)
    conflict_templates: list[dict] = field(default_factory=list)
    factions: dict[str, Faction] = field(default_factory=dict)
    global_memory_index: float = 1.0
    drift_log: list[str] = field(default_factory=list)

    def faction_ids(self) -> list[str]:
        return list(self.factions.keys())


@dataclass
class AgentState:
    id: str
    name: str
    faction_id: str
    goals: list[str]
    skills: list[Skill]
    memory: list[str] = field(default_factory=list)
    stress: float = 0.2
    last_action: str | None = None
