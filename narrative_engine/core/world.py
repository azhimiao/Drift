"""Layer 1 — World generator: drift, crises, reactions."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .types import Event, EventKind, WorldState

if TYPE_CHECKING:
    from .agent import Agent


def drift_world(world: WorldState, rng: random.Random) -> list[Event]:
    events: list[Event] = []
    world.tick += 1
    tick = world.tick

    instability = 1.0 - world.causality_stability
    world.veil_density = max(0.0, min(1.0, world.veil_density + rng.uniform(-0.08, 0.12)))
    world.causality_stability = max(0.1, min(1.0, world.causality_stability + rng.uniform(-0.06, 0.04)))
    world.global_memory_index = max(0.2, min(1.0, world.global_memory_index - instability * 0.02))

    drift_note = (
        f"遮蔽度 {world.veil_density:.2f}；因果稳态 {world.causality_stability:.2f}；"
        f"集体记忆指数 {world.global_memory_index:.2f}"
    )
    world.drift_log.append(drift_note)
    events.append(
        Event(tick=tick, kind=EventKind.WORLD_DRIFT, payload={"summary": drift_note})
    )

    pool = world.crisis_pool or ["veil_thickening"]
    if rng.random() < 0.15 + instability * 0.2:
        crisis = rng.choice(pool)
        if crisis not in world.active_crises:
            world.active_crises.append(crisis)
            world.narrative_pressure = min(1.0, world.narrative_pressure + 0.2)
            events.append(
                Event(
                    tick=tick,
                    kind=EventKind.CRISIS,
                    payload={"crisis": crisis, "new": True},
                )
            )

    return events


def react_to_action(
    world: WorldState,
    agent: Agent,
    skill_key: str,
    success: bool,
    rng: random.Random,
) -> list[Event]:
    events: list[Event] = []
    tick = world.tick
    faction = world.factions.get(agent.state.faction_id)
    if not faction:
        return events

    if "deception" in skill_key:
        for fid, other in world.factions.items():
            if fid == agent.state.faction_id:
                continue
            drop = 0.12 if success else 0.05
            other.trust[agent.state.faction_id] = max(
                0.0, other.trust.get(agent.state.faction_id, 0.5) - drop
            )
            events.append(
                Event(
                    tick=tick,
                    kind=EventKind.TRUST_SHIFT,
                    payload={
                        "from_faction": agent.state.faction_id,
                        "from_faction_name": faction.name,
                        "to_faction": fid,
                        "to_faction_name": other.name,
                        "delta": -drop,
                        "reason": "deception_field",
                    },
                )
            )
        world.narrative_pressure = min(1.0, world.narrative_pressure + 0.15)

    if "memory" in skill_key or "archive" in skill_key:
        world.global_memory_index = max(
            0.15, world.global_memory_index - (0.08 if success else 0.03)
        )
        events.append(
            Event(
                tick=tick,
                kind=EventKind.MEMORY_FADE,
                payload={
                    "agent": agent.state.name,
                    "memory_index": world.global_memory_index,
                    "skill": skill_key,
                },
            )
        )

    if "beacon" in skill_key and success:
        world.veil_density = max(0.0, world.veil_density - 0.1)
        world.narrative_pressure = min(1.0, world.narrative_pressure + 0.1)

    if "relay" in skill_key:
        faction.pressure = min(1.0, faction.pressure + 0.08)
        world.narrative_pressure = min(1.0, world.narrative_pressure + 0.08)

    if success:
        faction.resources = min(1.0, faction.resources + 0.05)
    else:
        faction.resources = max(0.0, faction.resources - 0.04)
        faction.pressure = min(1.0, faction.pressure + 0.1)

    events.append(
        Event(
            tick=tick,
            kind=EventKind.WORLD_REACT,
            payload={
                "faction": faction.name,
                "faction_id": faction.id,
                "resources": round(faction.resources, 3),
                "pressure": round(faction.pressure, 3),
                "narrative_pressure": round(world.narrative_pressure, 3),
            },
        )
    )
    return events
